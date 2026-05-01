from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from app.config import MONGO_URI, MONGO_DB

client: AsyncIOMotorClient = None


def get_db():
    return client[MONGO_DB]


def get_signals_col() -> AsyncIOMotorCollection:
    return get_db()["signals"]


def get_processed_col() -> AsyncIOMotorCollection:
    """Tracks processed article URLs for cross-refresh deduplication (TTL: 48h)."""
    return get_db()["processed_articles"]


async def ensure_indexes():
    signals = get_signals_col()
    await signals.create_index([("created_at", -1)])
    await signals.create_index([("sentiment", 1), ("created_at", -1)])
    await signals.create_index([("region", 1), ("created_at", -1)])
    await signals.create_index([("topic", 1), ("created_at", -1)])
    await signals.create_index([("signal_type", 1)])

    proc = get_processed_col()
    await proc.create_index([("url_hash", 1)], unique=True)
    # TTL index: auto-delete after 12h so articles re-cycle within the same day
    # Drop old index if it exists with a different TTL before recreating
    try:
        await proc.drop_index("processed_at_1")
    except Exception:
        pass
    await proc.create_index(
        [("processed_at", 1)],
        expireAfterSeconds=12 * 3600,
        name="processed_at_1",
    )


async def connect():
    global client
    client = AsyncIOMotorClient(MONGO_URI)
    await client.admin.command("ping")
    await ensure_indexes()


async def disconnect():
    global client
    if client:
        client.close()


async def is_already_processed(url_hash: str) -> bool:
    proc = get_processed_col()
    return bool(await proc.find_one({"url_hash": url_hash}))


async def mark_processed(url_hashes: list[str]):
    if not url_hashes:
        return
    from datetime import datetime, timezone
    proc = get_processed_col()
    now = datetime.now(timezone.utc)
    docs = [{"url_hash": h, "processed_at": now} for h in url_hashes]
    try:
        await proc.insert_many(docs, ordered=False)
    except Exception:
        pass  # duplicate key errors are expected and fine
