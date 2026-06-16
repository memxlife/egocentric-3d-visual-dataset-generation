from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from egodataset.config import ToolchainConfig
from egodataset.policies import action_sequence
from egodataset.schema import Episode, FrameRecord


def generate_episode(
    cfg: ToolchainConfig,
    output_dir: Path,
    episode_id: str,
    scene_id: str,
    scene_seed: int,
    episode_seed: int,
    policy: str,
) -> Episode:
    try:
        from ai2thor.controller import Controller
        from ai2thor.platform import CloudRendering
    except Exception as exc:
        raise RuntimeError("ai2thor backend requires ai2thor to be installed") from exc

    width, height = cfg.dataset.resolution
    frame_dir = output_dir / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    options = cfg.generation.backend_options
    scene = _resolve_scene(cfg, scene_seed)
    actions = action_sequence(policy, cfg.dataset.trajectory_length, episode_seed)
    controller = Controller(
        platform=CloudRendering,
        scene=scene,
        width=width,
        height=height,
        renderDepthImage=True,
        renderInstanceSegmentation=True,
        renderSemanticSegmentation=True,
    )

    frames: list[FrameRecord] = []
    poses: list[dict[str, float]] = []
    failed_actions = 0
    try:
        for frame_index, action in enumerate(actions):
            event = controller.step(action=action)
            if not event.metadata.get("lastActionSuccess", False):
                failed_actions += 1
                event = controller.step(action="Pass")
            pose = _agent_pose(event.metadata)
            poses.append(pose)
            visible_objects = _visible_objects(event.metadata)
            rgb_path = frame_dir / f"{frame_index:06d}.rgb.webp"
            depth_path = frame_dir / f"{frame_index:06d}.depth.png"
            semantic_path = frame_dir / f"{frame_index:06d}.semantic.png"
            instance_path = frame_dir / f"{frame_index:06d}.instance.png"
            Image.fromarray(event.frame).save(rgb_path, "WEBP", quality=85)
            _save_depth(event, depth_path)
            _save_segmentation(getattr(event, "semantic_segmentation_frame", None), semantic_path)
            _save_segmentation(getattr(event, "instance_segmentation_frame", None), instance_path)
            frames.append(
                FrameRecord(
                    frame_index=frame_index,
                    action=action,
                    rgb=rgb_path,
                    depth=depth_path,
                    semantic=semantic_path,
                    instance=instance_path,
                    pose=pose,
                    visible_objects=visible_objects,
                )
            )
    finally:
        controller.stop()

    diagnostics = {
        "backend": cfg.generation.backend,
        "scene": _scene_name(scene),
        "mean_motion": _mean_motion(poses),
        "failed_action_count": failed_actions,
        "visible_object_categories": sorted(
            {obj["category"] for frame in frames for obj in frame.visible_objects}
        ),
        "blank_rgb_fraction": 0.0,
    }
    return Episode(
        episode_id=episode_id,
        scene_id=scene_id,
        scene_seed=scene_seed,
        episode_seed=episode_seed,
        scenario_family=cfg.dataset.scenario_family,
        task_type=options.get("task_type", "ai2thor_smoke"),
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


def _resolve_scene(cfg: ToolchainConfig, scene_seed: int) -> Any:
    options = cfg.generation.backend_options
    if cfg.generation.backend == "procthor" or options.get("scene_source") == "procthor":
        try:
            import prior
        except Exception as exc:
            raise RuntimeError("procthor backend requires prior to be installed") from exc
        dataset_name = options.get("dataset", "procthor-10k")
        split = options.get("split", "train")
        dataset = prior.load_dataset(dataset_name)
        scenes = dataset[split]
        index = int(options.get("start_index", 0)) + (scene_seed % max(len(scenes), 1))
        return scenes[index % len(scenes)]
    return options.get("scene", "FloorPlan1")


def _scene_name(scene: Any) -> str:
    if isinstance(scene, str):
        return scene
    if isinstance(scene, dict):
        metadata = scene.get("metadata", {})
        return str(metadata.get("id") or metadata.get("sceneName") or "procthor_house")
    return type(scene).__name__


def _agent_pose(metadata: dict[str, Any]) -> dict[str, float]:
    agent = metadata["agent"]
    position = agent["position"]
    rotation = agent["rotation"]
    return {
        "x": float(position["x"]),
        "y": float(position["y"]),
        "z": float(position["z"]),
        "yaw": float(rotation["y"]),
        "pitch": float(agent.get("cameraHorizon", 0.0)),
        "roll": float(rotation.get("z", 0.0)),
    }


def _visible_objects(metadata: dict[str, Any]) -> list[dict[str, Any]]:
    visible = []
    for index, obj in enumerate(metadata.get("objects", []), start=1):
        if not obj.get("visible", False):
            continue
        visible.append(
            {
                "instance_id": obj.get("objectId", str(index)),
                "category": obj.get("objectType", "unknown"),
                "name": obj.get("name", ""),
                "distance": obj.get("distance"),
            }
        )
    return visible


def _save_depth(event: Any, path: Path) -> None:
    depth = getattr(event, "depth_frame", None)
    if depth is None:
        Image.fromarray(np.zeros_like(event.frame[:, :, 0], dtype=np.uint16)).save(path)
        return
    depth_mm = np.clip(np.asarray(depth) * 1000.0, 0, np.iinfo(np.uint16).max).astype(np.uint16)
    Image.fromarray(depth_mm).save(path)


def _save_segmentation(frame: Any, path: Path) -> None:
    if frame is None:
        Image.fromarray(np.zeros((1, 1), dtype=np.uint8)).save(path)
        return
    array = np.asarray(frame)
    if array.ndim == 2:
        Image.fromarray(array.astype(np.uint8)).save(path)
    else:
        Image.fromarray(array[:, :, :3].astype(np.uint8)).save(path)


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
