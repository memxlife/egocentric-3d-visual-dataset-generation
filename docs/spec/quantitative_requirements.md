# Quantitative Requirements

## Purpose

This document defines the default numeric contract for Version 1 pilot generation. These numbers
are not final scientific constants. They are the first executable thresholds that make the dataset
spec implementable, auditable, and falsifiable.

Each threshold has three possible states:

| State | Meaning |
|---|---|
| pass | Candidate is accepted by the quantitative gate. |
| reject | Candidate is rejected and gets a reason code. |
| review band | Candidate is saved for human inspection during pilot calibration. |

The review band is important. It prevents early thresholds from silently throwing away useful edge
cases while the metrics are still being calibrated.

Every number below is a starting hypothesis. It must be justified by the learning problem, then
tested during pilot calibration. A threshold is valid only if the pilot report shows representative
accepted examples, rejected examples, false accepts, and false rejects.

## Dataset Scale Targets

| Scope | Static scenes | Starts per scene | Clips per start | Frames per clip | Total clips | Total frames |
|---|---:|---:|---:|---:|---:|---:|
| remote schema smoke | 1-3 | 2-4 | 1 | 8-16 | 2-12 | 16-192 |
| object-aware start pilot | 5-10 | 8-16 | 1-2 | 32 | 40-320 | 1,280-10,240 |
| desk calibration pilot | 100 | 32 | 4 | 32 | 12,800 | 409,600 |
| scenario calibration pilot | 100-500 | 32-64 | 4 | 32 | 12,800-128,000 | 0.4M-4.1M |
| Version 1 major family | 1,000 | 128 | 4 | 32 | 512,000 | 16.4M |

Do not scale to the next row unless acceptance rate, rejection reasons, throughput, and visual
inspection all pass.

### Scale Target Justification

| Setting | Justification | If too low | If too high |
|---|---|---|---|
| remote schema smoke: 16-192 frames | Small enough to run quickly on the remote server while exercising manifests, frame writing, and validation. | May not touch all schema paths or failure modes. | Wastes time before basic file-writing bugs are fixed. |
| object-aware start pilot: 1,280-10,240 frames | Large enough to inspect whether starts actually look at objects across several scenes. | Start-quality failures may look anecdotal. | Hard to inspect manually before metrics are trusted. |
| desk calibration pilot: 409,600 frames | Gives thousands of clips from one controlled scenario, enough to estimate metric distributions by primitive and anchor type. | Threshold estimates are noisy. | Premature scale before one scenario is understood. |
| Version 1 major family: 16.4M frames | Provides many scenes, starts, and primitives so models cannot memorize one layout or one trajectory pattern. | Weak coverage for held-out scene/start/primitive tests. | Storage and rendering cost may exceed the first research need. |

## Scenario Scene Targets

| Scenario | Accepted scenes | Layout templates | Object categories per scene | Object instances per scene | Required probe views |
|---|---:|---:|---:|---:|---:|
| computer desk | 1,000 | >= 8 | 5-14 | 4-32 | 12 |
| kitchen counter | 1,000 | >= 8 | 6-18 | 5-48 | 12 |
| bookshelf/storage | 500 | >= 6 | 4-16 | 10-160 | 16 |
| living room table/sofa | 500 | >= 6 | 5-16 | 5-56 | 12 |
| bathroom vanity | 500 | >= 5 | 5-14 | 4-36 | 12 |

Scene targets count accepted scenes, not candidate scenes. Candidate counts must be reported
separately because low acceptance rate is evidence of a bad generator or overly strict thresholds.

### Scene Target Justification

