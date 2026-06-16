from __future__ import annotations

import random


DISCRETE_EGOCENTRIC_V1 = [
    "MoveAhead",
    "MoveBack",
    "MoveLeft",
    "MoveRight",
    "RotateLeft",
    "RotateRight",
    "LookUp",
    "LookDown",
    "CrouchDown",
    "StandUp",
    "Stop",
]

SCRIPTED_ACTIVE_SCAN = [
    "MoveAhead",
    "LookDown",
    "RotateLeft",
    "RotateRight",
    "MoveRight",
    "LookUp",
    "MoveLeft",
    "LookDown",
]

TARGET_SEARCH = [
    "RotateLeft",
    "MoveAhead",
    "RotateRight",
    "MoveAhead",
    "LookDown",
    "MoveRight",
]


def choose_policy(policy_mix: dict[str, float], seed: int) -> str:
    rng = random.Random(seed)
    names = list(policy_mix)
    weights = [policy_mix[name] for name in names]
    return rng.choices(names, weights=weights, k=1)[0]


def action_sequence(policy: str, length: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    if policy == "random_scan":
        return [rng.choice(DISCRETE_EGOCENTRIC_V1[:-1]) for _ in range(length)]
    if policy == "target_search":
        pattern = TARGET_SEARCH
    elif policy == "scripted_active_scan":
        pattern = SCRIPTED_ACTIVE_SCAN
    else:
        raise ValueError(f"Unknown policy: {policy}")
    return [pattern[i % len(pattern)] for i in range(length)]
