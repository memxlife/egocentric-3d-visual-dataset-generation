# Trajectory And Sequence Design

## Role In The Dataset

Each accepted static scene should produce many short egocentric clips. A clip starts from a valid,
meaningful camera pose and follows a smooth physically plausible trajectory through free space.

The key tension is:

```text
adjacent frames should change smoothly
but the full clip should show meaningful spatial change
```

Version 1 does not model full head, eye, hand, or body dynamics. The camera is an abstract
egocentric sensor. Motion is plausible if it is collision-free, smooth, bounded in velocity and
acceleration, and produces viewpoint changes consistent with a person visually inspecting a nearby
static scene.

## Sequence Representation

One clip is:

```text
tau = [(I_0, T_wc_0), (I_1, T_wc_1), ..., (I_H, T_wc_H)]
```

where `T_wc_t` maps camera coordinates to world coordinates at frame `t`.

The relative camera motion is:

```text
delta_T_t = inverse(T_wc_t) * T_wc_(t+1)
```

Version 1 clips are short:

```text
H = 32-64 frames for pilot clips
```

Longer scans may be used later, but the first production unit is many short useful motion
transformations, not a few long random videos.

## Object-Aware Starting Viewpoints

Starting poses must be valid and meaningful. The generator should not sample uniformly over empty
space.

Process:

1. Select a semantic anchor, such as a monitor, keyboard, sink, counter workspace, shelf section, or
   object cluster.
2. Sample a camera center near the anchor but in free space.
3. Orient the camera roughly toward the anchor.
4. Add angular perturbation so the anchor is not always centered.
5. Render a low-resolution start probe.
6. Reject the start if visual content is weak.

The selected anchor and start scores must be stored in sequence metadata.

### Start Parameter Ranges

Initial ranges:

| Scenario | camera height | anchor distance | pitch | yaw perturbation | roll | anchor area |
|---|---:|---:|---:|---:|---:|---:|
| desk | 0.9-1.5 m | 0.35-1.2 m | -35 to +20 deg | -25 to +25 deg | -3 to +3 deg | 0.03-0.55 |
| kitchen counter | 1.0-1.7 m | 0.4-1.5 m | -35 to +15 deg | -30 to +30 deg | -3 to +3 deg | 0.03-0.60 |
| bookshelf/storage | 0.6-1.8 m | 0.4-1.5 m | -20 to +30 deg | -30 to +30 deg | -3 to +3 deg | 0.03-0.60 |
| living room table/sofa | 0.7-1.7 m | 0.5-2.0 m | -30 to +20 deg | -35 to +35 deg | -3 to +3 deg | 0.02-0.55 |
| bathroom vanity | 0.9-1.6 m | 0.35-1.2 m | -35 to +20 deg | -25 to +25 deg | -3 to +3 deg | 0.03-0.55 |

The pilot must calibrate these ranges. Too-close starts create single-object close-ups. Too-far
starts become room-level views with weak object detail.

## Free-Space Construction

The camera has clearance radius `r`; it is not a zero-volume point.

Define:

```text
free_space(r) = positions whose sphere of radius r does not intersect occupied geometry
```

There are three distinct spaces:

| Space | Definition | Failure it detects |
|---|---|---|
| geometric free space | Collision-free camera-center positions. | Camera center inside furniture, wall, object, or support surface. |
| view-valid space | Collision-free positions from which useful visual content is visible. | Blank wall, empty floor, degenerate close-up. |
| trajectory-valid space | Continuous paths whose swept volume is collision-free and visually useful. | Valid start with no valid smooth motion. |

Every pose must satisfy:

```text
camera_center(T_wc_t) in free_space(r)
```

Every swept transition must also be valid:

```text
camera_center(interpolate(T_wc_t, T_wc_(t+1), s)) in free_space(r), for all s in [0, 1]
```

The rendered depth map should also satisfy:

```text
minimum_valid_depth > d_min
```

## Motion Plausibility

Initial motion ranges:

