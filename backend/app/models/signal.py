from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class FactCheck(BaseModel):
    verdict: Literal["organic", "coordinated"]
    confidence: float
    bot_risk: float
    account_diversity: float
    language_mix: float
    spread_pattern: float


class Breakdown(BaseModel):
    aspect: str
    score: int


class Entity(BaseModel):
    name: str
    type: str
    score: int


class Post(BaseModel):
    source: str
    url: str = ""          # direct link to original article
    text: str
    sentiment: Literal["neg", "pos", "neu"]
    score: int
    upvotes: int
    comments: int
    time_ago: str


class Signal(BaseModel):
    id: Optional[str] = None
    topic: str
    summary: str
    sentiment: Literal["neg", "pos", "neu"]
    score: int = Field(ge=-100, le=100)
    region: str
    signal_type: Literal["spike", "sustained", "trending"]
    post_count: int
    duration_hours: int
    spike_rate: float
    fact_check: FactCheck
    breakdown: list[Breakdown]
    entities: list[Entity]
    trend: list[int]
    posts: list[Post]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SignalListItem(BaseModel):
    id: Optional[str] = None
    topic: str
    sentiment: Literal["neg", "pos", "neu"]
    score: int
    region: str
    signal_type: Literal["spike", "sustained", "trending"]
    post_count: int
    created_at: datetime
