from pydantic import BaseModel

class TrendingItemResponse(BaseModel):
    item_id: int
    name: str
    category: str
    score: int
    