import time
import praw
from app.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

SUBREDDITS = [
    "india", "delhi", "mumbai", "bangalore", "hyderabad", "pune",
    "indianews", "unitedstatesofindia", "indiaspeaks", "bollywood",
    "cricket", "IPL", "IndianStockMarket",
]

_reddit: praw.Reddit = None


def _get_reddit() -> praw.Reddit:
    global _reddit
    if _reddit is None:
        _reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
            read_only=True,
        )
    return _reddit


def _time_ago(created_utc: float) -> str:
    delta = int(time.time() - created_utc)
    if delta < 3600:
        return f"{delta // 60}m ago"
    if delta < 86400:
        return f"{delta // 3600}h ago"
    return f"{delta // 86400}d ago"


def scrape_posts(limit: int = 100) -> list[dict]:
    reddit = _get_reddit()
    posts = []
    per_sub = max(1, limit // len(SUBREDDITS))

    for sub_name in SUBREDDITS:
        try:
            sub = reddit.subreddit(sub_name)
            for post in sub.hot(limit=per_sub):
                if not post.selftext and not post.title:
                    continue
                text = f"{post.title}\n{post.selftext}".strip()
                posts.append({
                    "source": f"r/{sub_name}",
                    "text": text,
                    "upvotes": post.score,
                    "comments": post.num_comments,
                    "time_ago": _time_ago(post.created_utc),
                    "created_utc": post.created_utc,
                    "subreddit": sub_name,
                    "post_id": post.id,
                })
        except Exception:
            continue

    return posts
