from collections import defaultdict
from fastapi import APIRouter
from app.db.mongo import get_signals_col

router = APIRouter(prefix="/api/regions", tags=["regions"])


@router.get("")
async def get_regions():
    col = get_signals_col()
    region_data: dict[str, dict] = defaultdict(
        lambda: {"signal_count": 0, "scores": [], "sentiments": []}
    )

    async for signal in col.find({}, {"region": 1, "score": 1, "sentiment": 1}):
        r = signal.get("region", "National")
        region_data[r]["signal_count"] += 1
        region_data[r]["scores"].append(signal.get("score", 0))
        region_data[r]["sentiments"].append(signal.get("sentiment", "neu"))

    result = []
    for region, data in region_data.items():
        scores = data["scores"]
        avg_score = int(sum(scores) / len(scores)) if scores else 0
        intensity = min(100, abs(avg_score))
        sentiments = data["sentiments"]
        dominant = max(set(sentiments), key=sentiments.count)
        result.append({
            "region": region,
            "intensity": intensity,
            "signal_count": data["signal_count"],
            "dominant_sentiment": dominant,
        })

    return sorted(result, key=lambda x: x["intensity"], reverse=True)
