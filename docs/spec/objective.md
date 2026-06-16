# Objective

## Purpose

The dataset trains models that learn visual-spatial dynamics from egocentric camera motion. The
model observes a visual stream from a moving camera and uses known camera motion to predict future
visual observations or infer persistent three-dimensional semantic structure.

Version 1 isolates one core learning problem: how a model learns persistent 3D semantic structure
from egocentric visual changes caused purely by camera motion. By keeping the world static, the
dataset removes confounding factors from object dynamics and contact physics. Therefore, when the
visual stream changes, the only valid explanation is the camera's changing viewpoint with respect
to a persistent scene.

The first-stage problem is:

```text
static 3D indoor world + moving egocentric camera -> spatially grounded visual sequence
```

No object manipulation, object motion, physical interaction, or task execution is required in
Version 1.

The central research claim is:

```text
Given past egocentric observations and known camera motion,
a model should learn to predict future visual observations
and infer stable 3D semantic structure in a static indoor environment.
```

## Generative Model

Each static world is:

```text
z = (G, O, M, L)
```

where:

- `G` is room geometry and layout;
- `O` is object set, object geometry, and object pose;
- `M` is material and texture assignment;
- `L` is lighting.

At frame `t`, the camera pose is:

```text
T_t in SE(3)
```

The rendered observation is:

```text
I_t = R(z, T_t)
```

The world is static during one clip:

```text
z_t = z for all t
```

All visual change should be caused by camera motion.

## Learning Target

The main Version 1 training problem is:

```text
(I_0:k, delta_T_k:H-1) -> I_k+1:H
```

That means the model receives past visual context and future spatial transformations, then predicts
future visual frames.

A richer spatial-learning target is:

```text
f(I_<=t, camera_poses, intrinsics) -> estimated 3D semantic scene representation
```

The ground-truth world model is not model input. It is retained for supervision, filtering,
diagnosis, and evaluation.

## Input And Supervision Separation

Model input should stay close to sensory experience:

- RGB;
- optional depth;
- camera pose or relative motion;
- camera intrinsics.

Ground-truth supervision may include:

- depth;
- normals;
- semantic segmentation;
- instance segmentation;
- pixel-to-3D correspondence;
- visible object and surface identifiers;
- scene and object metadata.

This separation keeps the learning problem meaningful while making the dataset auditable.

## Four Dataset Requirements

The dataset fails if it fails any of the four top-level requirements:

| Requirement | Meaning |
|---|---|
| generation speed | Accepted clips can be generated fast enough for repeated research loops. |
| realism | Static scenes obey real-world geometry, scale, support, object-state, lighting, and navigability rules. |
| per-scenario comprehensiveness | Clips cover required viewpoints, motions, objects, and visibility events inside each scenario. |
| cross-scenario diversity | The full dataset covers scenario families, layouts, objects, appearances, states, and trajectory types. |

## Claim Boundary

Version 1 is successful if it produces useful motion-conditioned visual transformations from static
indoor worlds. It does not need manipulation or real-robot deployment evidence yet.

The dataset should not be used to claim that a model understands object dynamics, contact physics,
robot control, or task execution. Those claims require later dataset versions with moving objects,
actions, and real or simulated interaction evidence.
