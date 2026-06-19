from collections import Counter
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import Interaction, Item, User
from app.models.base import Base


def build_test_client() -> tuple[TestClient, Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), db


def add_item(db: Session, name: str, category: str) -> Item:
    item = Item(name=name, category=category)
    db.add(item)
    db.flush()
    return item


def add_interaction(
    db: Session,
    user: User,
    item: Item,
    action_type: str,
    weight: float,
) -> None:
    db.add(
        Interaction(
            user_id=user.user_id,
            item_id=item.item_id,
            action_type=action_type,
            weight=weight,
            created_at=datetime.now(),
        )
    )


def test_trending_recommendations_can_filter_by_category() -> None:
    client, db = build_test_client()

    try:
        user = User(name="Trend User", email="trend-user@example.com")
        db.add(user)
        db.flush()

        gaming_item = add_item(db, "Gaming Item", "gaming")
        books_item = add_item(db, "Books Item", "books")

        add_interaction(db, user, gaming_item, "purchase", 8)
        add_interaction(db, user, books_item, "purchase", 20)
        db.commit()

        response = client.get(
            "/recommendations/trending",
            params={
                "category": "gaming",
                "limit": 10,
            },
        )

        assert response.status_code == 200

        body = response.json()
        assert body["success"] is True
        assert body["message"] == "Trending recommendations fetched successfully"
        assert len(body["data"]) == 1
        assert body["data"][0]["item_id"] == gaming_item.item_id
        assert body["data"][0]["category"] == "gaming"

    finally:
        app.dependency_overrides.clear()
        db.close()


def test_personalized_recommendations_follow_expected_rules() -> None:
    client, db = build_test_client()

    try:
        target_user = User(name="Target User", email="target-user@example.com")
        other_user = User(name="Other User", email="other-user@example.com")
        db.add_all([target_user, other_user])
        db.flush()

        excluded_like = add_item(db, "Liked Electronics", "electronics")
        excluded_share = add_item(db, "Shared Electronics", "electronics")
        book_affinity = add_item(db, "Viewed Book", "books")

        [
            add_item(db, f"Electronics Candidate {index}", "electronics")
            for index in range(1, 8)
        ]
        [
            add_item(db, f"Book Candidate {index}", "books")
            for index in range(1, 3)
        ]
        trending_candidate = add_item(db, "Trending Gaming Candidate", "gaming")

        add_interaction(db, target_user, excluded_like, "like", 3)
        add_interaction(db, target_user, excluded_share, "share", 5)
        add_interaction(db, target_user, book_affinity, "view", 1)
        add_interaction(db, other_user, trending_candidate, "purchase", 100)
        db.commit()

        response = client.get(
            f"/recommendations/users/{target_user.user_id}",
            params={"limit": 10},
        )

        assert response.status_code == 200

        recommendations = response.json()
        recommendation_ids = [item["item_id"] for item in recommendations]
        excluded_ids = {excluded_like.item_id, excluded_share.item_id}
        category_counts = Counter(item["category"] for item in recommendations)

        assert len(recommendations) == 10
        assert not excluded_ids.intersection(recommendation_ids)
        assert len(recommendation_ids) == len(set(recommendation_ids))
        assert category_counts["electronics"] == 7
        assert category_counts["books"] == 2
        assert category_counts["gaming"] == 1

    finally:
        app.dependency_overrides.clear()
        db.close()
