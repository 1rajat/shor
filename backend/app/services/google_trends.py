# Google Trends RSS endpoint (geo=IN) was deprecated and returns 404.
# This module is a stub — the pipeline continues without it.
# To re-enable: replace with a headless browser scrape or SerpAPI.

def get_trending_topics(limit: int = 20) -> list[dict]:
    return []


def get_interest_over_time(keyword: str) -> list[int]:
    return [50] * 24
