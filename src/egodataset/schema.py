from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FrameRecord:
    frame_index: int
    action: str
    rgb: Path
    depth: Path
    semantic: Path
    instance: Path
    pose: dict[str, float]
    visible_objects: list[dict[str, Any]]


@dataclass(frozen=True)
class Episode:
    episode_id: str
    scene_id: str
    scene_seed: int
    episode_seed: int
    scenario_family: str
    task_type: str
    policy: str
    frame_rate: int
    resolution: tuple[int, int]
    trajectory_length: int
    action_space: str
    render_profile: str
    agent_embodiment: str
    annotations: tuple[str, ...]
    frames: list[FrameRecord]
    diagnostics: dict[str, Any]
