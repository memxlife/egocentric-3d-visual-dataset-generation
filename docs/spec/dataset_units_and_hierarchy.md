# Dataset Units And Hierarchy

## Design Goal

The dataset must be organized so that a researcher can ask what varies at each level and what stays
fixed. This prevents two common failures: treating many clips from one static scene as many
independent worlds, and treating many frames from one clip as independent images.

## Unit Definitions

| Unit | Definition | What varies inside it | What stays fixed |
|---|---|---|---|
| dataset | Complete collection used for training or evaluation. | Scenario families, scenes, trajectories, appearances, splits. | Dataset version and schema version. |
| scenario family | Semantic environment type such as desk or kitchen counter. | Layout templates, object sets, materials, lighting. | High-level functional meaning. |
| static scene | One persistent 3D world. | Probe viewpoints and generated clips. | Layout, objects, object states, materials, lighting. |
| start viewpoint | One valid object-aware initial camera pose. | Motion primitives launched from the start. | Anchor object or surface and starting pose. |
| clip | One short camera-motion sequence. | Frames over time. | Static scene, start, primitive parameters. |
| frame | One rendered observation at one camera pose. | Annotation channels. | Timestamp and camera pose. |

The static scene is the main world unit. The clip is the main learning unit. The frame is not a
standalone training example unless the experiment explicitly ignores temporal structure.

## Version 1 Hierarchy

```text
scenario_family
  -> layout_template
    -> accepted_static_scene
      -> semantic_anchor
        -> object_aware_start
          -> motion_primitive_or_composition
            -> accepted_clip
              -> frame_annotations
```

This hierarchy defines where diversity should be measured. Cross-scenario diversity is not the same
as many random camera paths. Per-scenario comprehensiveness is not the same as many frames. A good
dataset varies both world content and camera behavior while preserving physically and semantically
valid structure.

## Phase 1 Prototype Unit

Phase 1 should use the same hierarchy but at small scale:

```text
1-2 scenario families
  5-10 procedural scenes
    8-16 object-aware starts per scene
      1-2 clips per start
        32 frames per clip
```

The Phase 1 success condition is not dataset size. It is whether each unit can be generated,
validated, rejected with a reason, written to disk, and inspected in the preview viewer.

## Version 1 Dataset Unit

Version 1 should scale only after the Phase 1 unit passes. A major scenario family target is:

```text
1,000 accepted scenes
  x 128 starting viewpoints per scene
  x 4 clips per starting viewpoint
  x 32 frames per clip
```

These numbers define the intended coverage density. The final production numbers should be based on
pilot acceptance rates, throughput, storage budget, and the diversity needed by held-out evaluation
splits.

## Required Metadata At Each Level

Every level must have enough metadata to explain why it exists and how it was generated.

| Level | Required metadata |
|---|---|
| scenario family | Required structures, allowed layout templates, object taxonomy, foreground classes, split policy. |
| static scene | Scene seed, layout template, object list, support relations, materials, lighting, free-space summary, acceptance scores. |
| start viewpoint | Anchor id, anchor category, camera pose, distance to anchor, anchor image area, start rejection checks. |
| clip | Primitive type, primitive parameters, pose sequence, visual-content scores, continuity scores, global-change scores, rejection reason. |
| frame | RGB/depth/segmentation paths, pose, intrinsics, visible objects, valid depth mask, timestamp. |

## Failure Modes Prevented

This hierarchy prevents:

- counting many correlated frames as many independent scenes;
- training on clips whose static scene cannot be regenerated;
- losing the anchor and primitive that explain why a clip was sampled;
- mixing prototype-scale smoke runs with Version 1 dataset claims;
- reporting dataset size without reporting scene, start, primitive, and split coverage.
