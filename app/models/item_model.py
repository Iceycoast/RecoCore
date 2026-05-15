from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


if TYPE_CHECKING:
    from app.models.interaction_model import Interaction


class Item(Base):
    __tablename__ = "items"

    item_id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        index=True,
        default=lambda: datetime.now(UTC)
    )

    interactions: Mapped[list["Interaction"]] = relationship(
        back_populates="item",
        cascade="all, delete-orphan"
    )