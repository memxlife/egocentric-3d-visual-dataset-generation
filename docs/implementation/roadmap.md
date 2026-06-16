# Implementation Roadmap

## Current State

The current toolchain can:

- run on the remote RTX 5090 server;
- generate mock episodes;
- run AI2-THOR CloudRendering;
- load ProcTHOR-10K through `prior`;
- render RGB, depth, semantic segmentation, instance segmentation, pose, action, and visible
  objects;
- write manifests and episode folders;
- compute initial four metric payloads;
- generate a static HTML preview with contact sheets and frame metadata;
- generate a Codex/browser-friendly HTML viewer for the Markdown specification.

Current limitations:

- trajectories are still weak and not object-aware;
- static scene acceptance is not yet implemented;
- camera intrinsics and quaternion pose are not fully stored;
- normals, point3D maps, and surface ids are not exported;
- visual-content metrics are only approximate;
- ProcTHOR scene selection does not yet target scenario families such as desk or kitchen;
- preview does not yet show rejection reasons or metric timelines.

## Dependency Order

Implementation should proceed in this order:

```text
schema upgrade
  -> metric implementation
    -> object-aware starts
      -> primitive library
        -> static scene acceptance
          -> preview dashboard
            -> scenario configs
              -> pilot calibration
```

Schema and metric work comes first because later stages must write enough evidence to explain why
examples pass or fail.

## Milestone Gates

| Milestone | Goal | Pass condition |
|---|---|---|
| M0 remote mock schema smoke | Validate writer, manifests, and package wiring on the remote server without simulator cost. | Remote mock run writes episodes, manifests, trajectory table, and validation report. |
| M1 AI2-THOR smoke | Confirm remote CloudRendering and frame annotations. | One or more AI2-THOR episodes render RGB/depth/semantic/instance data and validate. |
| M2 ProcTHOR scene loading | Confirm procedural houses and metadata extraction. | ProcTHOR scene loads, renders, and writes visible object metadata. |
| M3 object-aware starts | Replace random starts with anchor-conditioned starts. | Starts look at meaningful objects or support surfaces and store anchor metadata. |
| M4 trajectory primitives | Replace random action streams with parameterized smooth primitives. | Each primitive produces bounded pose deltas and visible spatial change. |
| M5 low-res rejection dashboard | Inspect accepted and rejected candidates before final render. | Preview shows RGB/depth/segmentation, metric timelines, and rejection reasons. |
| M6 desk pilot | Calibrate one scenario family. | Desk pilot reports threshold table, acceptance rates, false accept/reject examples. |
| M7 multi-scenario pilot | Expand beyond desk. | At least three scenario families pass scene and trajectory calibration. |
| M8 first production generation | Produce Version 1-scale shard. | Accepted clips meet metrics, splits are written, and throughput is sufficient. |

## Immediate Next Run

The next useful remote run should not be larger. It should be more diagnostic:

```text
ProcTHOR object-aware start pilot
  5-10 procedural scenes
  8-16 candidate starts per scene
  1-2 short clips per start
  32 frames per clip
  preview accepted and rejected clips
```

Success means:

- starts look at meaningful objects or surfaces;
- clips satisfy local continuity and global change;
- rejection reasons are useful;
- preview makes failures obvious.
