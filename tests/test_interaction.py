from collections.abc import Generator
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import app
from app.models import Item, User
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


def test_create_interaction_returns_created_interaction() -> None:
    client, db = build_test_client()

    try:
        user = User(name="Test User", email="test-user@example.com")
        item = Item(name="Test Item", category="gaming")
        db.add_all([user, item])
        db.commit()

        response = client.post(
            "/interactions",
            json={
                "user_id": user.user_id,
                "item_id": item.item_id,
                "action_type": "like",
            },
        )

        assert response.status_code == 201

        body = response.json()
        assert body["success"] is True
        assert body["message"] == "Interaction created successfully"
        assert body["data"]["user_id"] == user.user_id
        assert body["data"]["item_id"] == item.item_id
        assert body["data"]["action_type"] == "like"
        assert body["data"]["weight"] == 3
        assert body["data"]["interaction_id"] is not None
        assert body["data"]["created_at"] is not None

    finally:
        app.dependency_overrides.clear()
        db.close()


def test_create_interaction_returns_404_for_missing_user() -> None:
    client, db = build_test_client()

    try:
        item = Item(name="Existing Item", category="books")
        db.add(item)
        db.commit()

        response = client.post(
            "/interactions",
            json={
                "user_id": 999,
                "item_id": item.item_id,
                "action_type": "view",
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    finally:
        app.dependency_overrides.clear()
        db.close()
