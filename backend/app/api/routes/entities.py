import time
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter
from app.db.mongo import get_signals_col


def _format_ts(ts: float) -> str:
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    ist = dt + timedelta(hours=5, minutes=30)
    hour = ist.hour % 12 or 12
    minute = f"{ist.minute:02d}"
    period = "am" if ist.hour < 12 else "pm"
    return f"{ist.day} {ist.strftime('%b')}, {hour}:{minute} {period}"

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("")
async def get_entities():
    col = get_signals_col()
    entity_map: dict[str, dict] = {}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

    async for signal in col.find({"updated_at": {"$gte": cutoff}}, {"entities": 1}):
        for ent in signal.get("entities", []):
            name = ent.get("name", "")
            if not name:
                continue
            if name not in entity_map:
                entity_map[name] = {
                    "name": name,
                    "type": ent.get("type", "unknown"),
                    "score": ent.get("score", 0),
                    "mention_count": 1,
                }
            else:
                entity_map[name]["mention_count"] += 1
                entity_map[name]["score"] = int(
                    (entity_map[name]["score"] + ent.get("score", 0)) / 2
                )

    return sorted(entity_map.values(), key=lambda x: x["mention_count"], reverse=True)[:20]


@router.get("/{entity_name}")
async def get_entity_detail(entity_name: str):
    col = get_signals_col()
    topics_found = []
    all_articles = []
    scores = []

    name_lower = entity_name.lower()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    async for signal in col.find({"updated_at": {"$gte": cutoff}}):
        # Match via entities list OR by scanning post text
        entity_score = None
        for ent in signal.get("entities", []):
            if ent.get("name", "").lower() == name_lower:
                entity_score = ent.get("score", 0)
                break

        # Collect matching posts regardless of entity list
        matched_posts = [
            p for p in signal.get("posts", [])
            if name_lower in p.get("text", "").lower()
        ]

        if entity_score is not None or matched_posts:
            score = entity_score if entity_score is not None else (
                int(sum(p.get("score", 0) for p in matched_posts) / len(matched_posts))
                if matched_posts else 0
            )
            scores.append(score)
            topics_found.append({
                "topic": signal.get("topic", ""),
                "score": score,
                "signal_id": str(signal.get("_id", "")),
            })
            for post in matched_posts:
                p = {**post, "topic": signal.get("topic", "")}
                ts = p.get("created_utc", 0)
                if ts:
                    p["time_ago"] = _format_ts(ts)
                all_articles.append(p)

    avg_score = int(sum(scores) / len(scores)) if scores else 0

    return {
        "name": entity_name,
        "score": avg_score,
        "mention_count": len(scores),
        "topics": topics_found,
        "articles": all_articles[:12],
    }
