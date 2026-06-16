from __future__ import annotations

import shutil
import time
from pathlib import Path

from egodataset.backends import ai2thor_backend, mock
from egodataset.config import ToolchainConfig
from egodataset.metrics import compute_episode_metrics
from egodataset.policies import choose_policy
from egodataset.validators import validate_episode
from egodataset.writer import initialize_dataset_root, write_dataset_manifest, write_episode, write_run_report


def generate_dataset(
    cfg: ToolchainConfig,
    output: Path,
    episodes: int,
    frames: int | None = None,
    overwrite: bool = False,
) -> dict:
    if overwrite and output.exists():
        shutil.rmtree(output)
    initialize_dataset_root(output, cfg)

    generated = 0
    rejected = 0
    total_frames = 0
    run_started = time.perf_counter()
    rejection_reasons: dict[str, int] = {}
    trajectory_length = frames or cfg.dataset.trajectory_length
    cfg = _with_trajectory_length(cfg, trajectory_length)

    for episode_index in range(episodes):
        scene_index = episode_index // cfg.generation.episodes_per_scene
        scene_seed = cfg.generation.scene_seed_start + scene_index
        episode_seed = cfg.generation.episode_seed_start + episode_index
        scene_id = f"scene_{scene_index:06d}"
        episode_id = f"episode_{episode_index:09d}"
        episode_dir = output / "episodes" / episode_id
        policy = choose_policy(cfg.generation.policy_mix, episode_seed)

        episode_started = time.perf_counter()
        episode = _backend_generate(
            cfg=cfg,
            output_dir=episode_dir,
            episode_id=episode_id,
            scene_id=scene_id,
            scene_seed=scene_seed,
            episode_seed=episode_seed,
            policy=policy,
        )
        elapsed = max(time.perf_counter() - episode_started, 1e-9)
        episode.diagnostics["timing"] = {
            "wall_time_seconds": elapsed,
            "raw_frames_per_second": len(episode.frames) / elapsed,
        }
        episode.diagnostics["four_metrics"] = compute_episode_metrics(episode, cfg.scenario)
        valid, failures = validate_episode(episode, cfg.quality)
        if not valid:
            rejected += 1
            for failure in failures:
                key = failure.split(":", 1)[0]
                rejection_reasons[key] = rejection_reasons.get(key, 0) + 1
            shutil.rmtree(episode_dir, ignore_errors=True)
            print(f"rejected {episode_id}: {'; '.join(failures)}")
            continue
        write_episode(output, episode)
        generated += 1
        total_frames += len(episode.frames)

    write_dataset_manifest(output, cfg, generated, total_frames)
    wall_time = max(time.perf_counter() - run_started, 1e-9)
    report = {
        "generated": generated,
        "rejected": rejected,
        "frames": total_frames,
        "output": str(output),
        "wall_time_seconds": wall_time,
        "valid_frames_per_second": total_frames / wall_time,
        "rejection_reasons": rejection_reasons,
        "scenario_card": cfg.dataset.scenario_card,
    }
    write_run_report(output, report)
    return report


def _backend_generate(**kwargs):
    cfg = kwargs["cfg"]
    if cfg.generation.backend == "mock":
        return mock.generate_episode(**kwargs)
    if cfg.generation.backend in {"ai2thor", "procthor"}:
        return ai2thor_backend.generate_episode(**kwargs)
    raise ValueError(f"Unsupported backend: {cfg.generation.backend}")


def _with_trajectory_length(cfg: ToolchainConfig, trajectory_length: int) -> ToolchainConfig:
    dataset = cfg.dataset.__class__(
        **{**cfg.dataset.__dict__, "trajectory_length": int(trajectory_length)}
    )
    return ToolchainConfig(
        dataset=dataset,
        generation=cfg.generation,
        quality=cfg.quality,
        scenario=cfg.scenario,
        objects=cfg.objects,
    )
