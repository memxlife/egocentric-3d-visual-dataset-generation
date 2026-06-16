from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DatasetConfig:
    name: str
    version: str
    scenario_family: str
    scenario_card: str | None
    frame_rate: int
    resolution: tuple[int, int]
    trajectory_length: int
    action_space: str
    render_profile: str
    agent_embodiment: str
    annotations: tuple[str, ...]


@dataclass(frozen=True)
class GenerationConfig:
    backend: str
    scene_seed_start: int
    episode_seed_start: int
    episodes_per_scene: int
    policy_mix: dict[str, float]
    backend_options: dict[str, Any]


@dataclass(frozen=True)
class QualityConfig:
    min_mean_motion: float
    min_visible_object_categories: int
    max_blank_rgb_fraction: float


@dataclass(frozen=True)
class ToolchainConfig:
    dataset: DatasetConfig
    generation: GenerationConfig
    quality: QualityConfig
    scenario: dict[str, Any] | None
    objects: dict[str, Any]


def load_config(path: Path) -> ToolchainConfig:
    raw = yaml.safe_load(path.read_text())
    dataset_raw = raw["dataset"]
    dataset = DatasetConfig(
        name=dataset_raw["name"],
        version=str(dataset_raw["version"]),
        scenario_family=dataset_raw["scenario_family"],
        scenario_card=dataset_raw.get("scenario_card"),
        frame_rate=int(dataset_raw["frame_rate"]),
        resolution=tuple(dataset_raw["resolution"]),
        trajectory_length=int(dataset_raw["trajectory_length"]),
        action_space=dataset_raw["action_space"],
        render_profile=dataset_raw["render_profile"],
        agent_embodiment=dataset_raw["agent_embodiment"],
        annotations=tuple(dataset_raw["annotations"]),
    )
    generation_raw = raw["generation"]
    generation = GenerationConfig(
        backend=generation_raw["backend"],
        scene_seed_start=int(generation_raw["scene_seed_start"]),
        episode_seed_start=int(generation_raw["episode_seed_start"]),
        episodes_per_scene=int(generation_raw["episodes_per_scene"]),
        policy_mix=generation_raw["policy_mix"],
        backend_options=generation_raw.get("backend_options", {}),
    )
    quality = QualityConfig(**raw["quality"])
    scenario = _load_scenario_card(path, dataset.scenario_card)
    return ToolchainConfig(
        dataset=dataset,
        generation=generation,
        quality=quality,
        scenario=scenario,
        objects=raw.get("objects", {}),
    )


def _load_scenario_card(config_path: Path, scenario_card: str | None) -> dict[str, Any] | None:
    if not scenario_card:
        return None
    scenario_path = Path(scenario_card)
    if not scenario_path.is_absolute():
        scenario_path = config_path.parent / scenario_path
        if not scenario_path.exists():
            scenario_path = config_path.parent.parent / scenario_card
    payload = yaml.safe_load(scenario_path.read_text())
    payload["_path"] = str(scenario_path)
    return payload
