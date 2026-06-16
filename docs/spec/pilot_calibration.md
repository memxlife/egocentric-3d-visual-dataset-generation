# Pilot Calibration

## Purpose

Thresholds should not be chosen only from theory. Each scenario family needs empirical calibration
because desks, kitchens, bookshelves, living rooms, and bathrooms have different visual statistics.

The pilot is a falsification step. It asks whether the current scene grammar, start sampler, motion
primitive library, and metric thresholds actually accept good clips and reject bad clips.

## Static Scene Calibration

For each scenario family:

1. Generate 100-500 candidate static scenes.
2. Render 12 low-resolution probe views per scene for desk, kitchen, living room, and bathroom;
   render 16 probe views for bookshelf/storage.
3. Compute static scene metrics:
   - semantic completeness;
   - support validity;
   - physical plausibility;
   - probe foreground ratio;
   - probe visible object count;
   - free-space availability;
   - appearance diversity;
   - object count and category entropy.
4. Inspect accepted and rejected examples.
5. Tune thresholds or revise the scene grammar.
6. Generate 1,000 accepted scenes only after the pilot passes.
7. Pass accepted scenes to trajectory generation.

## Trajectory Calibration

For one scenario family, such as desks:

```text
100 scenes
  x 32 starting views
  x 4 candidate clips
```

For each candidate clip, compute:

- foreground ratio;
- visible object count;
- dominant object area ratio;
- semantic entropy;
- anchor visibility ratio;
- adjacent visual delta;
- first-to-last visual delta;
- adjacent pose delta;
- first-to-last pose delta;
- new visible object or surface evidence;
- action or primitive distribution;
- rejection reason.

Inspect accepted and rejected clips until three qualitative conditions hold:

1. the camera never violates obvious physical constraints;
2. the visual stream remains smooth and human-like;
3. the clip contains meaningful objects and meaningful spatial change.

## Pilot Threshold Starting Points

| Requirement | Initial value |
|---|---:|
| foreground ratio | 0.40 desk/kitchen/bath, 0.55 bookshelf, 0.30 living |
| minimum visible objects | 2 sparse, 3 medium/dense, 5 bookshelf |
| maximum single-object area | 0.70 |
| anchor area ratio | 0.03-0.55 default, 0.02-0.60 living/bookshelf |
| anchor visible frame fraction | 0.70 for anchor-maintaining primitives |
| clip length | 32 frames pilot, 32-64 allowed |
| per-frame translation | 1-5 cm |
| per-frame rotation | 1-3 degrees |
| max linear acceleration | 0.03 m/frame^2 |
| max angular acceleration | 2 deg/frame^2 |
| first-to-last visual delta | >= 0.12 pass, 0.08-0.12 review |
| adjacent visual delta | 0.015-0.18 pass |
| total displacement | >= 0.12 m for translation primitives |
| accumulated yaw/pitch | >= 10 degrees for scan primitives |

These are not final. Freeze thresholds only after pilot visual inspection and rejection analysis.

## Calibration Outputs

Each calibration run should produce:

- run report;
- threshold table by scenario family;
- distribution plots for each metric;
- accepted and rejected clip preview dashboard;
- false accept examples;
- false reject examples;
- rejection reason histogram;
- per-scenario acceptance rate;
- per-primitive acceptance rate;
- anchor-category acceptance rate;
- examples of true accept, true reject, and uncertain cases;
- decision log.

## Pilot Decision

Each pilot ends with one of these decisions:

| Decision | Meaning |
|---|---|
| scale up | Current grammar, policy, and thresholds are good enough for the next scale level. |
| revise static scene generator | Rejections or false accepts are dominated by bad scene content. |
| revise trajectory policy | Starts or primitives produce weak or invalid motion. |
| revise metric thresholds | Visual examples are good but metrics reject them, or bad examples pass. |
| revise scenario taxonomy | Scenario family definition is too broad, too narrow, or missing important variants. |
| revise schema | Needed evidence cannot be stored or audited. |

Do not scale on aggregate acceptance rate alone. The visual examples and rejection reasons must
explain why the accepted data is useful.

## Quantitative Scale Decision

Scale up only if all of these are true:

| Gate | Pass condition |
|---|---|
| static scene acceptance rate | between `10%` and `70%` for early pilots, unless a documented reason explains otherwise |
| clip acceptance rate after scene acceptance | `>= 20%` for Phase 1, `>= 35%` for Version 1 planning |
| rejected candidates with reason codes | `>= 95%` Phase 1, `>= 99%` Version 1 |
| false accept rate in reviewed sample | `<= 10%` |
| false reject rate in reviewed sample | `<= 15%` |
| post-write invalid-file rate | `0` |
| accepted examples inspected | at least `20` per scenario family before scaling |
| rejected examples inspected | at least `20` per scenario family before scaling |
