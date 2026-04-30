import time
from collections import Counter


def check_signal(posts: list[dict]) -> dict:
    if not posts:
        return _default_organic()

    sources = [p.get("source", "") for p in posts]
    source_diversity = len(set(sources)) / max(len(sources), 1)

    texts = [p.get("text", "") for p in posts]
    text_counter = Counter(texts)
    repetition_rate = text_counter.most_common(1)[0][1] / max(len(texts), 1)
    language_mix = _detect_language_mix(texts)

    now = time.time()
    timestamps = [p.get("created_utc", now) for p in posts]
    spread_pattern = _analyze_spread(timestamps)

    bot_risk = min(1.0, (repetition_rate * 0.5) + ((1 - source_diversity) * 0.3) + ((1 - spread_pattern) * 0.2))
    account_diversity = round(source_diversity, 2)

    verdict: str
    confidence: float
    if bot_risk > 0.6:
        verdict = "coordinated"
        confidence = round(bot_risk, 2)
    else:
        verdict = "organic"
        confidence = round(1 - bot_risk, 2)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "bot_risk": round(bot_risk, 2),
        "account_diversity": account_diversity,
        "language_mix": round(language_mix, 2),
        "spread_pattern": round(spread_pattern, 2),
    }


def _detect_language_mix(texts: list[str]) -> float:
    hindi_chars = set("अआइईउऊएओकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसहाि")
    mixed = sum(1 for t in texts if any(c in hindi_chars for c in t))
    return round(mixed / max(len(texts), 1), 2)


def _analyze_spread(timestamps: list[float]) -> float:
    if len(timestamps) < 2:
        return 1.0
    sorted_ts = sorted(timestamps)
    gaps = [sorted_ts[i + 1] - sorted_ts[i] for i in range(len(sorted_ts) - 1)]
    avg_gap = sum(gaps) / len(gaps)
    # organic posts have varied gaps; very uniform gaps suggest automation
    variance = sum((g - avg_gap) ** 2 for g in gaps) / len(gaps)
    normalised_variance = min(1.0, variance / (avg_gap ** 2 + 1))
    return round(normalised_variance, 2)


def _default_organic() -> dict:
    return {
        "verdict": "organic",
        "confidence": 0.8,
        "bot_risk": 0.1,
        "account_diversity": 0.9,
        "language_mix": 0.4,
        "spread_pattern": 0.7,
    }
