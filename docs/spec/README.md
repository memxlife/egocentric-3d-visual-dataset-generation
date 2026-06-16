# Egocentric Visual Scanning Dataset Specification v0.1

This specification defines the first version of the static egocentric visual scanning dataset. The
dataset is designed to train visual models that predict future egocentric visual streams and infer
three-dimensional semantic spatial structure from visual history and known camera motion.

Version 1 has one core restriction:

```text
the world is static; only the camera moves
```

The dataset should therefore isolate visual-spatial learning from object manipulation, object
motion, and robotics contact dynamics.

## Document Map

Read the documents in this order:

1. [Objective](objective.md)  
   Defines the research purpose, model input, supervision, and claim boundary.

2. [Static Scene Design](static_scene_design.md)  
   Defines scenario families, scene variety, object/layout/material requirements, and static scene
   acceptance checks.

3. [Trajectory And Sequence Design](trajectory_sequence_design.md)  
   Defines object-aware starts, free-space motion, smooth short clips, visual-content checks, local
   continuity, and sequence-level spatial change.

4. [Dataset Schema](dataset_schema.md)  
   Defines the directory layout, scene metadata, episode metadata, frame fields, camera pose,
   intrinsics, and required annotations.

5. [Metrics And Acceptance](metrics_acceptance.md)  
   Defines the four top-level dataset metrics and the concrete scene-level and sequence-level
   acceptance functions.

6. [Generation Pipeline](generation_pipeline.md)  
   Defines the gated generation process from scenario sampling to final accepted clips.

7. [Pilot Calibration](pilot_calibration.md)  
   Defines how thresholds are calibrated before scaling.

8. [Implementation Roadmap](implementation_roadmap.md)  
   Maps the spec to the current toolchain and the next engineering tasks.

## Conceptual Hierarchy

```text
dataset purpose
  -> scenario families
    -> many accepted static scenes per family
      -> many object-aware starting viewpoints per static scene
        -> many short smooth video clips per starting viewpoint
          -> frame-level RGB/depth/segmentation/pose/intrinsics/correspondence
```

## Version 1 Target

The first production target is:

```text
3,500 accepted static scenes
  desk: 1,000
  kitchen counter: 1,000
  bookshelf/storage: 500
  living room table/sofa area: 500
  bathroom vanity: 500
```

Each accepted static scene should then generate many short egocentric clips. The initial target for
major scenario families is:

```text
1,000 scenes
  x 128 starting viewpoints per scene
  x 4 clips per starting viewpoint
  x 32 frames per clip
  = 16,384,000 frames per major family
```

These numbers are starting targets. The actual thresholds and acceptance rates must be calibrated
with pilot batches before large-scale generation.

## Current Claim Boundary

This spec does not claim real-robot transfer yet. It claims that a useful Version 1 dataset must
produce static, physically grounded, semantically meaningful indoor worlds and short egocentric
camera-motion clips that are valid, visually meaningful, smooth frame-to-frame, and spatially
transformative across the sequence.