| Quantity | Initial value |
|---|---:|
| clip length | 32-64 frames |
| per-frame translation | 1-5 cm |
| per-frame rotation | 1-3 degrees |
| max linear acceleration | 0.03 m/frame^2 pass, 0.03-0.05 review |
| max angular acceleration | 2 deg/frame^2 pass, 2-4 review |
| minimum total displacement | 0.12 m for translational primitives |
| minimum accumulated yaw/pitch | 10 degrees for scan primitives |

The trajectory should avoid:

- teleportation;
- jitter;
- impossible acceleration;
- abrupt orientation changes;
- camera clipping through geometry;
- near-plane collisions.

These values are starting hypotheses. Their justification and too-low/too-high failure modes are
defined in [Quantitative Requirements](quantitative_requirements.md).

## Motion Primitive Library

Do not rely on purely random motion. Each primitive must define anchor type, start condition,
translation path, rotation path, duration, parameters, validity constraints, expected visual effect,
and failure modes.

| Primitive | Purpose | Key parameters | Acceptance |
|---|---|---|---|
| lateral shift around anchor | Produce parallax while keeping anchor visible. | duration 16-48 frames; displacement 0.10-0.40 m; yaw compensation toward anchor. | Anchor visible in at least 70 percent of frames; total translation >= 0.12 m; neighboring object/background set changes. |
| forward approach | Increase detail and depth change. | approach distance 0.10-0.50 m; max dominant object area 0.70. | Depth distribution changes; anchor does not consume whole frame; no near-plane collision. |
| backward retreat | Move from detail to context. | retreat distance 0.10-0.60 m; orientation toward anchor. | More context or additional objects become visible. |
| small orbit | Reveal side geometry around object or cluster. | arc 10-45 degrees; radius 0.35-1.5 m. | Visible surface/object set changes and anchor remains interpretable. |
| look-down scan | Inspect support surface objects. | pitch change 8-25 degrees; small translation optional. | Surface and objects remain visible; no floor-only frames. |
| look-up scan | Move from surface to vertical object/context. | pitch change 8-25 degrees. | Required anchor or neighboring context visible at start and end. |
| left-right scan | Traverse multiple objects on a surface or shelf. | yaw change 10-40 degrees; optional lateral motion. | Visible object set changes without abrupt motion. |
| peek-around-occluder | Create reveal events. | lateral/diagonal displacement 0.10-0.35 m. | At least one object or surface becomes newly visible. |
| diagonal lean | Combine parallax and distance change. | diagonal displacement 0.10-0.40 m. | Smooth pose path and nontrivial visual change. |
| combined translation and yaw | Natural inspection motion. | bounded translation plus 5-30 degrees yaw. | Passes continuity and global-change metrics. |

Reject any primitive if:

- anchor fills more than 70 percent of most frames;
- final frame is visually too similar to initial frame;
- motion clips through table, wall, chair, fixture, or object;
- visual content drops below frame-level thresholds for too many frames.

Primitive compositions may use:

```text
overview -> approach -> pan/tilt -> lateral shift -> orbit -> retreat -> revisit
```

Compositions must still pass per-frame, adjacent-frame, and full-clip metrics.

## Sequence-Level Spatial Change

A good clip should not merely shift pixels. It should reveal new spatial information.

Measure meaningful spatial change with:

- pose displacement;
- rotation displacement;
- RGB or perceptual image change;
- depth distribution change;
- semantic mask change;
- instance mask change;
- newly visible object pixels;
- newly visible surface pixels;
- change in visible object set;
- occlusion reveal events;
- parallax magnitude.

The first implementation may approximate these with RGB frame difference, depth histogram
difference, semantic mask difference, and visible object set difference. Later versions should use
surface IDs and pixel-to-3D correspondence.

## Sequence Acceptance Function

A sequence is accepted only if:

```text
A(tau) =
  C_occ
  and C_phys
  and C_frame_content
  and C_anchor
  and C_local_continuity
  and C_global_change
```

where:

- `C_occ` checks occupancy, free-space, and swept-path validity;
- `C_phys` checks plausible camera motion;
- `C_frame_content` checks foreground, object count, dominant-object balance, semantic diversity,
  depth validity, and segmentation validity;
- `C_anchor` checks anchor visibility and anchor area bounds;
- `C_local_continuity` checks adjacent pose and visual deltas;
- `C_global_change` checks sequence-level spatial and visual transformation.
