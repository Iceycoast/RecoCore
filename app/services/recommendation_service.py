from sqlalchemy.orm import Session

from app.ranking_engine import get_trending_items

def get_trending_recommendations(db:Session, limit: int = 10):
    return get_trending_items(db=db, limit=limit)