from sqlalchemy import func, select, desc
from sqlalchemy.orm import Session

from app.models import Item
from app.models import Interaction


def get_trending_items(db: Session, limit: int = 10):

    query = (
        select(
            Item,
            func.sum(Interaction.weight).label("score")
        )
        .join(Interaction, Item.item_id == Interaction.item_id)
        .group_by(Item.item_id)
        .order_by(desc("score"))
        .limit(limit)   
    )

    results = db.execute(query).all()

    trending_items = []

    for item, score in results:
        trending_items.append({
            "item_id" : item.item_id,
            "name" : item.name,
            "category" : item.category,
            "score" : score
        })

    return trending_items