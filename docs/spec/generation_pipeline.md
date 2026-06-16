# Generation Pipeline

## Overview

Generation is a gated process. The system should reject bad static scenes before trajectory
sampling, reject bad candidate trajectories before final-resolution rendering, and run post-write
validation after outputs are stored.

The pipeline has three validation layers:

| Layer | When it runs | What it prevents |
|---|---|---|
| scene validation | Before trajectory sampling. | Bad worlds, missing required content, invalid support, no useful viewpoints. |
| candidate trajectory validation | Before final rendering. | Collision, weak visual content, jitter, copy-forward clips. |
| post-render dataset validation | After final outputs are written. | Broken files, missing metadata, schema violations, corrupt annotations. |

## End-To-End Pipeline

1. Sample scenario family.
2. Sample layout template.
3. Instantiate required structures and support surfaces.
4. Place required objects under support and co-occurrence constraints.
5. Add optional and distractor objects.
6. Assign material, texture, color, state, and lighting.
7. Build occupancy and free-space fields.
8. Render low-resolution probe views.
9. Apply static scene acceptance.
10. Select semantic anchors.
11. Sample object-aware starts.
12. Generate candidate motion primitives.
13. Validate free-space poses and swept path.
14. Render low-resolution preview.
15. Compute visual-content, continuity, and global-change metrics.
16. Accept or reject candidate sequence.
17. Final-render accepted sequence.
18. Write frames, annotations, pose, intrinsics, metadata, and quality scores.
19. Run post-write integrity validation.
20. Add accepted episode to manifests and preview dashboard.

## Two-Stage Rendering

Use cheap validation renders before final rendering:

```text
candidate scene/trajectory
  -> low-resolution validation render
  -> acceptance scores
  -> final-resolution render only if accepted
```

This prevents final rendering from being dominated by invalid, empty, redundant, or physically
impossible clips.

## Rejection Metadata

Every rejected candidate should keep enough information to debug the rejection:

- static scene id;
- scenario family and layout template;
- anchor id and category;
- start parameters;
- primitive type and parameters;
- failed metric names;
- rejection reason codes;
- probe or preview frame paths when available.

Rejected examples are not training data, but they are critical calibration evidence.

## Scale Ladder

Use this ladder:

```text
schema smoke: 3-10 episodes
real simulator smoke: 1-5 episodes
micro scene/trajectory pilot: 100-1,000 clips
scenario pilot: 100-500 candidate static scenes
accepted scene pilot: 1,000 scenes
first production target: 3,500 accepted scenes
initial research scale: 10M+ frames
```

Do not scale until the current level passes acceptance metrics and visual inspection.
