# Metrics And Acceptance

## Top-Level Dataset Metrics

The dataset is judged by four top-level metrics:

| Metric | What it measures | Failure if weak |
|---|---|---|
| generation speed | Accepted frames per second and stage timing. | Research loops become too slow to iterate. |
| realism | Physical, geometric, semantic, and visual plausibility. | Models learn artifacts from invalid worlds. |
| per-scenario comprehensiveness | Required content, viewpoints, motions, objects, and visibility events inside each scenario. | A scenario is present by name but not actually covered. |
| cross-scenario diversity | Scenario families, layouts, objects, appearances, states, and trajectory types. | Dataset collapses into repeated templates. |

Acceptance metrics must be executable. Each metric should define name, purpose, inputs, formula,
valid range, default threshold, scenario override, failure mode, debug visualization, and rejection
reason code.

## Static Scene Acceptance

A static scene must pass:

```text
C_scene(z) =
  C_semantic_complete
  and C_physical
  and C_probe_visual_content
  and C_free_space
  and C_appearance_diverse
```

| Metric | Purpose | Inputs | Formula or test | Initial threshold | Reject reason |
|---|---|---|---|---|---|
| `semantic_completeness` | Ensure required scenario grammar is present. | Object metadata, scenario card. | Required structures and categories are present. | all required items present | `missing_required_content` |
| `support_validity` | Reject floating, embedded, or nonsensical objects. | Object poses, support surfaces, collision checks. | All required support relations valid and interpenetration below tolerance. | true | `invalid_support_relation` |
| `probe_foreground_ratio` | Reject scenes with no useful viewpoints. | Probe semantic masks. | Median foreground ratio over probe views. | scenario threshold | `low_probe_foreground` |
| `probe_visible_object_count` | Ensure probe views show meaningful entities. | Probe instance masks/object ids. | Median visible object count. | >= 2 or 3 | `low_probe_object_count` |
| `free_space_volume` | Ensure camera can move. | Occupancy/free-space field. | Valid camera-center samples or connected volume. | scenario threshold | `insufficient_free_space` |
| `appearance_entropy` | Avoid one-note materials/colors. | Material and color metadata. | Category/material/color entropy or unique bins. | pilot calibrated | `low_appearance_diversity` |

## Frame Metric Dictionary

### `foreground_ratio`

Purpose: reject frames dominated by empty background such as wall, ceiling, or floor.

Inputs: semantic segmentation map and scenario foreground class set.

Formula:

```text
foreground_ratio = foreground_pixels / valid_pixels
```

Default threshold: `>= 0.40`.

Scenario overrides: bookshelf may require `>= 0.55`; living room may allow `>= 0.30` because room
context can be meaningful.

Debug visualization: foreground mask over RGB frame.

Reject reason: `low_foreground_ratio`.

### `visible_object_count`

Purpose: reject frames with too few semantic entities.

Inputs: instance segmentation map and visible object id list.

Formula:

```text
visible_object_count = count(objects with pixel_area >= min_object_pixels)
```

Default threshold: `>= 2` for sparse scenes, `>= 3` for medium/dense scenes.

Debug visualization: instance overlay with object ids.

Reject reason: `low_visible_object_count`.

### `dominant_object_area_ratio`

Purpose: reject frames where one object occupies too much of the image and removes scene context.

Inputs: instance segmentation map.

Formula:

```text
dominant_object_area_ratio = max_instance_pixel_count / valid_pixels
```

Default threshold: `<= 0.70`.

Debug visualization: highlight largest instance and print area ratio.

Reject reason: `dominant_object_too_large`.

### `semantic_entropy`

Purpose: reject visually poor frames with too little semantic variety.

Inputs: semantic segmentation map.

Formula:

```text
semantic_entropy = -sum_c p(c) * log(p(c))
```

Default threshold: pilot calibrated per scenario. Use only valid pixels and ignore unknown labels.

Debug visualization: semantic mask plus class histogram.

Reject reason: `low_semantic_entropy`.

### `anchor_visibility`

Purpose: ensure object-aware starts and anchor-following primitives remain meaningful.

Inputs: anchor object id, instance segmentation map, visible object id list.

Formula:

```text
anchor_area_ratio = anchor_pixels / valid_pixels
anchor_visible = min_anchor_area <= anchor_area_ratio <= max_anchor_area
```

Default threshold: anchor visible in at least `70%` of frames for anchor-maintaining primitives.

Debug visualization: anchor mask overlay and timeline.

Reject reason: `anchor_not_visible` or `anchor_area_out_of_bounds`.

## Clip Metric Dictionary

### `visual_delta`

Purpose: measure whether adjacent frames are smooth and whether the full clip changes enough to
avoid copy-forward solutions.

Composite definition:

```text
visual_delta = w_rgb * delta_rgb
             + w_depth * delta_depth
             + w_sem * delta_semantic
             + w_inst * delta_instance
             + w_surface * delta_surface
```

Initial implementation:

```text
visual_delta_approx = w_rgb * mean_abs_rgb_difference
                    + w_depth * depth_histogram_distance
                    + w_sem * (1 - semantic_mask_iou)
                    + w_obj * visible_object_set_distance
```

Later versions should replace approximations with surface-level change metrics using surface ids
and pixel-to-3D correspondence.

Debug visualization: adjacent visual-delta timeline and first-to-last comparison.

Reject reasons: `visual_delta_too_low`, `visual_delta_too_high`, `copy_forward_clip`.

### `pose_delta`

Purpose: ensure camera motion is smooth locally and significant globally.

Inputs: camera poses `T_wc_t`.

Formula:

```text
translation_delta_t = norm(position_t+1 - position_t)
rotation_delta_t = angle(relative_rotation_t)
```

Initial local bounds: translation `1-5 cm` per frame; rotation `1-3 degrees` per frame.

Initial global bounds: total displacement `>= 0.10-0.20 m` for translational primitives or
accumulated yaw/pitch `>= 8-15 degrees` for scan primitives.

Reject reasons: `pose_jump`, `pose_change_too_small`, `pose_acceleration_too_high`.

### `new_visibility_evidence`

Purpose: verify that the clip reveals new object or surface evidence.

Inputs: visible object ids, visible surface ids when available, segmentation maps.

Formula:

```text
new_object_ratio = pixels or ids visible after t=0 but not visible at t=0
new_surface_ratio = surface pixels visible after t=0 but not visible at t=0
```

Version 0 approximation: visible object set change and semantic mask change.

Version 1 requirement: object instance coverage and surface coverage.

Reject reason: `no_new_visibility_evidence`.

## Coverage Metric Versions

Coverage requirements are versioned so the implementation can improve without pretending early
proxies are final.

| Version | Required coverage evidence |
|---|---|
| V0 approximation | Visible object timelines, semantic entropy, pose coverage, first-to-last image difference. |
| V1 required | Object instance coverage, visible surface coverage, viewing distance distribution, occlusion reveal count. |
| V2 preferred | Surface point revisit count, view-angle distribution per surface, pixel-to-3D correspondence-based coverage. |

## Sequence Acceptance

A video sequence must pass:

```text
A(tau) =
  C_occ
  and C_phys
  and C_frame_content
  and C_anchor
  and C_local_continuity
  and C_global_change
  and C_new_evidence
```

Each rejected sequence must store one or more rejection reason codes. The preview viewer should
show the failing metric values next to RGB/depth/segmentation contact sheets so an engineer can see
whether the metric matches the visual failure.
