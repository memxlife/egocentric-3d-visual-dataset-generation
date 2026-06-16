# Dataset Schema

## Dataset Layout

The dataset unit is a sequence episode generated from one accepted static scene.

Recommended conceptual layout:

```text
dataset_root/
  metadata/
    dataset_manifest.jsonl
    scene_manifest.jsonl
    episode_manifest.jsonl
    object_taxonomy.json
    action_space.json
  scenes/
    scene_000001/
      scene.json
      world.json
      object_metadata.json
      validation.json
  episodes/
    episode_000000001/
      episode.json
      trajectory.parquet
      camera_intrinsics.json
      frames/
        000000.rgb.webp
        000000.depth.png
        000000.semantic.png
        000000.instance.png
        000000.normal.exr
        000000.point3d.exr
        000000.visible_surface_ids.npy
        000000.visible_object_ids.json
  splits/
    train.txt
    val_seen_category.txt
    test_scene_held_out.txt
    test_object_held_out.txt
    test_layout_held_out.txt
    test_trajectory_held_out.txt
```

The exact file formats may change for storage efficiency, but the information must be preserved.

## Minimal Frame Fields

Version 1 mandatory frame fields:

- RGB;
- depth;
- camera pose;
- camera intrinsics;
- frame index or timestamp;
- semantic segmentation;
- instance segmentation;
- visible object identifiers.

Preferred full frame fields:

- RGB;
- depth;
- surface normals;
- semantic segmentation;
- instance segmentation;
- pixel-to-3D correspondence map;
- visible surface ids;
- visible object ids;
- optional optical flow to adjacent frames.

## Camera Pose

Canonical pose should use metric position and quaternion orientation:

```json
{
  "frame_id": 0,
  "timestamp": 0.0,
  "position_m": [0.0, 1.2, 2.4],
  "orientation_quaternion_xyzw": [0.0, 0.0, 0.0, 1.0],
  "yaw_pitch_roll_degrees": [0.0, 0.0, 0.0],
  "fov_degrees": 60.0
}
```

Yaw, pitch, and roll are for debugging. Quaternion orientation is canonical.

## Camera Intrinsics

Every sequence must store camera intrinsics:

```json
{
  "width": 768,
  "height": 768,
  "fx": 665.1,
  "fy": 665.1,
  "cx": 384.0,
  "cy": 384.0,
  "fov_degrees": 60.0,
  "near_clip_m": 0.05,
  "far_clip_m": 20.0
}
```

The intrinsic matrix is:

```text
K = [[fx, 0, cx],
     [0, fy, cy],
     [0, 0, 1]]
```

## Static Scene Metadata

Scene metadata must include:

- scene id;
- scenario family;
- layout template;
- clutter level;
- room bounds;
- support surfaces;
- free-space summary;
- lighting profile;
- accepted/rejected state;
- scene validation scores.

Object metadata must include:

- object id;
- category;
- mesh id;
- shape family;
- position;
- orientation;
- scale;
- support relation;
- material;
- base color;
- texture id;
- roughness;
- metallic;
- static state.

## Sequence Metadata

Each episode must store:

- scenario id;
- sequence id;
- static scene id;
- selected semantic anchor;
- camera poses;
- relative motions;
- camera intrinsics;
- action or primitive sequence;
- quality scores;
- acceptance/rejection reasons;
- paths to frame annotations.

The core model input is:

```text
(I_0:k, delta_T_k:H-1)
```

The target is:

```text
I_k+1:H
```
