import pytest
from app.services.signal_detector import detect_signals, _detect_topic, _detect_region


def test_detect_topic_cricket():
    assert _detect_topic("IPL match was incredible, Dhoni hit a six") == "Cricket / IPL"


def test_detect_topic_petrol():
    assert _detect_topic("Petrol prices are through the roof this month") == "Petrol Prices"


def test_detect_topic_unknown():
    assert _detect_topic("random unrelated text") == "General"


def test_detect_region_delhi():
    assert _detect_region("r/delhi", "") == "Delhi"


def test_detect_signals_groups_by_topic():
    posts = [
        {"text": "Cricket match was great", "source": "r/cricket", "sentiment": "pos", "score": 80,
         "upvotes": 100, "comments": 10, "time_ago": "1h ago", "created_utc": 1700000000},
        {"text": "IPL was amazing today", "source": "r/IPL", "sentiment": "pos", "score": 75,
         "upvotes": 200, "comments": 20, "time_ago": "2h ago", "created_utc": 1700000000},
    ]
    results = detect_signals(posts)
    assert len(results) >= 1
    topics = [r["topic"] for r in results]
    assert "Cricket / IPL" in topics


def test_detect_signals_returns_required_fields():
    posts = [
        {"text": "Petrol price is too high", "source": "r/india", "sentiment": "neg", "score": -70,
         "upvotes": 500, "comments": 50, "time_ago": "3h ago", "created_utc": 1700000000},
        {"text": "Fuel prices are killing us", "source": "r/india", "sentiment": "neg", "score": -65,
         "upvotes": 300, "comments": 30, "time_ago": "4h ago", "created_utc": 1700000000},
    ]
    results = detect_signals(posts)
    assert results
    s = results[0]
    for field in ("topic", "summary", "sentiment", "score", "region", "signal_type",
                  "post_count", "duration_hours", "spike_rate", "trend", "breakdown", "entities", "posts"):
        assert field in s, f"Missing field: {field}"
