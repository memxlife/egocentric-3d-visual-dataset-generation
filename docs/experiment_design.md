# Experiment Design

## Purpose

This document defines the tests that decide whether the dataset design is working. Each test must
produce numbers and inspectable examples. A large generation run is not useful until the small tests
explain why episodes pass or fail.

## Experiment 0: Remote Schema Smoke Test

Question:

Can the remote server write and validate the episode schema without a real simulator?

Setup:

- backend: `mock`;
- episodes: 3 to 10;
- frames per episode: 12 to 24;
- output: remote `${EGO5090_DATASET_ROOT}/scenario_smoke`.

Metrics:

- generated episodes;
- generated frames;
- validation failures;
- missing files;
- manifest completeness.

Pass condition:

- validator returns `valid: true`;
- every episode has `episode.json`, `trajectory.parquet`, RGB, depth, semantic, and instance files;
- action and pose columns exist in every trajectory table.

Fail condition:

- missing frame files;
- missing metadata fields;
- validator cannot explain failure reason.

Current status:

- not yet run on the remote server.
- previous local runs were useful only as code checks and are not research evidence.

## Experiment 1: Remote 5090 Environment Test

Question:

Can the remote server reproduce the same schema and run the generator in the target environment?

Setup:

- backend: `mock`;
- host: environment variable `EGO5090_HOST`;
- workdir: environment variable `EGO5090_WORKDIR`;
- dataset root: environment variable `EGO5090_DATASET_ROOT`;
- episodes: 10;
- frames per episode: 24.

Metrics:

- remote install success;
- generated episodes;
- generated frames;
- validation failures;
- wall time;
- output size.

Pass condition:

- remote validator returns `valid: true`;
- remote output contains the same required layout as local output;
- run command and environment variables are recorded.

Fail condition:

- install fails;
- output path is wrong;
- remote Python environment cannot import the package;
- generated files are incomplete.

Next action:

- run after server SSH target and remote paths are known.

## Experiment 2: ProcTHOR Minimal Desk Backend

Question:

Can the real fast simulator generate valid egocentric desk-exploration episodes with action, pose,
RGB-D, and object visibility?

Setup:

- backend: ProcTHOR / AI2-THOR;
- scenario family: `desk_exploration`;
- templates: start with 1 to 3 desk-like scene templates;
- policies: random scan, scripted active scan, target search;
- episodes: 100;
- frames per episode: 50;
- resolution: 256 x 256.

Stage evidence:

| Stage | Evidence | Pass condition |
|---|---|---|
| scene sampling | scene manifest and object list | desk support surface exists |
| object placement | object positions and categories | no severe interpenetration |
| policy rollout | action sequence and pose path | nonzero path length |
| rendering | frame files and example contact sheet | frames are nonblank |
| annotation | depth, segmentation, visible objects | labels exist for requested frames |
| validation | rejection reason histogram | failures are named and fixable |

Metrics:

- scene accept rate;
- episode accept rate;
- valid frames per second;
- action histogram;
- pose path length distribution;
- visible object category histogram;
- object disappearance and reappearance event rate.

Pass condition:

- at least 80 accepted episodes from 100 proposed episodes;
- every accepted episode has RGB, depth, pose, action, and visible object records;
- at least 30 percent of accepted episodes contain a disappear-reappear object event;
- valid frames per second is reported.

Fail condition:

- most rejected episodes share one fixable failure, such as no desk surface, broken labels, or stuck
  action;
- annotation is too incomplete to compute object permanence metrics;
- episodes are valid but contain almost no camera motion or occlusion.

## Experiment 2a: AI2-THOR Built-In Scene Backend Smoke

Question:

Can the `egodata generate` tool use a real AI2-THOR CloudRendering controller on the remote server?

Setup:

- backend: `ai2thor`;
- scenario card: `ai2thor_floorplan_smoke`;
- scene: `FloorPlan1`;
- episodes: 1;
- frames per episode: 8;
- resolution: 256 x 256;
- GPUs: `CUDA_VISIBLE_DEVICES=4,5,6,7`.

Metrics:

- AI2-THOR controller startup success;
- RGB/depth/semantic/instance file writing;
- action and pose recording;
- visible object category extraction;
- four metric gate payloads in episode manifest;
- valid frames per second.

Pass condition:

- remote validator returns `valid: true`;
- episode manifest includes all four metric groups;
- failed action count is zero or explained.

Current status:

- passed on the remote server with 1 episode, 8 frames, no rejections, no failed actions, and
  `valid_frames_per_second = 1.68`.
- stability smoke also passed on the remote server with 5 episodes, 100 frames, no rejections, and
  `valid_frames_per_second = 6.18`.

