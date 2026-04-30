"""
RSS scraper — 30+ Indian news sources.
Copyright note: we store and display only the headline + summary that publishers
explicitly include in their RSS feeds for syndication. We always link back to the
original article URL. This is standard RSS aggregation (Google News, Feedly, etc.)
and is compliant with each outlet's syndication intent.
"""
import re
import time
import hashlib
import concurrent.futures

import feedparser
import httpx

MAX_AGE_HOURS = 24
PER_FEED_LIMIT = 30
MAX_WORKERS = 22

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

RSS_SOURCES: dict[str, str] = {
    # ── National ──────────────────────────────────────────────────────
    "NDTV":              "https://feeds.feedburner.com/ndtvnews-india-news",
    "Times of India":    "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    "The Hindu":         "https://www.thehindu.com/news/national/feeder/default.rss",
    "Hindustan Times":   "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml",
    "India Today":       "https://www.indiatoday.in/rss/1206514",
    "DNA India":         "https://www.dnaindia.com/feeds/india.xml",
    # ── Business / Economy ────────────────────────────────────────────
    "Economic Times":    "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    "ET Markets":        "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "Livemint":          "https://www.livemint.com/rss/news",
    "Moneycontrol":      "https://www.moneycontrol.com/rss/latestnews.xml",
    "Financial Express": "https://www.financialexpress.com/feed/",
    "Business Standard": "https://www.business-standard.com/rss/home_page_top_stories.rss",
    # ── Sports ────────────────────────────────────────────────────────
    "ESPNCricinfo":      "https://www.espncricinfo.com/rss/content/story/feeds/0.xml",
    "NDTV Sports":       "https://feeds.feedburner.com/ndtvsports-cricket",
    # ── Entertainment ─────────────────────────────────────────────────
    "Bollywood Hungama": "https://www.bollywoodhungama.com/rss/news.xml",
    "Pinkvilla":         "https://www.pinkvilla.com/feed",
    "Filmfare":          "https://www.filmfare.com/rss.xml",
    # ── Cities ────────────────────────────────────────────────────────
    "NDTV Delhi":        "https://feeds.feedburner.com/ndtvnews-delhi-news",
    "TOI Delhi":         "https://timesofindia.indiatimes.com/rssfeeds/4418066.cms",
    "TOI Mumbai":        "https://timesofindia.indiatimes.com/rssfeeds/4419148.cms",
    "TOI Bangalore":     "https://timesofindia.indiatimes.com/rssfeeds/4418738.cms",
    "TOI Hyderabad":     "https://timesofindia.indiatimes.com/rssfeeds/7503091.cms",
    # ── Tech / Startup ────────────────────────────────────────────────
    "YourStory":         "https://yourstory.com/feed",
    "Inc42":             "https://inc42.com/feed/",
    # ── Hindi ─────────────────────────────────────────────────────────
    "Amar Ujala":        "https://www.amarujala.com/rss/breaking-news.xml",
    "Navbharat Times":   "https://navbharattimes.indiatimes.com/rssfeeds/0.cms",
    # ── Deccan / South ────────────────────────────────────────────────
    "Deccan Chronicle":  "https://www.deccanchronicle.com/rss_feed/",
    "The News Minute":   "https://www.thenewsminute.com/feed",
    # ── Digital / Independent ─────────────────────────────────────────
    "The Indian Express":"https://indianexpress.com/feed/",
    "Scroll.in":         "https://scroll.in/feed",
    "The Wire":          "https://thewire.in/rss",
    "The Print":         "https://theprint.in/feed/",
    "Firstpost":         "https://www.firstpost.com/rss/india.xml",
    "News18":            "https://www.news18.com/rss/india.xml",
    "Zee News":          "https://zeenews.india.com/rss/india-national-news.xml",
    "Republic World":    "https://www.republicworld.com/feeds/india-news.xml",
    "BusinessToday":     "https://www.businesstoday.in/rss/home.xml",
    "Outlook India":     "https://www.outlookindia.com/feed/news",
    "Tribune India":     "https://www.tribuneindia.com/rss/feed",
    "NDTV Profit":       "https://feeds.feedburner.com/NdtvProfit-BusinessNews",
    "Swarajya":          "https://swarajyamag.com/feed",
    # ── Sports extra ──────────────────────────────────────────────────
    "India Today Sports":"https://www.indiatoday.in/rss/1206577",
    "TOI Sports":        "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
    # ── Tech extra ────────────────────────────────────────────────────
    "TOI Tech":          "https://timesofindia.indiatimes.com/rssfeeds/66949542.cms",
    "ET Tech":           "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
    # ── Regional extra ────────────────────────────────────────────────
    "TOI Chennai":       "https://timesofindia.indiatimes.com/rssfeeds/7503221.cms",
    "Hindustan Hindi":   "https://www.livehindustan.com/rss/feed.xml",
}

_STRIP_HTML = re.compile(r"<[^>]+>")
_NOISE = re.compile(r"(advertisement|sponsored|subscribe|newsletter|follow us)", re.I)


def _strip(text: str) -> str:
    return _STRIP_HTML.sub(" ", text).strip()


def _url_hash(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _parse_ts(entry) -> float:
    pp = entry.get("published_parsed") or entry.get("updated_parsed")
    if pp:
        try:
            return time.mktime(pp)
        except Exception:
            pass
    return 0.0


def _time_ago(ts: float) -> str:
    delta = int(time.time() - ts)
    if delta < 3600:
        return f"{max(delta // 60, 1)}m ago"
    if delta < 86400:
        return f"{delta // 3600}h ago"
    return f"{delta // 86400}d ago"


def _fetch_one(source: str, url: str) -> list[dict]:
    now = time.time()
    cutoff = now - MAX_AGE_HOURS * 3600
    posts = []
    seen: set[str] = set()

    try:
        # Use httpx to follow redirects, then hand content to feedparser
        with httpx.Client(timeout=12, follow_redirects=True,
                          headers={"User-Agent": _UA}) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
            feed = feedparser.parse(resp.content)
    except Exception:
        return []

    for entry in feed.entries[:PER_FEED_LIMIT]:
        article_url = entry.get("link", "")
        if not article_url:
            continue

        ts = _parse_ts(entry)
        if ts and ts < cutoff:
            continue

        title = _strip(entry.get("title", "")).strip()
        if len(title) < 20 or _NOISE.search(title):
            continue

        summary = _strip(entry.get("summary", "") or entry.get("description", ""))[:400]
        text = f"{title}. {summary}".strip(". ")
        h = _url_hash(article_url)
        if h in seen:
            continue
        seen.add(h)

        posts.append({
            "source": source,
            "url": article_url,
            "url_hash": h,
            "text": text[:600],
            "upvotes": 0,
            "comments": 0,
            "time_ago": _time_ago(ts) if ts else "recent",
            "created_utc": ts if ts else now,
            "post_id": h,
        })

    return posts


def scrape_posts(limit: int = 500) -> list[dict]:
    all_posts: list[dict] = []
    seen: set[str] = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(_fetch_one, src, url): src for src, url in RSS_SOURCES.items()}
        for fut in concurrent.futures.as_completed(futures):
            for post in fut.result():
                h = post["url_hash"]
                if h not in seen:
                    seen.add(h)
                    all_posts.append(post)

    all_posts.sort(key=lambda p: p["created_utc"], reverse=True)
    return all_posts[:limit]
