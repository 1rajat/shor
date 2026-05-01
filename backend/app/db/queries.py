import time
from typing import Optional
from bson import ObjectId
from app.db.mongo import get_signals_col


def _format_ts(ts: float) -> str:
    from datetime import datetime, timezone, timedelta
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    ist = dt + timedelta(hours=5, minutes=30)
    day = ist.day
    month = ist.strftime("%b")
    hour = ist.hour % 12 or 12
    minute = f"{ist.minute:02d}"
    period = "am" if ist.hour < 12 else "pm"
    return f"{day} {month}, {hour}:{minute} {period}"


def _serialize(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    for post in doc.get("posts", []):
        ts = post.get("created_utc", 0)
        if ts:
            post["time_ago"] = _format_ts(ts)
    return doc


async def get_all_signals(
    sentiment_filter: Optional[str] = None,
    region_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
) -> list[dict]:
    col = get_signals_col()
    query: dict = {}
    if sentiment_filter and sentiment_filter in ("neg", "pos", "neu"):
        query["sentiment"] = sentiment_filter
    if region_filter:
        query["region"] = region_filter
    if type_filter and type_filter in ("spike", "sustained", "trending"):
        query["signal_type"] = type_filter

    cursor = col.find(query).sort("created_at", -1).skip(skip).limit(limit)
    return [_serialize(doc) async for doc in cursor]


async def get_signal_by_id(signal_id: str) -> Optional[dict]:
    col = get_signals_col()
    try:
        doc = await col.find_one({"_id": ObjectId(signal_id)})
    except Exception:
        doc = await col.find_one({"id": signal_id})
    return _serialize(doc) if doc else None


async def upsert_signal(signal_dict: dict) -> str:
    col = get_signals_col()
    signal_dict = signal_dict.copy()
    signal_dict.pop("id", None)
    topic = signal_dict.get("topic")
    if topic:
        result = await col.replace_one({"topic": topic}, signal_dict, upsert=True)
        return str(result.upserted_id) if result.upserted_id else topic
    result = await col.insert_one(signal_dict)
    return str(result.inserted_id)
