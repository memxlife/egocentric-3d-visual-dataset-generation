from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from egodataset.config import ToolchainConfig
from egodataset.policies import action_sequence
from egodataset.schema import Episode, FrameRecord


OBJECTS = [
    ("monitor", 1),
    ("keyboard", 2),
    ("mouse", 3),
    ("mug", 4),
    ("phone", 5),
    ("notebook", 6),
    ("lamp", 7),
    ("book", 8),
]


def generate_episode(
    cfg: ToolchainConfig,
    output_dir: Path,
    episode_id: str,
    scene_id: str,
    scene_seed: int,
    episode_seed: int,
    policy: str,
) -> Episode:
    width, height = cfg.dataset.resolution
    frame_dir = output_dir / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng([scene_seed, episode_seed])
    actions = action_sequence(policy, cfg.dataset.trajectory_length, episode_seed)
    object_subset = _sample_objects(rng)
    frames: list[FrameRecord] = []
    poses = []

    for frame_index, action in enumerate(actions):
        pose = _next_pose(frame_index, action, episode_seed)
        poses.append(pose)
        rgb, depth, semantic, instance, visible = _render_mock_frame(
            width=width,
            height=height,
            frame_index=frame_index,
            rng=rng,
            objects=object_subset,
        )
        rgb_path = frame_dir / f"{frame_index:06d}.rgb.webp"
        depth_path = frame_dir / f"{frame_index:06d}.depth.png"
        semantic_path = frame_dir / f"{frame_index:06d}.semantic.png"
        instance_path = frame_dir / f"{frame_index:06d}.instance.png"
        rgb.save(rgb_path, "WEBP", quality=85)
        Image.fromarray(depth).save(depth_path)
        Image.fromarray(semantic).save(semantic_path)
        Image.fromarray(instance).save(instance_path)
        frames.append(
            FrameRecord(
                frame_index=frame_index,
                action=action,
                rgb=rgb_path,
                depth=depth_path,
                semantic=semantic_path,
                instance=instance_path,
                pose=pose,
                visible_objects=visible,
            )
        )

    diagnostics = {
        "backend": "mock",
        "mean_motion": _mean_motion(poses),
        "visible_object_categories": sorted({obj["category"] for f in frames for obj in f.visible_objects}),
        "blank_rgb_fraction": 0.0,
    }
    return Episode(
        episode_id=episode_id,
        scene_id=scene_id,
        scene_seed=scene_seed,
        episode_seed=episode_seed,
        scenario_family=cfg.dataset.scenario_family,
        task_type="active_visual_scan",
        policy=policy,
        frame_rate=cfg.dataset.frame_rate,
        resolution=cfg.dataset.resolution,
        trajectory_length=cfg.dataset.trajectory_length,
        action_space=cfg.dataset.action_space,
        render_profile=cfg.dataset.render_profile,
        agent_embodiment=cfg.dataset.agent_embodiment,
        annotations=cfg.dataset.annotations,
        frames=frames,
        diagnostics=diagnostics,
    )


def _sample_objects(rng: np.random.Generator) -> list[tuple[str, int]]:
    required = [OBJECTS[0], OBJECTS[1], OBJECTS[2]]
    optional = OBJECTS[3:]
    count = int(rng.integers(1, len(optional) + 1))
    indices = rng.choice(len(optional), size=count, replace=False)
    return required + [optional[int(i)] for i in sorted(indices)]


def _render_mock_frame(
    width: int,
    height: int,
    frame_index: int,
    rng: np.random.Generator,
    objects: list[tuple[str, int]],
) -> tuple[Image.Image, np.ndarray, np.ndarray, np.ndarray, list[dict[str, Any]]]:
    x_grad = np.linspace(20, 210, width, dtype=np.uint8)
    y_grad = np.linspace(30, 180, height, dtype=np.uint8)
    rgb_arr = np.zeros((height, width, 3), dtype=np.uint8)
    rgb_arr[..., 0] = x_grad[None, :]
    rgb_arr[..., 1] = y_grad[:, None]
    rgb_arr[..., 2] = (80 + frame_index * 7) % 255
    rgb = Image.fromarray(rgb_arr, "RGB")
    draw = ImageDraw.Draw(rgb)
    depth = np.full((height, width), 4200, dtype=np.uint16)
    semantic = np.zeros((height, width), dtype=np.uint8)
    instance = np.zeros((height, width), dtype=np.uint16)
    visible = []

    for instance_id, (category, semantic_id) in enumerate(objects, start=1):
        base_x = int((instance_id / (len(objects) + 1)) * width)
        jitter = int(12 * np.sin(frame_index * 0.4 + instance_id))
        x0 = max(0, base_x - 18 + jitter)
        y0 = max(0, int(height * 0.45) + int(rng.integers(-12, 12)))
        x1 = min(width - 1, x0 + int(rng.integers(18, 46)))
        y1 = min(height - 1, y0 + int(rng.integers(16, 52)))
        color = (
            int((semantic_id * 41) % 255),
            int((semantic_id * 83) % 255),
            int((semantic_id * 127) % 255),
        )
        draw.rounded_rectangle((x0, y0, x1, y1), radius=3, fill=color)
        semantic[y0:y1, x0:x1] = semantic_id
        instance[y0:y1, x0:x1] = instance_id
        depth[y0:y1, x0:x1] = np.uint16(800 + semantic_id * 170 + frame_index * 3)
        visible.append(
            {
                "instance_id": instance_id,
                "category": category,
                "bbox_xyxy": [x0, y0, x1, y1],
                "semantic_id": semantic_id,
            }
        )
    return rgb, depth, semantic, instance, visible


def _next_pose(frame_index: int, action: str, seed: int) -> dict[str, float]:
    phase = (seed % 97) / 97.0
    return {
        "x": round(0.01 * frame_index, 5),
        "y": round(1.55 + (0.08 if action == "StandUp" else 0.0) - (0.08 if action == "CrouchDown" else 0.0), 5),
        "z": round(0.02 * np.sin(frame_index * 0.3 + phase), 5),
        "yaw": round((frame_index * 3.5 + (8 if action == "RotateRight" else -8 if action == "RotateLeft" else 0)) % 360, 5),
        "pitch": round(-8 if action == "LookDown" else 8 if action == "LookUp" else 0, 5),
        "roll": 0.0,
    }


def _mean_motion(poses: list[dict[str, float]]) -> float:
    if len(poses) < 2:
        return 0.0
    diffs = []
    for prev, cur in zip(poses[:-1], poses[1:]):
        diffs.append(
            ((cur["x"] - prev["x"]) ** 2 + (cur["y"] - prev["y"]) ** 2 + (cur["z"] - prev["z"]) ** 2)
            ** 0.5
        )
    return float(np.mean(diffs))
