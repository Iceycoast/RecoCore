from sqlalchemy import select, func, desc
from sqlalchemy.orm import Session

from app.models import Interaction, Item
from app.ranking_engine.scoring import calculate_effective_weight

def get_category_affinity(db: Session, user_id: int) -> dict[str, float]:

    query = (
        select(
            Item.category,
            Interaction.weight,
            Interaction.created_at,
        )
        .join(Item, Item.item_id == Interaction.item_id)
        .where(Interaction.user_id == user_id)
    )
    
    results = db.execute(query).all()

    affinity_scores: dict[str, float] = {}

    for category, weight, created_at in results:
        effective_weight = calculate_effective_weight(weight=weight, interaction_date=created_at)

        affinity_scores[category] = (affinity_scores.get(category,0) + effective_weight)

    return affinity_scores


def get_top_categories(affinity_scores: dict[str, float],) -> tuple[str| None, str| None]:
    
    if not affinity_scores:
        return None, None
    
    sorted_categories = sorted(affinity_scores.items(),
                               key = lambda item: item[1],
                               reverse= True,)
    primary_category = sorted_categories[0][0]

    secondary_category = (sorted_categories[1][0]
                          if len(sorted_categories) > 1
                          else None)
    return primary_category, secondary_category


def get_excluded_item_ids(db: Session, user_id: int) -> set[int]:

    query = (
        select(Interaction.item_id)
        .where(Interaction.user_id == user_id,
               Interaction.action_type.in_(
                   ["like",
                    "share",
                    "purchase"]
               )
        )
    )

    results = db.execute(query).scalars().all()
    return set(results)


def get_category_recommendations(
    db: Session,
    category: str,
    excluded_item_ids: set[int],
    limit: int,
) -> list[Item]:

    query = (
        select(Item)
        .where(
            Item.category == category
        )
    )

    if excluded_item_ids:
        query = query.where(
            Item.item_id.not_in(
                excluded_item_ids
            )
        )

    query = query.limit(limit)

    items = list(
        db.execute(query)
        .scalars()
        .all()
    )

    return items


def get_trending_candidate_items(
    db: Session,
    excluded_item_ids: set[int],
    limit: int,
) -> list[Item]:

    query = (
        select(Item)
        .join(
            Interaction,
            Item.item_id == Interaction.item_id,
        )
    )

    if excluded_item_ids:
        query = query.where(
            Item.item_id.not_in(
                excluded_item_ids
            )
        )

    query = (
        query
        .group_by(Item.item_id)
        .order_by(
            desc(
                func.sum(
                    Interaction.weight
                )
            )
        )
        .limit(limit)
    )

    items = list(
        db.execute(query)
        .scalars()
        .all()
    )

    return items

def build_personalized_recommendations(
    db: Session,
    user_id: int,
    limit: int = 10,
) -> list[Item]:

    affinity_scores = get_category_affinity(
        db=db,
        user_id=user_id,
    )

    if not affinity_scores:
        return get_trending_candidate_items(
            db=db,
            excluded_item_ids=set(),
            limit=limit
        )

    primary_category, secondary_category = get_top_categories(
        affinity_scores
    )

    excluded_item_ids = get_excluded_item_ids(
        db=db,
        user_id=user_id,
    )

    primary_limit = int(limit * 0.7)
    secondary_limit = int(limit * 0.2)
    trending_limit = limit - primary_limit - secondary_limit

    if primary_category:
        primary_items = get_category_recommendations(
            db=db,
            category=primary_category,
            excluded_item_ids=excluded_item_ids,
            limit=primary_limit,
        )
    else:
        primary_items = []

    if secondary_category:
        secondary_items = get_category_recommendations(
            db=db,
            category=secondary_category,
            excluded_item_ids=excluded_item_ids,
            limit=secondary_limit,
        )
    else:
        secondary_items = []

    trending_items = get_trending_candidate_items(
        db=db,
        excluded_item_ids=excluded_item_ids,
        limit=trending_limit,
    )

    recommendations = primary_items + secondary_items + trending_items

    return recommendations[:limit]