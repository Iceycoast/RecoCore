from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import get_db
from app.schemas import DataResponse
from app.schemas import TrendingItemResponse
from app.services import get_trending_recommendations

recommendation_router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)

@recommendation_router.get(
    "/trending",
    response_model=DataResponse[list[TrendingItemResponse]]
)
def fetch_trending_recommendations(
    db: Session = Depends(get_db),
    limit: int = 10
):
    trending_items = get_trending_recommendations(db=db, limit=limit)
    return DataResponse(
        success=True,
        message="Trending recommendations fetched successfully",
        data=trending_items
    )