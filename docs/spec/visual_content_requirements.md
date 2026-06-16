# Visual Content Requirements

## Design Goal

A physically valid camera path is not automatically useful. The camera can move smoothly through
free space and still see blank walls, empty floors, one giant object, repeated texture, or almost no
new spatial information. Visual-content requirements define what a frame, clip, and full dataset
must visually contain before the data is accepted.

## Frame-Level Requirements

Each accepted frame should contain enough meaningful content for motion-conditioned prediction.

| Requirement | Why it matters | Initial test |
|---|---|---|
| foreground or support-surface content | Rejects views dominated by wall, ceiling, floor, or empty background. | `foreground_ratio >= threshold_for_scenario` |
| visible object count | Ensures the frame contains semantic entities, not only one texture. | `visible_object_count >= min_objects` |
| bounded dominant-object area | Rejects close-ups where one object removes scene context. | `dominant_object_area_ratio <= max_ratio` |
| semantic diversity | Encourages object and surface variety in the image. | `semantic_entropy >= min_entropy` |
| valid depth distribution | Rejects invalid depth, near-plane collision, or flat-depth degenerate views. | valid depth mass, depth range, depth histogram spread |
| valid segmentation coverage | Ensures semantic/instance annotations cover visible content. | unknown or invalid segmentation ratio below threshold |
| anchor visibility | Keeps object-aware starts and anchor-following primitives meaningful. | anchor visible in required frames and within area bounds |

The foreground class set is scenario-specific. For a desk, foreground includes desk surface,
monitor, keyboard, mouse, notebooks, mugs, electronics, cables, and nearby chair or shelf context.
For a living room, some room-scale context such as sofa, table, rug, wall art, or window can be
valid visual content.

## Clip-Level Requirements

An accepted clip must be locally continuous but globally informative.

| Requirement | Why it matters | Initial test |
|---|---|---|
| smooth adjacent change | Prevents teleportation, jitter, and abrupt visual jumps. | adjacent pose delta and adjacent visual delta within bounds |
| nontrivial first-to-last change | Rejects copy-forward clips. | first-to-last pose and visual delta above threshold |
| new object or surface evidence | Ensures motion reveals spatial structure. | visible object set or surface set changes over time |
| depth distribution change | Encourages approach, retreat, parallax, or viewpoint change. | depth histogram delta above threshold |
| parallax or viewpoint-induced transformation | Separates useful camera motion from pure image noise. | pose translation plus visible-background or surface-correspondence change |
| no long redundant run | Prevents many near-duplicate frames. | maximum consecutive low-delta frames below limit |

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
first_to_last_visual_delta < min_global_visual_delta
or visible_object_set_change < min_object_set_change
or pose_displacement < min_pose_displacement
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
