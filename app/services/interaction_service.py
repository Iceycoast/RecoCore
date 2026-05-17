from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import ACTION_WEIGHTS
from app.models import Interaction, Item, User
from app.schemas import InteractionCreate

def create_interaction(
        payload: InteractionCreate,
        db: Session
) -> Interaction:
    
    user = db.scalar(
        select(User).where(
            User.user_id == payload.user_id
        )
    )

    if user is None:
        raise ValueError ("User not found")
    
    item = db.scalar(
        select(Item).where(
            Item.item_id == payload.item_id
        )
    )

    if item is None:
        raise ValueError ("Item not found")
    
    interaction = Interaction(
        user_id= payload.user_id,
        item_id= payload.item_id,
        action_type= payload.action_type,
        weight= ACTION_WEIGHTS[payload.action_type]
    )

    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    
    return interaction