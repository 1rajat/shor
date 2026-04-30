from pydantic import BaseModel


class EntitySummary(BaseModel):
    name: str
    type: str
    score: int
    mention_count: int = 0
