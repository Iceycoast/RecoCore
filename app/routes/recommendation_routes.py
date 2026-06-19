from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import get_db
from app.schemas import DataResponse
from app.schemas import TrendingItemResponse, RecommendationResponse
from app.services import get_trending_recommendations, get_personalised_recommendations

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
    limit: int = 10,
    category: str |None = None
):
    trending_items = get_trending_recommendations(db=db, limit=limit, category=category)
    return DataResponse(
        success=True,
        message="Trending recommendations fetched successfully",
        data=trending_items
    )

@recommendation_router.get(
    "/users/{user_id}",
    response_model=list[RecommendationResponse]
)
def personalised_recommendations(
    user_id:int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    return get_personalised_recommendations(
        db=db,
        user_id=user_id,
        limit=limit
    )