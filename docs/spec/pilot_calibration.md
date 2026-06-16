# Pilot Calibration

## Purpose

Thresholds should not be chosen only from theory. Each scenario family needs empirical calibration
because desks, kitchens, bookshelves, living rooms, and bathrooms have different visual statistics.

## Static Scene Calibration

For each scenario family:

1. Generate 100-500 candidate static scenes.
2. Render 10-20 low-resolution probe views per scene.
3. Compute static scene metrics:
   - semantic completeness;
   - physical plausibility;
   - visual richness;
   - free-space availability;
   - appearance diversity;
   - object count and category entropy.
4. Inspect accepted and rejected examples.
5. Tune thresholds.
6. Generate 1,000 accepted scenes.
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
- maximum single-object area ratio;
- semantic entropy;
- anchor visibility ratio;
- adjacent visual delta;
- first-to-last visual delta;
- adjacent pose delta;
- first-to-last pose delta;
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
- accepted and rejected clip preview dashboard;
- threshold table by scenario family;
- rejection reason histogram;
- examples of true accept, true reject, and uncertain cases;
- decision: scale, revise static scene generator, revise trajectory policy, or revise thresholds.