| Setting | Justification | If too low | If too high |
|---|---|---|---|
| 1,000 desk and kitchen scenes | Desk and kitchen are the first major families because they contain dense object interactions, support relations, and varied small-object visual content. | Models may overfit to a small number of surfaces and object layouts. | Generator effort may be spent before metrics and scene grammar are stable. |
| 500 bookshelf, living room, bathroom scenes | These families add different visual regimes but can initially be smaller because they are secondary coverage families. | Held-out scenario tests become weak. | Pilot effort spreads too thin before desk/kitchen quality is known. |
| 5-18 object categories per scene | Enough categories to create semantic structure without turning every scene into unrealistic clutter. | Frames become too simple and semantically sparse. | Scenes become implausible, cluttered, and hard to validate. |
| 12 probe views, 16 for bookshelf | Probe views need enough angles to detect empty or blocked viewpoints; bookshelf needs more because shelf content is vertically structured and repetitive. | Bad scenes pass because only easy viewpoints were tested. | Probe rendering cost grows before trajectory sampling. |

## Static Scene Probe Gates

Probe views are low-resolution validation renders. A static scene passes only if enough probe views
contain useful visual content and enough valid free space exists for starts and trajectories.

| Metric | Pass | Review band | Reject |
|---|---:|---:|---:|
| valid probe view count | >= 8 desk/kitchen/living/bath, >= 10 bookshelf | 5-7 or 8-9 bookshelf | below review band |
| median foreground ratio | >= 0.40 desk/kitchen/bath, >= 0.55 bookshelf, >= 0.30 living | within 0.05 below pass | below review band |
| median visible object count | >= 3 desk/kitchen/bath/living, >= 6 bookshelf | 1 object below pass | below review band |
| dominant object ratio median | <= 0.65 | 0.65-0.75 | > 0.75 |
| unknown segmentation ratio | <= 0.05 | 0.05-0.10 | > 0.10 |
| valid depth pixel ratio | >= 0.95 | 0.90-0.95 | < 0.90 |
| free-space connected component count | >= 1 component supporting 16 poses | component supports 8-15 poses | no component supports 8 poses |
| support validity | >= 98% valid object support relations | 95-98% | < 95% |
| severe interpenetration count | 0 | 1 if visually hidden | > 1 or visible |

### Static Scene Probe Gate Justification

| Metric | Justification | If threshold too low | If threshold too high |
|---|---|---|---|
| valid probe view count | A scene should support several possible starts, not just one lucky viewpoint. | Scenes with mostly unusable viewpoints pass. | Good compact scenes are rejected because they have fewer camera-accessible angles. |
| median foreground ratio | The model needs object/support-surface content, not mostly wall/floor. Bookshelves need higher foreground because shelf content should dominate; living rooms allow more context. | Empty views pass. | Useful contextual views are rejected. |
| median visible object count | Multiple objects create occlusion, correspondence, and semantic persistence signals. Bookshelves require more because repeated objects are central to the scenario. | Single-object or empty scenes pass. | Sparse but realistic scenes are rejected. |
| dominant object ratio median | Prevents probe views from being dominated by one close object while allowing purposeful close-up scenes. | Degenerate close-ups pass. | Legitimate inspection views are rejected. |
| unknown segmentation ratio | Segmentation is supervision; too much unknown area makes frame labels unreliable. | Bad labels enter training. | Minor annotation gaps reject otherwise useful scenes. |
| valid depth pixel ratio | Depth is a key supervision signal; invalid depth often indicates clipping or renderer artifacts. | Clipped or broken views pass. | Reflective or thin geometry scenes may be over-rejected. |
| free-space component supports 16 poses | The scene needs enough nearby valid starts to generate multiple clips. | Scene accepts but cannot produce trajectory diversity. | Compact spaces such as bathrooms may be over-rejected. |
| support validity 98% | One or two minor issues may be tolerable in large clutter, but most objects must obey support physics. | Floating/intersecting objects teach wrong priors. | Asset imperfections reject many plausible scenes. |
| severe interpenetration count 0 | Visible severe penetration is a realism failure. | Physically impossible scenes pass. | Hidden harmless mesh overlap blocks useful scenes. |

## Frame-Level Gates

Frame-level metrics are computed for every rendered frame. A clip may tolerate a small number of
borderline frames, but not long runs of weak content.

