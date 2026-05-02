import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.mongo import connect, disconnect, get_signals_col, is_already_processed, mark_processed
from app.api.routes.signals import router as signals_router
from app.api.routes.entities import router as entities_router
from app.api.routes.regions import router as regions_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("groq").setLevel(logging.WARNING)
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
        BATCH = 50
        logger.info("Refresh started — scraping RSS feeds")
        raw_posts = await _asyncio.to_thread(scrape_posts, 200)
        logger.info("Scraped %d raw articles from feeds", len(raw_posts))

        new_posts = []
        for p in raw_posts:
            if not await is_already_processed(p.get("url_hash", "")):
                new_posts.append(p)
            if len(new_posts) >= BATCH:
                break

        if not new_posts:
            logger.info("No new articles (all already processed)")
            refresh_state["last_refresh"] = datetime.now(timezone.utc).isoformat()
            return {"status": "ok", "new_articles": 0, "signals_created": 0}

        logger.info("Classifying %d new articles via LLM", len(new_posts))
        classified = []
        for i, post in enumerate(new_posts, 1):
            result = await classify_post(post["text"])
            classified.append({**post, **result})
            if i % 10 == 0:
                logger.info("  classified %d/%d  last: %s → %s %+d",
                            i, len(new_posts),
                            post.get("source", "?"),
                            result.get("sentiment", "?"),
                            result.get("score", 0))

        signals = detect_signals(list(classified))
        logger.info("Detected %d topic signals", len(signals))

        saved = 0
        for sig in signals:
            fc = check_signal(sig.get("posts", []))
            sig["fact_check"] = fc
            await upsert_signal(sig)
            saved += 1
            logger.info("  saved signal: %-15s  score=%+d  posts=%d  type=%s",
                        sig.get("topic","?"), sig.get("score",0),
                        sig.get("post_count",0), sig.get("signal_type","?"))

        await mark_processed([p["url_hash"] for p in new_posts if p.get("url_hash")])

        refresh_state["last_refresh"] = datetime.now(timezone.utc).isoformat()
        refresh_state["last_signals_created"] = saved
        refresh_state["last_articles_fetched"] = len(new_posts)

        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        pruned = await get_signals_col().delete_many({"updated_at": {"$lt": cutoff}})
        if pruned.deleted_count:
            logger.info("Pruned %d signals older than 24h", pruned.deleted_count)

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
