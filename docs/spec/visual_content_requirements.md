# Visual Content Requirements

## Design Goal

A physically valid camera path is not automatically useful. The camera can move smoothly through
free space and still see blank walls, empty floors, one giant object, repeated texture, or almost no
new spatial information. Visual-content requirements define what a frame, clip, and full dataset
must visually contain before the data is accepted.

## Frame-Level Requirements

Each accepted frame should contain enough meaningful content for motion-conditioned prediction.

| Requirement | Why it matters | Default quantitative test |
|---|---|---|
| foreground or support-surface content | Rejects views dominated by wall, ceiling, floor, or empty background. | `foreground_ratio >= 0.40` for desk/kitchen/bath, `>= 0.55` bookshelf, `>= 0.30` living room. |
| visible object count | Ensures the frame contains semantic entities, not only one texture. | `visible_object_count >= 2` sparse, `>= 3` medium/dense, `>= 5` bookshelf. |
| bounded dominant-object area | Rejects close-ups where one object removes scene context. | `dominant_object_area_ratio <= 0.70`. |
| semantic diversity | Encourages object and surface variety in the image. | entropy `>= 0.75` desk/kitchen/bath/living, `>= 1.00` bookshelf. |
| valid depth distribution | Rejects invalid depth, near-plane collision, or flat-depth degenerate views. | valid depth ratio `>= 0.95`; depth `p95-p05 >= 0.20 m`. |
| valid segmentation coverage | Ensures semantic/instance annotations cover visible content. | unknown segmentation ratio `<= 0.05`. |
| anchor visibility | Keeps object-aware starts and anchor-following primitives meaningful. | anchor area ratio `0.03-0.55` default, `0.02-0.60` living/bookshelf. |

The foreground class set is scenario-specific. For a desk, foreground includes desk surface,
monitor, keyboard, mouse, notebooks, mugs, electronics, cables, and nearby chair or shelf context.
For a living room, some room-scale context such as sofa, table, rug, wall art, or window can be
valid visual content.

## Clip-Level Requirements

An accepted clip must be locally continuous but globally informative.

| Requirement | Why it matters | Initial test |
|---|---|---|
| smooth adjacent change | Prevents teleportation, jitter, and abrupt visual jumps. | adjacent visual delta `0.015-0.18`; translation `0.01-0.05 m/frame`; rotation `1-3 deg/frame`. |
| nontrivial first-to-last change | Rejects copy-forward clips. | first-to-last visual delta `>= 0.12`; total displacement `>= 0.12 m` for translation primitives or accumulated yaw/pitch `>= 10 deg` for scan primitives. |
| new object or surface evidence | Ensures motion reveals spatial structure. | at least 1 new/lost object or `>= 20%` object-pixel reweighting. |
| depth distribution change | Encourages approach, retreat, parallax, or viewpoint change. | first-to-last depth histogram distance `>= 0.08`. |
| parallax or viewpoint-induced transformation | Separates useful camera motion from pure image noise. | pose translation plus visible-background or surface-correspondence change |
| no long redundant run | Prevents many near-duplicate frames. | max consecutive low-delta frames `<= 4`; weak frame fraction `<= 0.10`. |

A clip is spatially transformative if it causes a measurable change in viewpoint, changes the
visible surface or object set, and reveals or reweights scene geometry in a way that cannot be
solved by copying the initial frame.

## Dataset-Level Requirements

Across the dataset, visual content must vary in controlled ways:

- scenario families;
- layout templates;
- object categories and counts;
- object states;
- materials, textures, and colors;
- lighting profiles;
- motion primitives;
- anchor categories;
- viewing distances and angles;
- occlusion regimes;
- reveal and revisit events.

The generator should use controlled distributions rather than arbitrary random colors or textures.
The goal is variation that preserves real-world plausibility while preventing overfitting to a small
number of visual templates.

## Occlusion Regimes

Occlusion is useful because it forces the model to learn persistence and reappearance, but too much
occlusion can make a frame uninformative. Each scenario family should sample three regimes:

| Regime | Definition | Accepted example | Rejected example |
|---|---|---|---|
| low occlusion | Most required objects are fully visible. | A sparse desk where monitor, keyboard, and mug are all visible. | Empty desk with only one object. |
| medium occlusion | Some objects are partially occluded but interpretable. | A mug partly behind a notebook, with the keyboard still visible. | Keyboard completely hidden behind the monitor in every probe view. |
| high occlusion | Object clusters overlap strongly but remain semantically readable. | Dense kitchen counter with bottles and utensils partially blocking each other. | A single close object covers most of the frame and hides all context. |

## Copy-Forward Rejection

Copy-forward clips are sequences where predicting future frames from the first frame alone is too
easy. Reject a clip when:

```text
first_to_last_visual_delta < 0.08
or visible_object_set_change == 0 and object_pixel_reweighting < 0.20
or pose_displacement < 0.08 m for translation primitives
```

The first implementation may approximate this with RGB difference, depth histogram difference,
semantic mask difference, and visible object set difference. Later versions should use surface IDs
and pixel-to-3D correspondence.

## Debug Artifacts

Every accepted or rejected pilot batch should produce:

- RGB contact sheet;
- depth contact sheet;
- semantic and instance contact sheets;
- foreground mask overlay;
- largest-instance overlay;
- anchor visibility timeline;
- visible object count timeline;
- adjacent visual-delta plot;
- first-to-last change summary;
- rejection reason table.