| Metric | Pass | Review band | Reject reason |
|---|---:|---:|---|
| foreground ratio | >= 0.40 desk/kitchen/bath, >= 0.55 bookshelf, >= 0.30 living | within 0.05 below threshold | `low_foreground_ratio` |
| visible object count | >= 2 sparse, >= 3 medium/dense, >= 5 bookshelf | 1 object below threshold | `low_visible_object_count` |
| dominant object area ratio | <= 0.70 | 0.70-0.80 | `dominant_object_too_large` |
| semantic entropy | >= 0.75 desk/kitchen/bath/living, >= 1.00 bookshelf | within 0.15 below threshold | `low_semantic_entropy` |
| valid depth pixel ratio | >= 0.95 | 0.90-0.95 | `invalid_depth_coverage` |
| depth range p95-p05 | >= 0.20 m | 0.10-0.20 m | `flat_depth_distribution` |
| unknown segmentation ratio | <= 0.05 | 0.05-0.10 | `invalid_segmentation_coverage` |
| anchor area ratio when required | 0.03-0.55 default, 0.02-0.60 for living/bookshelf | 0.01 outside bounds | `anchor_area_out_of_bounds` |

Clip-level tolerance:

```text
weak_frame_fraction <= 0.10
max_consecutive_weak_frames <= 3 for 32-frame clips
```

### Frame Gate Justification

| Metric | Justification | If threshold too low | If threshold too high |
|---|---|---|---|
| foreground ratio | Ensures the frame contains objects or support surfaces relevant to spatial learning. | Blank background/floor/wall frames pass. | Legitimate contextual frames are rejected. |
| visible object count | Forces semantic richness and object persistence evidence. | Single-object clips become common. | Minimal but realistic scenes cannot pass. |
| dominant object area ratio | Keeps close-ups from losing spatial context. | One object fills the frame and prediction becomes texture extrapolation. | Useful approach/inspection motions are rejected. |
| semantic entropy | Requires more than one semantic region. Bookshelf threshold is higher because repeated shelf structure should still contain varied books/objects. | Monotone texture or one-class views pass. | Clean sparse scenes are rejected. |
| valid depth pixel ratio | Keeps depth supervision reliable. | Invalid depth artifacts enter training. | Thin/specular objects may trigger excessive rejection. |
| depth range p95-p05 | Requires visible depth structure for 3D learning. | Flat wall/surface views pass. | Close planar inspection views are over-rejected. |
| unknown segmentation ratio | Keeps semantic/instance supervision usable. | Large unlabeled regions enter training. | Minor taxonomy gaps block otherwise good frames. |
| anchor area ratio | Anchor should be visible but not consume the whole frame. | Anchor may be absent or tiny. | Useful close/far anchor views are rejected. |
| weak frame fraction 0.10 | Allows occasional borderline frames during smooth motion. | Long weak intervals pass. | Natural transient views cause over-rejection. |
| max 3 consecutive weak frames | Prevents a 32-frame clip from spending a long interval in useless visual content. | Smooth but useless clips pass. | Short occlusion or transition events are over-rejected. |

## Clip-Level Gates

| Metric | Pass | Review band | Reject reason |
|---|---:|---:|---|
| clip length | 32 frames pilot, 32-64 allowed | 16-31 for smoke only | `clip_too_short` |
| per-frame translation | 0.01-0.05 m | 0.005-0.01 m or 0.05-0.07 m | `pose_translation_out_of_bounds` |
| per-frame rotation | 1-3 deg | 0.5-1 deg or 3-5 deg | `pose_rotation_out_of_bounds` |
| per-frame linear acceleration | <= 0.03 m/frame^2 | 0.03-0.05 | `pose_acceleration_too_high` |
| per-frame angular acceleration | <= 2 deg/frame^2 | 2-4 | `angular_acceleration_too_high` |
| total displacement for translation primitive | >= 0.12 m | 0.08-0.12 m | `pose_change_too_small` |
| accumulated yaw/pitch for scan primitive | >= 10 deg | 6-10 deg | `pose_change_too_small` |
| anchor visible fraction for anchor primitive | >= 0.70 | 0.50-0.70 | `anchor_not_visible` |
| visible object set change | >= 1 new/lost object or >= 20% object-pixel reweighting | weak but visible change | `no_new_visibility_evidence` |
| first-to-last depth histogram distance | >= 0.08 | 0.04-0.08 | `depth_change_too_small` |
| max consecutive low-delta frames | <= 4 | 5-6 | `redundant_frame_run` |

