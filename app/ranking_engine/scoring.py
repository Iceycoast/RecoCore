from datetime import UTC, datetime

from app.core.constants import DECAY_RULES

def get_decay_multiplier(interaction_date: datetime) -> float:

    now = (
        datetime.now(UTC)
        if interaction_date.tzinfo is not None
        else datetime.now()
    )

    age_days = (now - interaction_date).days

    for max_age, multiplier in DECAY_RULES:
        if age_days <= max_age:
            return multiplier

    raise ValueError("Invalid decay configuration.")


def calculate_effective_weight(weight: int, interaction_date: datetime) -> float:

    decay_multiplier = get_decay_multiplier(interaction_date)

    return weight * decay_multiplier
