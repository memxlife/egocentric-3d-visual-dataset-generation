# Trajectory And Sequence Design

## Role In The Dataset

Each accepted static scene should produce many short egocentric clips. A clip starts from a valid,
meaningful camera pose and follows a smooth physically plausible trajectory through free space.

The key tension is:

```text
adjacent frames should change smoothly
but the full clip should show meaningful spatial change
```

## Sequence Representation

One clip is:

```text
tau = [(I_0, T_0), (I_1, T_1), ..., (I_H, T_H)]
```

The relative camera motion is:

```text
delta_T_t = inverse(T_t) * T_t+1
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
4. Add small angular perturbation so the anchor is not always centered.
5. Reject the start if visual content is weak.

The selected anchor must be stored in sequence metadata.

## Free-Space Constraints

The camera has clearance radius `r`; it is not a zero-volume point.

Every pose must satisfy:

```text
camera_center(T_t) in free_space(r)
```

Every swept transition must also be valid:

```text
camera_center(interpolate(T_t, T_t+1, s)) in free_space(r), for all s in [0, 1]
```

The rendered depth map should also satisfy a near-plane safety condition:

```text
minimum_valid_depth > d_min
```

## Motion Plausibility

Pilot motion ranges:

| Quantity | Initial value |
|---|---:|
| per-frame translation | 1-5 cm |
| per-frame rotation | 1-3 degrees |
| clip length | 32-64 frames |

The trajectory should avoid:

- teleportation;
- jitter;
- impossible acceleration;
- abrupt orientation changes;
- camera clipping through geometry;
- near-plane collisions.

## Motion Primitive Library

Do not rely on purely random motion. Initial primitives:

- lateral shift around anchor;
- forward approach toward anchor;
- backward retreat from anchor;
- small orbit around object or object group;
- look-down scan over surface;
- look-up scan from surface to object;
- left-right scan across multiple objects;
- peek-around-occluder motion;
- diagonal lean motion;
- combined translation and yaw motion.

A complete child-like inspection trajectory may combine:

```text
overview -> approach -> pan/tilt -> lateral shift -> orbit -> retreat -> revisit
```

## Visual Content Checks

Each frame should contain meaningful visual content.

Per-frame checks:

- foreground ratio;
- minimum visible object count;
- maximum single-object area ratio;
- semantic entropy;
- anchor visibility.

Pilot thresholds:

| Requirement | Pilot value |
|---|---:|
| foreground ratio | 0.4 |
| minimum visible objects | 2 or 3 |
| maximum single-object area | 0.7 |
| anchor visibility ratio | 0.5 |

Thresholds must be calibrated per scenario family.

## Continuity And Change

Local continuity:

- adjacent visual change should be moderate;
- adjacent pose change should be bounded;
- acceleration should be smooth.

Global sequence change:

- final pose should differ from initial pose;
- final visual frame should differ from initial frame;
- the clip should not be solvable by copy-forward.

Accepted clips should satisfy:

```text
moderate local change at each step
significant accumulated change over the sequence
```

## Sequence Acceptance Function

A sequence is accepted only if:

```text
A(tau) =
  C_occ
  and C_phys
  and C_fg
  and C_obj
  and C_balance
  and C_div
  and C_anchor
  and C_cont
  and C_change
```

where:

- `C_occ` checks occupancy and swept-path validity;
- `C_phys` checks plausible camera motion;
- `C_fg` checks foreground content;
- `C_obj` checks visible object count;
- `C_balance` checks object-area balance;
- `C_div` checks semantic diversity;
- `C_anchor` checks anchor visibility;
- `C_cont` checks local continuity;
- `C_change` checks sequence-level spatial and visual change.
