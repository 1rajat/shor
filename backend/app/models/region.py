from pydantic import BaseModel


class RegionSummary(BaseModel):
    region: str
    intensity: int
    signal_count: int
    dominant_sentiment: str
