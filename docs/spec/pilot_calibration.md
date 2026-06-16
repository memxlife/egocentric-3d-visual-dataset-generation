# Pilot Calibration

## Purpose

Thresholds should not be chosen only from theory. Each scenario family needs empirical calibration
because desks, kitchens, bookshelves, living rooms, and bathrooms have different visual statistics.

The pilot is a falsification step. It asks whether the current scene grammar, start sampler, motion
primitive library, and metric thresholds actually accept good clips and reject bad clips.

## Static Scene Calibration

For each scenario family:

1. Generate 100-500 candidate static scenes.
2. Render 10-20 low-resolution probe views per scene.
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
| foreground ratio | 0.4 |
| minimum visible objects | 2 or 3 |
| maximum single-object area | 0.7 |
| anchor visibility ratio | 0.5 |
| clip length | 32-64 frames |
| per-frame translation | 1-5 cm |
| per-frame rotation | 1-3 degrees |

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
