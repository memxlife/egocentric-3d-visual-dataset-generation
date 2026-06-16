from __future__ import annotations

import json
from pathlib import Path

from egodataset.config import QualityConfig
from egodataset.schema import Episode


def validate_episode(episode: Episode, quality: QualityConfig) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if episode.diagnostics["mean_motion"] < quality.min_mean_motion:
        failures.append(
            f"mean_motion {episode.diagnostics['mean_motion']:.5f} < {quality.min_mean_motion:.5f}"
        )
    if len(episode.diagnostics["visible_object_categories"]) < quality.min_visible_object_categories:
        failures.append("too few visible object categories")
    if episode.diagnostics["blank_rgb_fraction"] > quality.max_blank_rgb_fraction:
        failures.append("too many blank RGB frames")
    four_metrics = episode.diagnostics.get("four_metrics", {})
    for metric_name in [
        "generation_speed",
        "realism",
        "per_scenario_comprehensiveness",
        "cross_scenario_diversity",
    ]:
        metric = four_metrics.get(metric_name)
        if metric and not metric.get("passed", False):
            failures.append(f"{metric_name}: {', '.join(metric.get('failures', []))}")
    return not failures, failures


def validate_dataset(root: Path) -> dict:
    episode_manifest = root / "metadata" / "episode_manifest.jsonl"
    if not episode_manifest.exists():
        return {"valid": False, "failures": ["missing metadata/episode_manifest.jsonl"]}

    failures = []
    episodes = 0
    frames = 0
    for line in episode_manifest.read_text().splitlines():
        if not line.strip():
            continue
        episodes += 1
        record = json.loads(line)
        episode_json = root / "episodes" / record["episode_id"] / "episode.json"
        trajectory = root / "episodes" / record["episode_id"] / "trajectory.parquet"
        if not episode_json.exists():
            failures.append(f"missing {episode_json}")
            continue
        if not trajectory.exists():
            failures.append(f"missing {trajectory}")
        payload = json.loads(episode_json.read_text())
        if "four_metrics" not in payload.get("diagnostics", {}):
            failures.append(f"missing four_metrics in {episode_json}")
        frames += len(payload.get("frames", []))
        for frame in payload.get("frames", []):
            for key in ["rgb", "depth", "semantic", "instance"]:
                frame_path = episode_json.parent / frame[key]
                if not frame_path.exists():
                    failures.append(f"missing {frame_path}")
    return {"valid": not failures, "episodes": episodes, "frames": frames, "failures": failures}
