import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.sentiment import classify_post, _extract_json


def test_extract_json_clean():
    raw = '{"sentiment": "neg", "score": -75, "reason": "very angry post"}'
    result = _extract_json(raw)
    assert result["sentiment"] == "neg"
    assert result["score"] == -75


def test_extract_json_with_surrounding_text():
    raw = 'Here is the result: {"sentiment": "pos", "score": 60, "reason": "happy"} done.'
    result = _extract_json(raw)
    assert result["sentiment"] == "pos"


def test_extract_json_no_json_raises():
    with pytest.raises(ValueError):
        _extract_json("no json here at all")


@pytest.mark.asyncio
async def test_classify_post_returns_fallback_on_error():
    with patch("app.services.sentiment.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(side_effect=Exception("connection refused"))
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
        result = await classify_post("some text")
    assert result["sentiment"] in ("neg", "pos", "neu")
    assert -100 <= result["score"] <= 100
