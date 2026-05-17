from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict

class InteractionCreate(BaseModel):
    user_id: int
    item_id: int

    action_type: Literal[
        "view",
        "like",
        "share",
        "purchase"
    ]

class InteractionResponse(BaseModel):
    interaction_id: int
    user_id: int
    item_id: int
    action_type: str
    weight: float
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )