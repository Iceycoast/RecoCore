from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


if TYPE_CHECKING:
    from app.models.item_model import Item
    from app.models.user_model import User


class Interaction(Base):
    __tablename__ = "interactions"

    __table_args__ = (
        Index("idx_item_created", "item_id", "created_at"),
        Index("idx_user_created", "user_id", "created_at"),
    )

    interaction_id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        index=True,
        nullable=False
    )

    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.item_id"),
        index=True,
        nullable=False
    )

    action_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False
    )

    weight: Mapped[float] = mapped_column(
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        index=True,
        default=lambda: datetime.now(UTC)
    )

    user: Mapped["User"] = relationship(
        back_populates="interactions"
    )

    item: Mapped["Item"] = relationship(
        back_populates="interactions"
    )