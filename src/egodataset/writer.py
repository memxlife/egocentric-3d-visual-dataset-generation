from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from egodataset.config import ToolchainConfig
from egodataset.policies import DISCRETE_EGOCENTRIC_V1
from egodataset.schema import Episode


def initialize_dataset_root(root: Path, cfg: ToolchainConfig) -> None:
    (root / "metadata").mkdir(parents=True, exist_ok=True)
    (root / "episodes").mkdir(parents=True, exist_ok=True)
    (root / "scenes").mkdir(parents=True, exist_ok=True)
    (root / "splits").mkdir(parents=True, exist_ok=True)
    _write_json(root / "metadata" / "action_space.json", {"discrete_egocentric_v1": DISCRETE_EGOCENTRIC_V1})
    _write_json(root / "metadata" / "object_taxonomy.json", cfg.objects.get("taxonomy", {}))
    if cfg.scenario:
        _write_json(root / "metadata" / "scenario_card.json", cfg.scenario)


def write_episode(root: Path, episode: Episode) -> None:
    episode_dir = root / "episodes" / episode.episode_id
    episode_dir.mkdir(parents=True, exist_ok=True)
    scene_dir = root / "scenes" / episode.scene_id
    scene_config = scene_dir / "scene_config.json"
    if not scene_config.exists():
        scene_dir.mkdir(parents=True, exist_ok=True)
        scene_record = _scene_manifest_record(episode)
        _write_json(scene_config, scene_record)
        _append_jsonl(root / "metadata" / "scene_manifest.jsonl", scene_record)
    metadata = asdict(episode)
    metadata["frames"] = [
        {
            **asdict(frame),
            "rgb": str(frame.rgb.relative_to(episode_dir)),
            "depth": str(frame.depth.relative_to(episode_dir)),
            "semantic": str(frame.semantic.relative_to(episode_dir)),
            "instance": str(frame.instance.relative_to(episode_dir)),
        }
        for frame in episode.frames
    ]
    _write_json(episode_dir / "episode.json", metadata)
    _write_trajectory(episode_dir / "trajectory.parquet", episode)
    _append_jsonl(root / "metadata" / "episode_manifest.jsonl", _episode_manifest_record(episode))


def write_dataset_manifest(root: Path, cfg: ToolchainConfig, episodes: int, frames: int) -> None:
    _append_jsonl(
        root / "metadata" / "dataset_manifest.jsonl",
        {
            "dataset_name": cfg.dataset.name,
            "version": cfg.dataset.version,
            "scenario_family": cfg.dataset.scenario_family,
            "scenario_card": cfg.dataset.scenario_card,
            "backend": cfg.generation.backend,
            "episodes": episodes,
            "frames": frames,
            "render_profile": cfg.dataset.render_profile,
            "annotations": list(cfg.dataset.annotations),
        },
    )


def write_run_report(root: Path, report: dict) -> None:
    _write_json(root / "metadata" / "run_report.json", report)


def _write_trajectory(path: Path, episode: Episode) -> None:
    rows = []
    for frame in episode.frames:
        rows.append(
            {
                "frame_index": frame.frame_index,
                "action": frame.action,
                "pose_x": frame.pose["x"],
                "pose_y": frame.pose["y"],
                "pose_z": frame.pose["z"],
                "pose_yaw": frame.pose["yaw"],
                "pose_pitch": frame.pose["pitch"],
                "pose_roll": frame.pose["roll"],
                "visible_object_count": len(frame.visible_objects),
                "visible_categories": ",".join(sorted({obj["category"] for obj in frame.visible_objects})),
            }
        )
    pd.DataFrame(rows).to_parquet(path, index=False)


def _episode_manifest_record(episode: Episode) -> dict:
    return {
        "episode_id": episode.episode_id,
        "scene_id": episode.scene_id,
        "scene_seed": episode.scene_seed,
        "episode_seed": episode.episode_seed,
        "scenario_family": episode.scenario_family,
        "policy": episode.policy,
        "frames": len(episode.frames),
        "four_metrics": episode.diagnostics.get("four_metrics", {}),
        "validity": episode.diagnostics,
    }


def _scene_manifest_record(episode: Episode) -> dict:
    return {
        "scene_id": episode.scene_id,
        "scene_seed": episode.scene_seed,
        "scenario_family": episode.scenario_family,
    }


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _append_jsonl(path: Path, payload: dict) -> None:
    with path.open("a") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")