### Clip Gate Justification

| Metric | Justification | If threshold too low | If threshold too high |
|---|---|---|---|
| 32-frame pilot clips | Long enough to show accumulated change while short enough for cheap pilots and contact-sheet inspection. | Clips may not contain a meaningful transformation. | Clips become harder to inspect and more expensive to render. |
| 0.01-0.05 m/frame translation | Produces visible parallax without teleporting the egocentric camera. | Motion becomes visually redundant. | Motion becomes abrupt or collision-prone. |
| 1-3 deg/frame rotation | Supports smooth scan motions without jump cuts. | Visual change may be too weak. | Abrupt gaze shifts dominate the sequence. |
| 0.03 m/frame^2 acceleration | Limits sudden speed changes while allowing primitive transitions. | Jitter and unrealistic velocity changes pass. | Smooth but purposeful starts/stops may be rejected. |
| 2 deg/frame^2 angular acceleration | Limits abrupt angular jumps. | Look direction can snap unnaturally. | Natural scan acceleration is over-rejected. |
| 0.12 m total displacement | Ensures translation primitives produce meaningful parallax over 32 frames. | Copy-forward or near-static clips pass. | Compact scenes cannot produce valid clips. |
| 10 deg accumulated yaw/pitch | Ensures scan primitives change view enough to reveal new content. | Tiny pans pass. | Focused small-object inspection gets rejected. |
| 70% anchor visible fraction | Maintains the semantic reason for anchor-conditioned clips while allowing temporary occlusion/look-away. | Anchor-conditioned clips lose the anchor. | Reveal/peek motions are over-rejected. |
| 1 new/lost object or 20% reweighting | Requires visible evidence that viewpoint changed scene content. | Pixel-only shifts pass without semantic change. | Smooth parallax over the same objects may be rejected. |
| 0.08 depth histogram distance | Requires measurable 3D change, not just color change. | Flat visual motion passes. | Lateral motions at similar depth are over-rejected. |
| max 4 low-delta frames | Allows short pauses but rejects long redundant intervals. | Copy-forward sections pass. | Smooth slow motion gets over-rejected. |

## Composite Visual Delta Defaults

For RGB values normalized to `[0, 1]`, depth histograms normalized to probability mass, and masks
represented by IoU:

```text
visual_delta_approx =
  0.25 * mean_abs_rgb_difference
  + 0.25 * depth_histogram_l1
  + 0.25 * (1 - semantic_mask_iou)
  + 0.25 * visible_object_set_distance
```

Initial gates:

| Delta | Pass | Review band | Reject |
|---|---:|---:|---:|
| adjacent visual delta | 0.015-0.18 | 0.008-0.015 or 0.18-0.25 | outside review band |
| first-to-last visual delta | >= 0.12 | 0.08-0.12 | < 0.08 |

Too-low adjacent delta means the sequence is redundant. Too-high adjacent delta means abrupt motion,
occlusion pop-in, or rendering instability.

### Visual Delta Weight Justification

| Setting | Justification | If too low | If too high |
|---|---|---|---|
| equal weights 0.25 each | No single modality is trusted before calibration; RGB, depth, semantic mask, and object-set change each test a different failure mode. | A modality may be ignored even when it catches a real failure. | A noisy modality may dominate acceptance. |
| adjacent delta lower bound 0.015 | Rejects frame pairs with almost no visual change. | Redundant clips pass. | Slow smooth inspection is over-rejected. |
| adjacent delta upper bound 0.18 | Rejects abrupt visual discontinuities while allowing normal parallax and pan. | Jump cuts and rendering pop-in pass. | Useful reveal events are over-rejected. |
| first-to-last delta 0.12 | Requires accumulated visual transformation over the full clip. | Copy-forward clips pass. | Short but meaningful transformations are rejected. |

