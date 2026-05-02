import json
import logging
import re
from groq import AsyncGroq
from app.config import GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger("shor.sentiment")

VALID_TOPICS = [
    "Politics", "Cricket", "Economy", "Stock Market", "Weather",
    "Education", "Petrol Prices", "Electricity", "Transport",
    "Unemployment", "Budget", "Railways", "Bollywood", "Technology",
    "Crime", "Health", "Agriculture", "Defence", "Business", "Environment",
]

PROMPT_TEMPLATE = """Classify this Indian news article. Output ONLY a JSON object, nothing else.

Rules:
- sentiment: "neg" if bad news/criticism/loss, "pos" if good news/achievement/growth, "neu" if factual/neutral
- score: -100 (very negative) to +100 (very positive), 0 only if truly neutral. Use the full range.
- aspect: 3-5 word phrase naming the specific issue (e.g. "fuel price hike", "GDP growth surge")
- topics: pick 1-2 from the valid list below
- region: most relevant city, or "National"
- entities: up to 3 key people or organisations mentioned

Valid topics: {topics}

Article: {text}

JSON:"""

_FALLBACK = {
    "sentiment": "neu",
    "score": 0,
    "aspect": "general news",
    "topics": ["General"],
    "region": "National",
    "entities": [],
}


def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found")


_VALID_TOPICS_SET = set(VALID_TOPICS)
# Client is None when API key is not configured — classify_post returns fallback
_client = AsyncGroq(api_key=GROQ_API_KEY) if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here" else None


def _normalise(result: dict) -> dict:
    sentiment = result.get("sentiment", "neu")
    if sentiment not in ("neg", "pos", "neu"):
        sentiment = "neu"

    score = int(result.get("score", 0))
    score = max(-100, min(100, score))

    raw_topics = result.get("topics", [])
    if not isinstance(raw_topics, list):
        raw_topics = []
    topics = [t for t in raw_topics if isinstance(t, str) and t in _VALID_TOPICS_SET][:2]
    if not topics:
        topics = []  # empty = unclassifiable, will be skipped by detector

    region = result.get("region", "National")
    if region not in ("Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "National"):
        region = "National"

    entities = result.get("entities", [])
    if not isinstance(entities, list):
        entities = []
    entities = [e for e in entities if isinstance(e, str)][:5]

    aspect = str(result.get("aspect", "general news"))[:60]

    return {
        "sentiment": sentiment,
        "score": score,
        "aspect": aspect,
        "topics": topics,
        "region": region,
        "entities": entities,
    }


async def classify_post(text: str) -> dict:
    if _client is None:
        logger.warning("GROQ_API_KEY not set — add it to .env to enable LLM classification")
        return _FALLBACK.copy()
    prompt = PROMPT_TEMPLATE.format(
        topics=", ".join(VALID_TOPICS),
        text=text[:800],
    )
    try:
        response = await _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.05,
            max_tokens=256,
        )
        raw = response.choices[0].message.content or ""
        return _normalise(_extract_json(raw))
    except Exception as exc:
        logger.debug("classify_post failed: %s", exc)
        return _FALLBACK.copy()
