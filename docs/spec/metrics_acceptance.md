# Metrics And Acceptance

## Top-Level Dataset Metrics

The dataset is judged by four top-level metrics:

| Metric | What it measures |
|---|---|
| generation speed | Accepted frames per second and stage timing. |
| realism | Physical, geometric, semantic, and visual plausibility. |
| per-scenario comprehensiveness | Whether each scenario and sequence covers required content and viewpoints. |
| cross-scenario diversity | Whether the dataset covers scenario families, layouts, objects, appearances, states, and trajectory types. |

## Static Scene Acceptance

A static scene must pass:

```text
C_scene(z) =
  C_semantic_complete
  and C_physical
  and C_visual_rich
  and C_free_space
  and C_appearance_diverse
```

### Semantic Completeness

The scene must contain all required categories for its scenario family.

Examples:

- desk: desk or table, display, input device;
- kitchen: counter, storage, dishware or appliance;
- bookshelf: shelf and repeated shelf objects.

### Physical Plausibility

Reject if:

- objects float;
- objects interpenetrate severely;
- support relations are invalid;
- scale is implausible;
- camera-valid free space is empty.

### Visual Richness

Render low-resolution probe views and compute whether meaningful content is visible. A static scene
with valid geometry but no useful viewpoints should be rejected before trajectory generation.

### Free-Space Availability

The scene must have enough camera-valid free space for object-aware starts and short smooth
trajectories.

### Appearance Diversity

The scene should vary materials, colors, and textures enough to avoid one-note visual content.

## Sequence Acceptance

A video sequence must pass:

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

### Occupancy Validity

- every camera center is in free space;
- swept path between adjacent poses stays in free space;
- near-plane depth is above the minimum safety threshold.

### Physical Plausibility

- per-frame translation is bounded;
- per-frame rotation is bounded;
- acceleration and angular acceleration are smooth;
- no teleportation or jitter.

### Visual Content

Per-frame visual-content metrics:

- foreground ratio;
- visible object count;
- maximum single-object area ratio;
- semantic entropy;
- anchor visibility.

Pilot thresholds:

| Metric | Initial value |
|---|---:|
| foreground ratio | 0.4 |
| visible objects | 2 or 3 |
| max single-object area | 0.7 |
| anchor visibility ratio | 0.5 |

### Local Continuity

Adjacent frames should have moderate visual change:

```text
d_min_local <= visual_delta(I_t, I_t+1) <= d_max_local
```

Adjacent pose changes should also be bounded.

### Global Spatial Change

The final pose and visual frame should differ meaningfully from the initial pose and frame:

```text
pose_delta(T_0, T_H) >= Gamma_T
visual_delta(I_0, I_H) >= Gamma_I
```

This prevents copy-forward clips.

## Coverage Metrics

Sequence and scene coverage should eventually include:

- percentage of object instances observed at least once;
- percentage of visible surface area observed at least once;
- average number of views per observed surface point;
- viewing angle distribution per surface;
- viewing distance distribution per surface;
- occlusion reveal count;
- revisit count;
- close-up coverage ratio;
- global overview coverage ratio.

The first implementation may approximate these with visible object timelines, pose coverage, and
image-space metrics. The preferred implementation should use pixel-to-3D correspondence and surface
ids.