## Experiment 2b: ProcTHOR House Loading Smoke

Question:

Can the toolchain load a procedural ProcTHOR house through `prior`, pass it to AI2-THOR
CloudRendering, and write the same dataset layout?

Setup:

- backend: `procthor`;
- dataset: `procthor-10k`;
- split: `train`;
- scenario card: `procthor_house_smoke`;
- episodes: 1;
- frames per episode: 8;
- resolution: 256 x 256;
- GPUs: `CUDA_VISIBLE_DEVICES=4,5,6,7`.

Metrics:

- ProcTHOR dataset split loading;
- procedural house loading into AI2-THOR;
- RGB/depth/semantic/instance file writing;
- action and pose recording;
- visible object category extraction;
- four metric gate payloads;
- valid frames per second.

Pass condition:

- remote validator returns `valid: true`;
- at least one procedural house episode is accepted;
- episode manifest includes backend `procthor`;
- failed action count is zero or explained.

Current status:

- passed on the remote server with 1 episode, 8 frames, no rejections, no failed actions, visible
  categories `Fridge` and `GarbageBag`, and `valid_frames_per_second = 0.91`.

## Experiment 3: Variety Audit

Question:

Does adding more seeds actually increase controlled variety?

Setup:

- backend: first real ProcTHOR backend;
- episode counts: 100, 1,000, 10,000;
- fixed render profile;
- compare metrics after each scale step.

Metrics:

- object category coverage;
- object instance coverage;
- size bin coverage;
- color bin coverage;
- texture bin coverage;
- layout coverage;
- policy coverage;
- trajectory coverage;
- co-occurrence coverage;
- duplicate or near-duplicate episode rate.

Pass condition:

- coverage increases with more seeds;
- required bins reach minimum counts before the next scale step;
- near-duplicate rate stays below the chosen threshold.

Fail condition:

- frame count increases but variable coverage saturates early;
- one policy or object group dominates the dataset;
- validation split contains near-duplicates of training scenes.

## Experiment 4: Throughput Profiling

Question:

Which stage limits generation speed on the remote 5090 server?

Setup:

- backend: real fast simulator;
- episodes: 1,000;
- frames per episode: 100;
- resolution: 256 x 256 and 384 x 384;
- workers: test 1, 2, 4, 8 if supported.

Metrics:

- scene sampling time;
- simulation time;
- rendering time;
- annotation time;
- write time;
- validation time;
- raw frames per second;
- valid frames per second;
- storage per million frames;
- rejection rate by reason.

Pass condition:

- bottleneck stage is identified;
- valid frames per second is high enough to plan a 100,000 to 1,000,000 frame run;
- write speed and storage are measured, not guessed.

Fail condition:

- only total runtime is recorded;
- throughput ignores rejected episodes;
- output size makes the next run impractical.

## Experiment 5: Learning Sanity Check

Question:

Does the dataset contain useful action-conditioned signal?

Setup:

- train three small baselines on the same accepted episodes:
  - static frame baseline;
  - passive temporal baseline without action;
  - action-conditioned temporal baseline;
- evaluate on held-out scenes and held-out object arrangements.

Metrics:

- next RGB prediction loss;
- depth prediction loss;
- object permanence accuracy;
- target reappearance localization error;
- held-out layout performance gap.

Pass condition:

```text
action_conditioned < passive_temporal < static_frame
```

for at least one core prediction metric, with object permanence examples showing the same direction.

Fail condition:

- action-conditioned model does not improve;
- object permanence metric cannot be computed;
- held-out split is contaminated by near-duplicate episodes.

## Experiment 6: High-Fidelity Subset Transfer Test

Question:

Does fast-rendered training transfer to visually richer scenes?

Setup:

- train on fast ProcTHOR episodes;
- validate on BlenderProc or Infinigen-rendered desk and kitchen clips;
- keep trajectory and task variables as close as possible.

Metrics:

- prediction loss gap between fast validation and high-fidelity validation;
- segmentation/depth label consistency;
- appearance variable coverage;
- manual visual quality review.

Pass condition:

- high-fidelity subset exposes a measurable domain gap;
- examples explain whether the gap comes from texture, lighting, geometry, object type, or label
  mismatch.

Fail condition:

- high-fidelity clips do not match the embodied task;
- the renderer is slow but does not answer a transfer question;
- labels are inconsistent with fast-profile labels.

## Iteration Ledger Template

Use this format after each run:

```text
Conjecture:
Physical parameterization:
Operationalization:
Profiling plan:
Result:
Interpretation:
Conjecture update:
Next uncertainty:
```
