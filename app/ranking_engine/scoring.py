from datetime import datetime, UTC

from app.core.constants import DECAY_RULES

def get_decay_multiplier(interaction_date: datetime) -> float:

    age_days = (datetime.now(UTC) - interaction_date).days

    for max_age, multiplier in DECAY_RULES:
        if age_days <= max_age:
            return multiplier

    raise ValueError("Invalid decay configuration.")


def calculate_effective_weight(weight: int, interaction_date: datetime) -> float:

    decay_multiplier = get_decay_multiplier(interaction_date)

    return weight * decay_multiplier