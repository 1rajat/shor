from fastapi import APIRouter
from app.db.mongo import get_signals_col

router = APIRouter(prefix="/api/entities", tags=["entities"])


@router.get("")
async def get_entities():
    col = get_signals_col()
    entity_map: dict[str, dict] = {}

    async for signal in col.find({}, {"entities": 1}):
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

    async for signal in col.find({}):
        for ent in signal.get("entities", []):
            if ent.get("name", "").lower() == entity_name.lower():
                score = ent.get("score", 0)
                scores.append(score)
                topics_found.append({
                    "topic": signal.get("topic", ""),
                    "score": score,
                    "signal_id": str(signal.get("_id", "")),
                })
                # Collect posts from this signal that mention the entity
                name_lower = entity_name.lower()
                for post in signal.get("posts", []):
                    if name_lower in post.get("text", "").lower():
                        all_articles.append({
                            **post,
                            "topic": signal.get("topic", ""),
                        })
                break

    avg_score = int(sum(scores) / len(scores)) if scores else 0

    return {
        "name": entity_name,
        "score": avg_score,
        "mention_count": len(scores),
        "topics": topics_found,
        "articles": all_articles[:12],
    }
