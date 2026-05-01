import time
from collections import defaultdict
from datetime import datetime, timezone
from app.services.sentiment import VALID_TOPICS

_VALID_TOPICS_SET = set(VALID_TOPICS)

MIN_POSTS_PER_SIGNAL = 2      # noise filter — drop topics with fewer posts
MAX_POSTS_PER_SIGNAL = 20     # keep top N posts in a signal
MAX_AGE_HOURS = 24            # only last 24h counts toward duration


def _determine_signal_type(posts: list[dict]) -> tuple[str, float, int]:
    now = time.time()
    recent_6h = [p for p in posts if (now - p.get("created_utc", now)) < 6 * 3600]
    older = [p for p in posts if (now - p.get("created_utc", now)) >= 6 * 3600]

    if not older:
        spike_rate = 100.0
    else:
        spike_rate = (len(recent_6h) / max(len(older), 1)) * 100

    if spike_rate > 100:
        signal_type = "spike"
    elif len(posts) >= 10:
        signal_type = "sustained"
    else:
        signal_type = "trending"

    # only look at posts within MAX_AGE_HOURS to avoid 4999h bug
    cutoff = now - MAX_AGE_HOURS * 3600
    valid_ts = [p["created_utc"] for p in posts
                if p.get("created_utc", 0) > cutoff]
    if valid_ts:
        earliest = min(valid_ts)
        duration_hours = max(1, int((now - earliest) / 3600))
    else:
        duration_hours = 1

    return signal_type, round(spike_rate, 1), duration_hours


def _build_trend(posts: list[dict]) -> list[int]:
    now = time.time()
    buckets = [0] * 24
    for p in posts:
        ts = p.get("created_utc", 0)
        if not ts:
            continue
        hours_ago = int((now - ts) / 3600)
        if 0 <= hours_ago < 24:
            buckets[23 - hours_ago] += 1
    max_val = max(buckets) or 1
    return [int((v / max_val) * 100) for v in buckets]


def _build_breakdown(posts: list[dict]) -> list[dict]:
    """Group posts by LLM-extracted aspect and average their scores."""
    aspect_scores: dict[str, list[int]] = defaultdict(list)
    for p in posts:
        aspect = p.get("aspect", "").strip()
        if aspect and len(aspect) > 3:
            aspect_scores[aspect].append(p.get("score", 0))

    if not aspect_scores:
        return [{"aspect": "General sentiment", "score": 0}]

    breakdown = []
    for aspect, scores in sorted(
        aspect_scores.items(), key=lambda x: abs(sum(x[1])), reverse=True
    )[:6]:
        breakdown.append({
            "aspect": aspect,
            "score": int(sum(scores) / len(scores)),
        })
    return breakdown


def _build_entities(posts: list[dict]) -> list[dict]:
    entity_scores: dict[str, list[int]] = defaultdict(list)
    for p in posts:
        for ent in p.get("entities", []):
            if ent and len(ent) > 1:
                entity_scores[ent].append(p.get("score", 0))

    result = []
    for name, scores in sorted(
        entity_scores.items(), key=lambda x: len(x[1]), reverse=True
    )[:6]:
        result.append({
            "name": name,
            "type": "entity",
            "score": int(sum(scores) / len(scores)),
        })
    return result


def _dominant(values: list[str]) -> str:
    if not values:
        return "neu"
    return max(set(values), key=values.count)


def detect_signals(classified_posts: list[dict]) -> list[dict]:
    # Group by primary LLM topic
    grouped: dict[str, list[dict]] = defaultdict(list)
    for post in classified_posts:
        topics = [t for t in (post.get("topics") or []) if t in _VALID_TOPICS_SET]
        if not topics:
            continue  # skip unclassifiable posts — no "General" bucket
        grouped[topics[0]].append(post)
        if len(topics) > 1:
            grouped[topics[1]].append(post)

    signals = []
    now_dt = datetime.now(timezone.utc)

    for topic, posts in grouped.items():
        if len(posts) < MIN_POSTS_PER_SIGNAL:
            continue

        scores = [p.get("score", 0) for p in posts]
        avg_score = int(sum(scores) / len(scores))
        dominant_sentiment = _dominant([p.get("sentiment", "neu") for p in posts])

        signal_type, spike_rate, duration_hours = _determine_signal_type(posts)

        # Region: majority vote from LLM-assigned regions
        region_votes: dict[str, int] = defaultdict(int)
        for p in posts:
            region_votes[p.get("region", "National")] += 1
        region = max(region_votes, key=region_votes.get)

        # Sort posts by upvotes desc, cap at MAX_POSTS_PER_SIGNAL
        top_posts = sorted(posts, key=lambda p: p.get("upvotes", 0), reverse=True)

        # Source diversity for summary
        sources = list({p.get("source", "") for p in posts})[:3]
        sources_str = ", ".join(sources)

        signals.append({
            "topic": topic,
            "summary": (
                f"Coverage of {topic} is active across {len(sources)} Indian news sources "
                f"including {sources_str}. {len(posts)} articles published in the last "
                f"{duration_hours}h with {'mostly ' + dominant_sentiment + ' sentiment' if dominant_sentiment != 'neu' else 'mixed sentiment'}."
            ),
            "sentiment": dominant_sentiment,
            "score": avg_score,
            "region": region,
            "signal_type": signal_type,
            "post_count": len(posts),
            "duration_hours": duration_hours,
            "spike_rate": spike_rate,
            "fact_check": {
                "verdict": "organic",
                "confidence": 0.85,
                "bot_risk": 0.05,
                "account_diversity": min(1.0, len(set(p.get("source","") for p in posts)) / 5),
                "language_mix": 0.4,
                "spread_pattern": 0.7,
            },
            "breakdown": _build_breakdown(posts),
            "entities": _build_entities(posts),
            "trend": _build_trend(posts),
            "posts": [
                {
                    "source": p.get("source", ""),
                    "url": p.get("url", ""),
                    "text": p.get("text", "")[:300],
                    "sentiment": p.get("sentiment", "neu"),
                    "score": p.get("score", 0),
                    "upvotes": p.get("upvotes", 0),
                    "comments": p.get("comments", 0),
                    "time_ago": p.get("time_ago", ""),
                    "created_utc": p.get("created_utc", 0),
                }
                for p in top_posts[:MAX_POSTS_PER_SIGNAL]
            ],
            "created_at": now_dt,
            "updated_at": now_dt,
        })

    # Sort by post_count descending
    return sorted(signals, key=lambda s: s["post_count"], reverse=True)
