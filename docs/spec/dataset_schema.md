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
    schema_version.json
  scenes/
    scene_000001/
      scene.json
      world.json
      object_metadata.json
      validation.json
      probe_views/
  episodes/
    episode_000000001/
      episode.json
      trajectory.parquet
      camera_intrinsics.json
      quality_metrics.json
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
    test_object_category_held_out.txt
    test_object_instance_held_out.txt
    test_layout_held_out.txt
    test_trajectory_held_out.txt
    test_material_held_out.txt
    test_cross_scenario.txt
```

The exact file formats may change for storage efficiency, but the information must be preserved.

## Coordinate Conventions

All position units are meters. The canonical pose is:

```text
T_wc: camera-to-world transform
```

`T_wc` maps points from camera coordinates to world coordinates. If a backend natively reports
world-to-camera or a different handedness, the writer must convert or explicitly record the backend
convention in metadata.

Canonical pose should store:

- metric position in world coordinates;
- quaternion orientation as `xyzw`;
- optional yaw/pitch/roll for debugging;
- frame index and timestamp;
- backend pose fields for traceability when useful.

Example:

```json
{
  "frame_id": 0,
  "timestamp": 0.0,
  "T_convention": "T_wc_camera_to_world",
  "position_m": [0.0, 1.2, 2.4],
  "orientation_quaternion_xyzw": [0.0, 0.0, 0.0, 1.0],
  "yaw_pitch_roll_degrees_debug": [0.0, 0.0, 0.0],
  "fov_degrees": 60.0
}
```

The camera coordinate frame must be declared in `schema_version.json`. If the renderer uses a
different axis convention, the dataset must state whether camera coordinates use `+x` right, `+y`
up or down, and `+z` forward or backward.

## Depth Encoding

Depth must be unambiguous.

Each dataset version must declare:

- depth units, normally meters;
- file format and dtype;
- near and far clipping planes;
- invalid depth value;
- whether depth is metric z-depth or ray distance;
- whether depth is in camera coordinates or converted from renderer output.

Recommended Version 1 fields:

```json
{
  "depth_units": "meters",
  "depth_type": "metric_z_depth",
  "invalid_depth_value": 0,
  "near_clip_m": 0.05,
  "far_clip_m": 20.0
}
```

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

## Segmentation And Object ID Stability

Semantic classes must come from `metadata/object_taxonomy.json`. Instance IDs must be stable within
one static scene.

Required guarantees:

- semantic class ids are stable across the dataset version;
- object instance ids are stable across frames in a sequence;
- object instance ids are stable across episodes generated from the same static scene;
- regenerated scenes with the same scene seed should produce the same object ids when the backend
  supports deterministic generation;
- visible object ids mean object instances with at least `min_object_pixels` visible pixels unless
  otherwise stated.

The schema should distinguish:

```text
semantic_class_id
scene_object_id
episode_visible_object_id
backend_object_id
```

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
- scene validation scores;
- rejection reason codes when rejected.

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
- object-aware start parameters;
- camera poses;
- relative motions;
- camera intrinsics;
- action or primitive sequence;
- primitive parameters;
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

## Seed Semantics

Every generated object must be reproducible from explicit seeds:

| Seed | Controls |
|---|---|
| dataset seed | High-level split and batch sampling. |
| scenario seed | Scenario family and layout-template sampling. |
| scene seed | Static scene content, object placement, materials, lighting. |
| episode seed | Anchor, start pose, primitive, and trajectory parameters. |
| render seed | Any stochastic renderer effects if enabled. |

If a backend cannot guarantee exact regeneration, the dataset must record backend version, asset
version, and enough metadata to explain the difference.

## Schema Versioning

Each dataset root must include `metadata/schema_version.json` with:

- schema version;
- generator git commit;
- backend name and version;
- asset source and version;
- coordinate convention;
- depth convention;
- taxonomy version;
- split policy version;
- metric threshold version.
