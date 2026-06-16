# Egocentric Visual Scanning Dataset Specification

This specification defines a synthetic egocentric visual scanning dataset for learning
motion-conditioned visual prediction and persistent 3D semantic spatial structure.

Version 1 isolates a deliberately constrained problem: the world is static and only the camera
moves. This removes object dynamics, manipulation, contact physics, and task execution from the
first dataset version. As a result, every visual change in a sequence should be explainable by the
camera's changing viewpoint over a persistent 3D indoor scene.

The dataset is organized around accepted static scenes and short egocentric camera-motion clips. A
static scene defines the layout, objects, support relations, materials, lighting, and valid camera
free space. A clip starts from a meaningful object-aware viewpoint and follows a smooth physically
valid trajectory that produces locally continuous frames and globally meaningful spatial change.

The purpose of this specification is not only to describe what files are written. It defines the
generation constraints, visual-content requirements, trajectory mechanics, acceptance metrics,
calibration procedure, and claim boundary needed to produce a useful research dataset.

Every quantitative setting in this specification must state why that value is used and what failure
appears if the value is too low or too high. A number without justification is only a placeholder,
not an accepted dataset requirement.

## Phase 1 Prototype And Version 1 Dataset

The project has two scopes that must not be confused.

| Scope | Purpose | Success condition |
|---|---|---|
| Phase 1 prototype | Validate the end-to-end generation, validation, rejection, preview, and storage pipeline. | The remote pipeline can generate short clips, reject bad candidates, write the schema, and make failures visible in a preview. |
| Version 1 dataset | Produce a calibrated multi-scenario dataset for learning motion-conditioned egocentric prediction and 3D semantic structure. | The dataset contains physically grounded static worlds and valid, visually meaningful, smooth, spatially transformative clips with controlled generalization splits. |

Phase 1 may use a small number of desk or ProcTHOR scenes. Version 1 targets multiple scenario
families, many accepted static scenes, many object-aware starts per scene, multiple motion
primitives per start, RGB/depth/segmentation/pose/intrinsics/correspondence annotations, calibrated
acceptance metrics, and held-out evaluation splits.

## Document Map

Read the specification documents in this order:

1. [Objective And Claim Boundary](objective.md)  
   Defines the research purpose, core learning target, input/supervision separation, and claim
   boundary.

2. [Dataset Units And Hierarchy](dataset_units_and_hierarchy.md)  
   Defines the dataset hierarchy from scenario families to scenes, starts, clips, frames, and
   annotations.

3. [Static Scene Design](static_scene_design.md)  
   Defines scenario grammar, layout templates, object categories, support rules, object states,
   material distributions, clutter regimes, and rejected examples.

4. [Quantitative Requirements](quantitative_requirements.md)  
   Defines the default numeric contract for scene probes, frame gates, clip gates, visual delta,
   dataset coverage, throughput, and pilot calibration.

5. [Visual Content Requirements](visual_content_requirements.md)  
   Defines frame-level, clip-level, and dataset-level visual-content requirements.

6. [Trajectory And Sequence Design](trajectory_sequence_design.md)  
   Defines object-aware start sampling, free-space construction, motion primitives, smoothness
   constraints, and spatial-change requirements.

7. [Metrics And Acceptance](metrics_acceptance.md)  
   Defines executable scene, frame, clip, and dataset metrics with inputs, formulas, thresholds,
   debug artifacts, and rejection reason codes.

8. [Dataset Schema](dataset_schema.md)  
   Defines directory layout, coordinate conventions, depth encoding, segmentation IDs, metadata,
   and seed/version policy.

9. [Splits And Generalization](splits_and_generalization.md)  
   Defines train/validation/test split policies and the generalization claims each split supports.

10. [Generation Pipeline](generation_pipeline.md)  
   Defines the abstract gated generation process from scenario sampling to post-write validation.

11. [Pilot Calibration](pilot_calibration.md)  
    Defines how thresholds are calibrated before scaling.

Implementation status and machine-specific commands live outside the specification:

- [Implementation Roadmap](../implementation/roadmap.md)
- [Remote 5090 Runbook](../runbook/remote_5090.md)
- [Smoke Tests](../runbook/smoke_tests.md)
- [Preview Generation](../runbook/preview_generation.md)

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

These are target orders of magnitude, not frozen constants. They must be revised after pilot
calibration reports acceptance rates, rejection reasons, throughput, and visual quality.

## Current Claim Boundary

This spec does not claim real-robot transfer yet. It claims that a useful Version 1 dataset must
produce static, physically grounded, semantically meaningful indoor worlds and short egocentric
camera-motion clips that are valid, visually meaningful, smooth frame-to-frame, and spatially
transformative across the sequence.
