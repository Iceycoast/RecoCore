from sqlalchemy.orm import Session

from app.ranking_engine.trending import get_trending_items
from app.ranking_engine.personalised import build_personalized_recommendations
from app.schemas.recommendation_schema import RecommendationResponse

def get_trending_recommendations(db:Session, limit: int = 10, category: str | None = None):
    return get_trending_items(db=db, limit=limit, category=category)


def get_personalised_recommendations(
        db: Session,
        user_id: int,
        limit: int = 10,
) -> list[RecommendationResponse]:
    
    items = build_personalized_recommendations(
        db=db,
        user_id=user_id,
        limit=limit,
    )

    return [
        RecommendationResponse(
            item_id=item.item_id,
            name=item.name,
            category=item.category,
        )
        for item in items
    ]