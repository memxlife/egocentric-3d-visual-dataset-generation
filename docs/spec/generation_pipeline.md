# Generation Pipeline

## Overview

Generation is a gated process. The system should reject bad static scenes before rendering expensive
clips and reject bad candidate trajectories before final-resolution rendering.

## Static Scene Pipeline

1. Sample scenario family.
2. Sample layout template.
3. Sample clutter level.
4. Sample required object categories.
5. Sample optional and distractor categories.
6. Sample object mesh or procedural geometry.
7. Sample object scale, shape variant, and pose.
8. Place large furniture and support structures.
9. Place required objects.
10. Place optional objects.
11. Place clutter objects.
12. Resolve collisions and support constraints.
13. Assign material, texture, color, and surface properties.
14. Assign static object states.
15. Generate occupancy field.
16. Generate free-space field.
17. Render low-resolution probe views.
18. Score semantic completeness, physical plausibility, visual richness, free-space, and appearance
    diversity.
19. Accept or reject static scene.
20. Pass accepted scene to trajectory generation.

## Trajectory Pipeline

1. Select accepted static scene.
2. Build or load occupancy and free-space representation.
3. Select semantic anchor.
4. Sample valid object-aware starting pose.
5. Sample a smooth motion primitive or primitive composition.
6. Check free-space poses and swept path.
7. Render cheap validation preview.
8. Compute visual-content metrics.
9. Compute local continuity metrics.
10. Compute global sequence-change metrics.
11. Accept or reject candidate sequence.
12. Final-render accepted sequence.
13. Store frames, pose, intrinsics, annotations, metadata, and quality scores.

## Two-Stage Rendering

Use cheap validation renders before final rendering:

```text
candidate scene/trajectory
  -> low-resolution validation render
  -> acceptance scores
  -> final-resolution render only if accepted
```

This prevents final rendering from being dominated by invalid, empty, or redundant clips.

## Remote Execution Rule

All dataset generation, simulator tests, and preview generation should run on the remote RTX 5090
server. Local runs are for source editing and static checks only.

Default GPU reservation:

```text
CUDA_VISIBLE_DEVICES=4,5,6,7
```

## Scale Ladder

Use this ladder:

```text
remote schema smoke: 3-10 episodes
real simulator smoke: 1-5 episodes
micro scene/trajectory pilot: 100-1,000 clips
scenario pilot: 100-500 candidate static scenes
accepted scene pilot: 1,000 scenes
first production target: 3,500 accepted scenes
initial research scale: 10M+ frames
```

Do not scale until the current level passes acceptance metrics and visual inspection.
