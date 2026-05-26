import random
from datetime import datetime, UTC, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.core import ACTION_WEIGHTS
from app.db import SessionLocal
from app.models import Interaction, Item, User

fake = Faker()

CATEGORIES = [
    "electronics",
    "gaming",
    "books",
    "fashion",
    "fitness"
]

CATEGORY_WEIGHTS = [
    40,
    30,
    15,
    10,
    5
]

ACTION_TYPES = [
    "view",
    "like",
    "share",
    "purchase"
]

ACTION_TYPE_WEIGHTS = [
    60,
    25,
    10,
    5
]


def clear_tables(db: Session) -> None:
    
    db.query(Interaction).delete()
    db.query(Item).delete()
    db.query(User).delete()

    db.commit()
    



def seed_users(db: Session, total_users: int = 10) -> list[User]:
    
    users = []

    for _ in range(total_users):

        user = User(
            name= fake.name(),
            email= fake.email()
        )
        users.append(user)
    
    db.add_all(users)
    db.commit()

    return users

def seed_items(db: Session, total_items: int = 100) -> list[Item]:
    
    items = []

    for _ in range(total_items):

        category = random.choices(
            population=CATEGORIES,
            weights=CATEGORY_WEIGHTS,
            k=1
        )[0]

        item = Item(
            name= fake.catch_phrase(),
            category=category
        )
        items.append(item)

    db.add_all(items)
    db.commit()

    return items

def seed_interaction(db: Session, users: list[User], items: list[Item]) -> list[Interaction]:

    interactions = []

    for user in users:
        
        interacted_items = random.sample(
            items,
            k= random.randint(5,15)
        )

        for item in interacted_items:

            action_type = random.choices(
                population=ACTION_TYPES,
                weights=ACTION_TYPE_WEIGHTS,
                k=1
            )[0]
    
            interaction = Interaction(
                user_id= user.user_id,
                item_id= item.item_id,
                action_type= action_type,
                weight= ACTION_WEIGHTS[action_type],
                created_at=datetime.now(UTC) - timedelta(
                    days= random.randint(0,30)
                )
            )

            interactions.append(interaction)

    db.add_all(interactions)
    db.commit()

    return interactions



def main():
    
    db: Session = SessionLocal()

    try:
        clear_tables(db)

        users = seed_users(
            db=db,
            total_users=10
        )

        items = seed_items(
            db=db,
            total_items=100
        )

        interactions = seed_interaction(
            db=db,
            users=users,
            items=items
        )

        print(f"seeded {len(users)} users")
        print(f"seeded {len(items)} items")
        print(f"seeded {len(interactions)} interactions")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()