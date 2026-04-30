import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mongo import connect, disconnect, get_signals_col, is_already_processed, mark_processed
from app.api.routes.signals import router as signals_router
from app.api.routes.entities import router as entities_router
from app.api.routes.regions import router as regions_router

logger = logging.getLogger("shor")

REFRESH_INTERVAL_SECONDS = 5 * 60  # 5 minutes

# Shared state — readable by /api/status
refresh_state = {
    "last_refresh": None,
    "last_signals_created": 0,
    "last_articles_fetched": 0,
    "running": False,
}


async def run_refresh() -> dict:
    """Core pipeline: scrape → classify → detect → save. Called by route and background task."""
    import asyncio as _asyncio
    from app.services.news_rss import scrape_posts
    from app.services.sentiment import classify_post
    from app.services.signal_detector import detect_signals
    from app.services.fact_checker import check_signal
    from app.db.queries import upsert_signal

    if refresh_state["running"]:
        return {"status": "already_running"}

    refresh_state["running"] = True
    try:
        # Fetch newest articles; dedup skips anything already classified
        BATCH = 60  # llama3.2:3b ~5s each → 60 × 5s ≈ 5 min per cycle
        raw_posts = await _asyncio.to_thread(scrape_posts, 200)

        new_posts = []
        for p in raw_posts:
            if not await is_already_processed(p.get("url_hash", "")):
                new_posts.append(p)
            if len(new_posts) >= BATCH:
                break

        if not new_posts:
            refresh_state["last_refresh"] = datetime.now(timezone.utc).isoformat()
            return {"status": "ok", "new_articles": 0, "signals_created": 0}

        # Ollama is serial internally — no point exceeding 1 concurrent call
        classified = []
        for post in new_posts:
            result = await classify_post(post["text"])
            classified.append({**post, **result})

        signals = detect_signals(list(classified))

        saved = 0
        for sig in signals:
            fc = check_signal(sig.get("posts", []))
            sig["fact_check"] = fc
            await upsert_signal(sig)
            saved += 1

        # Mark all processed
        await mark_processed([p["url_hash"] for p in new_posts if p.get("url_hash")])

        refresh_state["last_refresh"] = datetime.now(timezone.utc).isoformat()
        refresh_state["last_signals_created"] = saved
        refresh_state["last_articles_fetched"] = len(new_posts)
        return {
            "status": "ok",
            "new_articles": len(new_posts),
            "signals_created": saved,
        }
    finally:
        refresh_state["running"] = False


async def _background_loop():
    """Refresh immediately on startup, then every REFRESH_INTERVAL_SECONDS."""
    # First run: give the server 2 seconds to finish binding, then go
    await asyncio.sleep(2)
    while True:
        try:
            result = await run_refresh()
            logger.info("Auto-refresh: %s", result)
        except Exception as exc:
            logger.error("Auto-refresh failed: %s", exc)
        await asyncio.sleep(REFRESH_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    task = asyncio.create_task(_background_loop())
    yield
    task.cancel()
    await disconnect()


app = FastAPI(title="Shor API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signals_router)
app.include_router(entities_router)
app.include_router(regions_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "shor"}


@app.get("/api/status")
async def status():
    col = get_signals_col()
    total = await col.count_documents({})
    return {
        "total_signals": total,
        "last_refresh": refresh_state["last_refresh"],
        "last_articles_fetched": refresh_state["last_articles_fetched"],
        "last_signals_created": refresh_state["last_signals_created"],
        "refresh_running": refresh_state["running"],
        "refresh_interval_minutes": REFRESH_INTERVAL_SECONDS // 60,
    }
