ACTION_WEIGHTS = {
    "view": 1,
    "like": 3,
    "share": 5,
    "purchase": 8
}

DECAY_RULES = [
    (30, 1.0),
    (90, 0.8),
    (180, 0.6),
    (365, 0.4),
    (float("inf"), 0.2),
]