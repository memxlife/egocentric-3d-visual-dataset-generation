# Implementation Roadmap

## Current State

The current toolchain can:

- run remotely on the RTX 5090 server;
- generate mock episodes;
- run AI2-THOR CloudRendering;
- load ProcTHOR-10K through `prior`;
- render RGB, depth, semantic segmentation, instance segmentation, pose, action, and visible objects;
- write manifests and episode folders;
- compute initial four metric payloads;
- generate a static HTML preview with contact sheets and frame metadata.

Current limitation:

- trajectories are still weak and not object-aware;
- static scene acceptance is not yet implemented;
- camera intrinsics and quaternion pose are not fully stored;
- normals, point3D maps, and surface ids are not exported;
- visual-content metrics are only approximate;
- ProcTHOR scene selection does not yet target scenario families such as desk or kitchen.

## Next Engineering Tasks

### 1. Schema Upgrade

Add:

- camera intrinsics file;
- quaternion orientation;
- relative motion `delta_T`;
- selected anchor metadata;
- static scene validation metadata;
- sequence acceptance metadata.

### 2. Visual-Content Metrics

Implement:

- visible object count;
- foreground ratio from semantic segmentation;
- maximum single-object area from instance segmentation;
- semantic entropy;
- first-to-last image delta;
- adjacent image delta;
- pose continuity;
- first-to-last pose change.

### 3. Object-Aware Starts

Use AI2-THOR/ProcTHOR metadata to:

- find visible semantic anchors;
- sample or choose reachable camera poses near anchors;
- orient camera toward anchor;
- reject starts with weak visual content.

### 4. Smooth Motion Primitive Library

Implement primitive policies:

- lateral shift;
- approach;
- retreat;
- small orbit;
- look-down scan;
- look-up scan;
- left-right scan;
- diagonal lean;
- combined translation and yaw.

### 5. Static Scene Acceptance Layer

Implement static scene probe views and scores:

- semantic completeness;
- physical plausibility;
- visual richness;
- free-space availability;
- appearance diversity.

For current ProcTHOR integration, start with metadata and probe-view approximations, then improve
with explicit occupancy/free-space geometry.

### 6. Viewer Upgrade

Extend `egodata preview` to show:

- accepted and rejected examples;
- rejection reasons;
- visual-content metrics per frame;
- pose path;
- action or primitive timeline;
- anchor visibility timeline;
- frame-to-frame visual delta;
- first-to-last visual delta.

### 7. Scenario Configs

Add scenario-family config files:

- `computer_desk.yaml`;
- `kitchen_counter.yaml`;
- `bookshelf_storage.yaml`;
- `living_room_table.yaml`;
- `bathroom_vanity.yaml`.

Each file should encode required categories, optional categories, clutter levels, layout variants,
static states, visual-content foreground classes, and pilot thresholds.

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