## Dataset-Level Coverage Gates

| Metric | Phase 1 pilot target | Version 1 target |
|---|---:|---:|
| scenario family coverage | 1-2 families | 5 families |
| layout template coverage | >= 3 for pilot family | all listed templates, no template < 5% in family |
| motion primitive coverage | >= 5 primitives | all primitives, no primitive < 5% unless intentionally rare |
| anchor category coverage | >= 5 anchor categories | scenario-specific required anchors, no required anchor < 5% |
| clutter regime balance | each regime >= 15% | each regime >= 20% where plausible |
| occlusion regime balance | low/medium/high each >= 15% | low/medium/high each >= 20% where plausible |
| material family coverage | >= 3 material families | all allowed material families represented |
| rejection reason reporting | >= 95% rejected candidates have reason codes | >= 99% |

### Coverage Gate Justification

| Setting | Justification | If too low | If too high |
|---|---|---|---|
| no Version 1 template below 5% | Prevents one layout from dominating a scenario family. | Dataset collapses into a few templates. | Rare but useful templates may be oversampled unnaturally. |
| each clutter/occlusion regime >= 20% | Forces sparse, medium, and dense cases to all be learnable/evaluable. | Model sees too little of one regime. | Unrealistic balancing may distort natural scenario frequency. |
| required anchor category >= 5% | Ensures anchor-conditioned learning covers all important target types. | Some anchor types have too little data for evaluation. | Rare anchor types are overrepresented. |
| rejection reason reporting >= 99% | Scaling requires nearly all failures to be explainable. | Failure analysis becomes impossible. | Minor tooling gaps may block scale unnecessarily. |

## Throughput Gates

Throughput must be measured as accepted output, not raw rendered frames.

| Metric | Phase 1 pass | Version 1 planning target |
|---|---:|---:|
| accepted frames per second, low-res validation | >= 50 | >= 200 |
| accepted frames per second, final render | >= 2 for simulator smoke | >= 20 for production profile |
| accepted clip rate after scene acceptance | >= 20% | >= 35% |
| static scene acceptance rate | 10-70% | 20-80% |
| invalid-file rate after write | 0 | 0 |

If acceptance rate is above 90%, the gates are probably too weak or candidate generation is not
diverse enough. If acceptance rate is below 10%, the generator, scenario grammar, or thresholds need
revision before scaling.

### Throughput Gate Justification

| Setting | Justification | If too low | If too high |
|---|---|---|---|
| accepted low-res validation FPS >= 50 Phase 1 | Low-res gates should be cheap enough to reject bad candidates before final rendering. | Invalid candidates consume final-render time. | Engineering may optimize validation prematurely. |
| accepted final-render FPS >= 2 smoke | A minimal simulator smoke may be slow but must still produce inspectable clips in reasonable time. | Even small diagnostic loops become stale. | Early prototype may be blocked by performance before correctness. |
| accepted final-render FPS >= 20 planning | Million-frame runs require production throughput, not only correctness. | Dataset generation takes too long for research iteration. | Quality may be sacrificed for speed. |
| clip acceptance >= 20% Phase 1 | At least one in five post-scene clips should be useful; lower means sampling is mostly waste. | Too much time is spent rendering bad clips. | Metrics may be too permissive. |
| scene acceptance 10-70% pilot | A healthy pilot rejects bad scenes but does not reject almost everything. | Bad scenes pass or generator lacks diversity. | Generator/thresholds are mismatched and cannot scale. |

## Calibration Rule

A pilot may change a threshold only if it records:

- metric distribution before the change;
- at least 10 accepted examples;
- at least 10 rejected examples;
- false accept examples;
- false reject examples;
- new threshold value;
- expected failure if the threshold is too low;
- expected failure if the threshold is too high.
