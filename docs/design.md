# Dataset Design And Metrics

## Falsifiable Conjecture

An egocentric embodied dataset is useful for our embodied AI research if models trained on
observation-action trajectories learn a better hidden world state than models trained on static
images or passive videos, while the generator can produce valid episodes fast enough to support
many controlled variations.

This conjecture is false if the dataset fails any one of the four dataset metrics:

- generation speed: accepted episodes cannot be generated fast enough for repeated research
  iterations;
- realism: generated scenes do not obey real-world geometry, scale, support, object-state, lighting,
  and navigability rules;
- per-scenario comprehensiveness: episodes do not cover the required 3D viewpoints, motions, objects,
  and visibility events inside each scenario;
- cross-scenario diversity: the full dataset does not cover enough scenario families, layouts,
  objects, appearances, states, and trajectory types.

## Task Input And Output

Input to the generator:

- scene seed;
- episode seed;
- scenario family;
- object taxonomy and asset pool;
- camera and agent embodiment;
- policy family;
- render profile.

Output from the generator:

- ordered egocentric RGB frames;
- depth;
- semantic and instance masks;
- camera pose;
- action label or continuous action vector;
- visible object state;
- scene metadata;
- episode diagnostics;
- generation time and storage cost.

The dataset unit is an episode, not a frame.

## Four Dataset Requirements

The dataset is judged by four requirements. A generated run is not good because it has many frames.
It is good only if it passes all four requirements below.

| Requirement | Question | Primary metric | Failure mode |
|---|---|---|---|
| generation speed | Can we generate accepted episodes fast enough to iterate? | valid frames per second | high raw frame count with many rejected or invalid episodes |
| realism | Do scenes obey real-world object, support, scale, state, and lighting rules? | realism pass rate | physically impossible or semantically wrong scenes |
| per-scenario comprehensiveness | Does each episode cover the 3D space of the target scenario enough to connect motion with visual feedback? | scenario coverage score | camera sees only a narrow or repeated view |
| cross-scenario diversity | Does the dataset cover many scenario families, layouts, objects, appearances, and trajectories? | diversity coverage score | many episodes are near-duplicates with different seeds |

These four requirements are separate. A run can be fast but unrealistic. A run can be realistic but
too narrow. A run can be diverse across scenes but weak inside each scenario. Each failure must be
reported separately.

## Core Difficulty

The dataset must be diverse in the variables that matter for embodied learning, not only diverse in
surface appearance. A useful episode should force a model to connect what it sees now, what it did,
what it saw before, and what could be hidden outside the camera view.

The hard parts are:

- making scenes physically and semantically valid;
- creating enough object, appearance, layout, state, and trajectory variation;
- creating partial observability rather than always-visible objects;
- generating many episodes quickly;
- keeping enough metadata to know which variation was tested.

## Scenario Generation Contract

Each scenario family must be specified before large-scale generation. A scenario family is not a
theme such as "desk" or "kitchen." It is a measurable generation contract.

Each scenario card must define:

- scenario name;
- physical volume to cover;
- required surfaces and objects;
- allowed object states;
- required motion primitives;
- required viewpoint bins;
- required visibility events;
- realism constraints;
- diversity axes;
- speed target;
- pass, fail, and insufficient-evidence conditions.

The generator must write the scenario card id into every episode manifest. If an episode does not
satisfy the card, it must be rejected or marked as insufficient evidence.

## Dataset Generation Process

Dataset generation is a gated process. Each gate checks the four dataset requirements: generation
speed, realism, per-scenario comprehensiveness, and cross-scenario diversity. A run moves to the
next scale only when the current scale passes the gates.

### Gate 0: Define Scenario Cards

Input:

- research goal;
- scenario family list;
- available simulator and asset sources.

Process:

1. Choose the scenario cards to generate, such as desk active scan, kitchen counter active scan, and
   room-to-object search.
2. For each scenario card, define required objects, physical volume, motion primitives, viewpoint
   bins, visibility events, realism constraints, diversity axes, and speed target.
3. Mark each requirement as hard, soft, or optional.

Output:

- scenario card definitions;
- required metadata fields;
- pass, fail, and insufficient-evidence rules.

Pass condition:

- every scenario card has measurable coverage, realism, diversity, and speed rules.

### Gate 1: Sample Candidate Scenes

Input:

- scenario card;
- scene seed;
- object taxonomy;
- asset pool;
- layout rules.

Process:

1. Sample scene layout and support surfaces.
2. Sample required objects first.
3. Sample optional clutter objects.
4. Assign object size, color, texture, state, and support relation.
5. Run scene-level realism checks before any trajectory is rendered.

Output:

- candidate scene;
- full object instance list;
- scene metadata;
- scene rejection reason if failed.

Gate checks:

- realism: object scale, support, collision, semantic relation, state, lighting, navigability;
- diversity: scene card, layout, object categories, object instances, size, color, texture, state;
- speed: scene sampling time.

Pass condition:

- scene realism score passes;
- required objects and required physical volume exist;
- scene adds useful coverage or is allowed by the sampling quota.

### Gate 2: Plan Coverage Trajectories

Input:

- accepted scene;
- scenario card;
- episode seed;
- policy family.

Process:

1. Select a policy family: random scan, scripted active scan, target search, or navigation.
2. Convert the scenario card into required viewpoint bins and motion primitives.
3. Plan camera poses or simulator actions that should visit those bins.
4. Reserve one or more look-away and return segments when object permanence is required.
5. Reject the plan before rendering if it cannot cover the required bins.

Output:

- planned action sequence;
- expected viewpoint-bin coverage;
- expected visibility events;
- trajectory rejection reason if failed.

Gate checks:

- per-scenario comprehensiveness: required motion primitives and expected viewpoint bins;
- speed: planning time;
- realism: planned path does not pass through geometry.

Pass condition:

- planned trajectory can cover the scenario card's minimum bins;
- action sequence includes required movement and view changes;
- target object or region is reachable or visible from reachable poses.

### Gate 3: Simulate And Render Episode

Input:

- accepted scene;
- accepted trajectory plan;
- render profile.

Process:

1. Step the simulator with the action sequence.
2. Render RGB, depth, semantic mask, and instance mask.
3. Record camera pose and action at every frame.
4. Record visible object instances at every frame.
5. Record stage timing for simulation, rendering, annotation, writing, and validation.

Output:

- episode folder;
- frame files;
- `trajectory.parquet`;
- `episode.json`;
- raw timing report.

Gate checks:

- speed: raw frames per second and stage timing;
- realism: camera clipping and invalid simulator states;
- per-scenario comprehensiveness: actual viewpoint-bin coverage and visibility events;
- label completeness: all requested annotations exist.

Pass condition:

- episode has all required files and labels;
- camera motion is non-degenerate;
- rendered frames are nonblank;
- actual coverage matches or exceeds the scenario card threshold.

### Gate 4: Validate Episode Against The Four Metrics

Input:

- rendered episode;
- scenario card;
- scene metadata.

Process:

1. Compute generation speed for the episode.
2. Compute realism score and hard realism failures.
3. Compute scenario coverage score from actual pose, action, object, and visibility records.
4. Compute diversity contribution against the current run coverage table.
5. Accept, reject, or mark insufficient evidence.

Output:

- accepted episode or rejection record;
- rejection reason histogram;
- per-episode metric row.

Pass condition:

- speed is recorded;
- realism score passes and no hard realism constraint fails;
- scenario coverage score passes;
- episode contributes to the required run distribution or is within quota.

### Gate 5: Audit Run-Level Coverage

Input:

- accepted episodes from the current run;
- rejected episodes and reasons;
- target run specification.

Process:

1. Summarize speed: raw frames per second, valid frames per second, stage time share.
2. Summarize realism: pass rate and failure reasons.
3. Summarize per-scenario comprehensiveness: coverage score distribution per scenario card.
4. Summarize diversity: scenario, layout, object, appearance, state, lighting, policy, and trajectory
   coverage.
5. Identify missing bins and dominant rejection reasons.

Output:

- run report;
- coverage dashboard inputs;
- next sampling weights;
- decision to scale, revise, or stop.

Pass condition:

- valid frames per second is high enough for the next scale;
- realism failures are below the threshold and explainable;
- each scenario card reaches minimum coverage;
- required diversity bins reach minimum counts.

### Gate 6: Scale Or Revise

Decision rules:

- If speed fails, profile the slow stage before generating more data.
- If realism fails, fix scene sampling, asset filtering, support rules, or simulator constraints.
- If per-scenario comprehensiveness fails, revise trajectory planning or scenario card thresholds.
- If diversity fails, change sampling weights, add assets, add layouts, or add scenario cards.
- If all four pass, scale to the next run size.

Scale ladder:

```text
remote schema smoke: 3 to 10 episodes
remote simulator smoke: 10 to 100 episodes
micro dataset: 100 to 1,000 episodes
pilot dataset: 10,000 episodes
phase-one dataset: 100,000+ episodes
```

The high-fidelity renderer is introduced only after the fast renderer passes the four gates for a
small or pilot dataset.

### Scenario Card 1: Desk Active Scan

Objective:

Generate an egocentric sequence where the camera approaches and scans a cluttered computer desk. The
episode must show how motion changes visible desk objects.

Physical volume:

- desk support surface;
- region in front of desk where a person or robot head camera can move;
- left, center, and right desk regions;
- near, middle, and far depth regions on the desktop.

Required objects:

- one support surface: desk or table;
- at least one display object: monitor or laptop;
- at least one input object: keyboard or mouse;
- at least two small clutter objects: mug, phone, notebook, book, pen, cable, lamp, headphones, box.

Realism constraints:

- keyboard is in front of monitor or laptop when both exist;
- mouse is left or right of keyboard, not behind the display;
- mug, phone, notebook, and book rest on the support surface;
- lamp rests on desk or clamps to a desk edge;
- cables start or end near electronic objects when cables exist;
- no object intersects another object beyond the validator threshold;
- object scale must fall inside category-specific real-world ranges.

Required motion primitives:

- approach the desk;
- look down at the desktop;
- pan left and right across the desk;
- move laterally at least once;
- look away and return to at least one previously visible object.

Required viewpoint bins:

```text
horizontal position: left, center, right
distance from desk: near, middle, far
camera pitch: down, level, slight up
yaw relative to desk: left-facing, center-facing, right-facing
```

Coverage pass condition:

- at least 6 of 9 horizontal-position x distance bins are visited;
- at least 2 camera pitch bins are visited;
- at least 2 yaw bins are visited;
- at least one object disappears from view and later reappears.

Failure reasons:

- `missing_required_object`;
- `invalid_support_relation`;
- `insufficient_viewpoint_coverage`;
- `no_disappear_reappear_event`;
- `camera_clipping`;
- `low_motion`.

### Scenario Card 2: Kitchen Counter Active Scan

Objective:

Generate an egocentric sequence where the camera moves along a kitchen counter and observes object
states, occlusion, and support relations.

Physical volume:

- counter surface;
- sink, stove, cabinet, drawer, or appliance region when available;
- reachable corridor along the counter;
- above-counter and under-cabinet viewing angles.

Required objects:

- one counter or island support surface;
- at least one large fixture or appliance: sink, stove, refrigerator, microwave, cabinet, drawer;
- at least three counter objects: mug, bowl, plate, bottle, pan, knife, cutting board, towel,
  utensil, food item.

Realism constraints:

- food, dishes, and utensils rest on the counter, in a sink, in a drawer, or on a shelf;
- knives lie flat on a cutting board or counter, not upright in empty space;
- pans are near stove, cabinet, sink, or counter;
- bottles and mugs are upright unless the scenario explicitly samples a fallen state;
- drawers and cabinets use valid open or closed states;
- the agent path does not pass through counters or fixtures.

Required motion primitives:

- move along the counter;
- look down at counter objects;
- look toward a fixture or appliance;
- inspect an open state if an open drawer, cabinet, or appliance is sampled;
- look away and return to one target object or state.

Required viewpoint bins:

```text
counter segment: left, center, right
camera distance: near, middle
height: crouched, standing
pitch: down, level
state focus: closed-region view, open-region view when open states exist
```

Coverage pass condition:

- at least 4 counter segment x distance bins are visited;
- at least 2 height or pitch bins are visited;
- if an open state exists, at least one frame must show its interior or edge state;
- at least one target object or state disappears and reappears.

Failure reasons:

- `missing_counter_surface`;
- `invalid_object_state`;
- `invalid_support_relation`;
- `unreachable_counter_segment`;
- `insufficient_viewpoint_coverage`;
- `state_not_observed`.

### Scenario Card 3: Room-To-Object Search

Objective:

Generate an egocentric navigation sequence where the agent starts away from a target object and moves
until the target becomes visible from a useful viewpoint.

Physical volume:

- room or connected rooms;
- navigable free space;
- start region;
- target object region;
- distractor object regions.

Required objects:

- one target category: chair, table, sofa, desk, fridge, sink, bed, shelf, lamp, door, cabinet, or
  computer;
- at least three distractor categories;
- enough room geometry to create partial observability.

Realism constraints:

- furniture rests on the floor;
- wall-mounted objects are attached to walls;
- target object is reachable or visible from a reachable pose;
- the path does not cross walls, furniture, or closed doors unless interaction is explicitly enabled.

Required motion primitives:

- rotate to search;
- move through free space;
- correct heading toward the target or target region;
- stop when target is visible enough for annotation.

Required viewpoint bins:

```text
distance to target: far, middle, near
target bearing: left, center, right
visibility state: not visible, partially visible, clearly visible
room progress: start region, transition region, target region
```

Coverage pass condition:

- episode includes not-visible, partially visible, and clearly visible target states when possible;
- path length is above the minimum for the room size;
- target is visible in final frames;
- action sequence contains both rotation and translation.

Failure reasons:

- `target_unreachable`;
- `target_never_visible`;
- `path_too_short`;
- `stuck_policy`;
- `insufficient_search_views`.

## Scenario Coverage Score

Per-scenario comprehensiveness is measured inside each episode and then summarized across a run.

Model:

```text
scenario_coverage_score =
  w_view * viewpoint_bin_coverage
  + w_motion * required_motion_coverage
  + w_visibility * required_visibility_event_coverage
  + w_object * required_object_coverage
```

Default weights for phase one:

| Parameter | Value | Meaning | If too low | If too high |
|---|---:|---|---|---|
| `w_view` | 0.35 | required viewpoint bins matter most | repeated narrow views pass | generator over-optimizes camera grid |
| `w_motion` | 0.25 | required motion primitives must happen | static scans pass | unnatural movement can pass only for motion |
| `w_visibility` | 0.25 | disappear-reappear and target visibility matter | no hidden-state pressure | hard occlusion may dominate |
| `w_object` | 0.15 | required objects must exist and be seen | wrong scenario content passes | object checklist dominates motion |

Pass condition:

- `scenario_coverage_score >= 0.75`;
- no required hard constraint failed.

Insufficient evidence condition:

- simulator metadata cannot determine one required bin or event.

Failure condition:

- `scenario_coverage_score < 0.75`;
- any hard realism constraint fails;
- required object, motion, or visibility event is missing.

## Realism Score

Realism is not photorealism alone. For phase one, realism means the scene obeys real-world geometry,
scale, object relations, state rules, and navigability.

Model:

```text
realism_score =
  w_scale * scale_validity
  + w_support * support_validity
  + w_collision * collision_validity
  + w_relation * semantic_relation_validity
  + w_state * state_validity
  + w_light * lighting_validity
```

Pass condition:

- `realism_score >= 0.85`;
- no hard collision, support, or reachability failure.

Examples of hard failures:

- mug floats above desk;
- keyboard intersects monitor;
- knife floats vertically in air;
- drawer is labeled open but geometry is closed;
- target object exists but cannot be seen from any reachable pose.

## Diversity Score

Cross-scenario diversity is measured across a run, not inside one episode. It asks whether the
dataset covers different scenario cards and different values inside each scenario card.

Model:

```text
diversity_score =
  mean coverage over required run-level bins
```

Required run-level bins:

- scenario card;
- room or surface layout;
- object category;
- object instance;
- object size bin;
- object color bin;
- object texture bin;
- object state;
- lighting profile;
- policy family;
- trajectory family.

Pass condition:

- every required scenario card reaches its minimum episode count;
- every required bin has at least the configured minimum count;
- near-duplicate rate is below the configured threshold.

Failure condition:

- one scenario dominates the run;
- many seeds generate visually or structurally identical episodes;
- diversity is mostly color or texture changes without layout, object, or trajectory changes.

## Physical Priors, Models, And Implementation Contracts

### Prior 1: Egocentric Motion Changes What Is Knowable

Physical prior:

An agent's camera motion changes which surfaces and objects are visible. The same scene can be easy
or hard depending on the trajectory.

Model:

```text
episode = (o_1, a_1, o_2, ..., a_T, o_{T+1})
belief_t = f(belief_{t-1}, observation_t, action_{t-1})
```

Metric:

```text
trajectory_action_entropy = H(action)
pose_path_length = sum_t distance(pose_t, pose_{t+1})
viewpoint_coverage = unique_view_bins / possible_view_bins
```

Implementation contract:

- `trajectory.parquet` must contain frame index, action, and camera pose.
- The validator must reject episodes with too little motion.
- The dashboard must show action histogram and pose path length distribution.

Pass condition:

- each policy family has nonzero action entropy;
- scripted scan and target search episodes have higher viewpoint coverage than static or near-static
  episodes.

Failure condition:

- many episodes repeat the same view;
- action labels change but camera pose does not;
- motion is too random to inspect meaningful hidden state.

### Prior 2: Hidden State Requires Partial Observability

Physical prior:

A robot does not see the whole room at once. It must remember objects after looking away and infer
objects behind occluders.

Model:

```text
visibility_{t,k} = 1 if object k is visible at time t else 0
reappearance_gap_k = max number of frames where object k exists but is not visible before reappearing
```

Metric:

```text
occlusion_event_rate = episodes_with_visibility_drop_and_reappearance / episodes
mean_reappearance_gap = mean reappearance_gap_k over objects
hidden_object_count = count objects that exist but are not visible at frame t
```

Implementation contract:

- frame records must include visible object instances.
- scene records must include full object instances, not only visible objects.
- the quality checker must compute visibility timelines per object.

Pass condition:

- a target share of episodes contain at least one object that disappears and reappears;
- object permanence examples exist in train and validation splits.

Failure condition:

- most objects are either always visible or never visible;
- object identity is not stable across frames;
- the dataset cannot tell whether a hidden object still exists.

### Prior 3: Object And Scene Variety Must Be Controlled

Physical prior:

Embodied models should not learn one desk, one kitchen, one object placement pattern, or one texture
style. Variation must cover object type, shape, size, color, texture, layout, support relation, and
state.

Model:

```text
z = (
  scenario_family,
  room_or_surface_layout,
  object_category_set,
  object_instance_set,
  object_size_bin,
  object_color_bin,
  object_texture_bin,
  object_state,
  lighting_profile,
  policy_family
)
```

Metric:

```text
coverage(variable) = occupied_bins(variable) / target_bins(variable)
entropy(variable) = H(variable)
long_tail_min_count(variable) = min count over required bins
cooccurrence_coverage = occupied object-pair bins / target object-pair bins
```

Implementation contract:

- manifests must record scenario family, scene seed, episode seed, policy, object categories,
  object instances, size bins, color bins, texture bins, state bins, and lighting profile.
- splits must be made by scene, layout, object instance, and scenario family, never by adjacent
  frames.

Pass condition:

- required bins have minimum counts before large-scale generation continues;
- validation-unseen-object and validation-unseen-layout splits contain variables absent from train.

Failure condition:

- high frame count comes from repeated near-duplicate scenes;
- color or texture changes hide lack of layout and trajectory diversity;
- split leakage lets adjacent or nearly identical episodes appear in train and validation.

### Prior 4: Validity Is A Dataset Metric, Not A Cleanup Step

Physical prior:

Invalid scenes teach wrong physical and semantic relations. A mug floating above a table, a keyboard
inside a monitor, or a target object outside the navigable area damages the learning signal.

Model:

```text
validity_score =
  w_collision * collision_score
  + w_support * support_score
  + w_semantic * semantic_relation_score
  + w_navigation * navigation_score
  + w_visibility * visibility_score
```

Metric:

```text
scene_accept_rate = accepted_scenes / proposed_scenes
episode_accept_rate = accepted_episodes / proposed_episodes
rejection_reason_histogram = count by reason
```

Implementation contract:

- every scene and episode validator must emit pass, fail, or uncertain.
- every rejection must name a reason.
- rejection counts must be written to a run report.

Pass condition:

- rejection reasons are measurable and inspectable;
- a small manual review agrees with automatic validity labels often enough to trust scaling.

Failure condition:

- invalid episodes pass silently;
- many valid episodes are rejected for unclear reasons;
- rejection reasons do not map to fixable generator stages.

### Prior 5: Throughput Determines Research Iteration Speed

Physical prior:

If generation is slow, we cannot test enough seeds, policies, and variations. Fast generation is part
of the scientific method because it lets us falsify dataset assumptions quickly.

Model:

```text
frames_per_second = generated_frames / wall_time_seconds
valid_frames_per_second = accepted_frames / wall_time_seconds
cost_per_million_frames = compute_cost / accepted_million_frames
```

Metric:

```text
scene_sampling_time
simulation_time
render_time
annotation_time
write_time
validation_time
valid_frames_per_second
storage_gb_per_million_frames
```

Implementation contract:

- generator runs must write stage timing.
- remote 5090 runs must record GPU name, CPU count, worker count, render profile, resolution, and
  storage path.
- the dashboard must separate raw frames per second from valid frames per second.

Pass condition:

- remote schema smoke tests finish in minutes;
- remote fast-profile generation reaches enough valid frames per second to make million-frame
  experiments practical;
- high-fidelity rendering is used only when the fast profile has already answered a research
  question or exposes a domain-transfer question.

Failure condition:

- throughput is reported without rejection rate;
- rendering dominates before the fast profile is scientifically tested;
- storage write speed becomes the hidden bottleneck.

## Key Dataset Metrics

### Research Value Metrics

These metrics decide whether the dataset can train the intended embodied AI models.

| Metric | Definition | Required evidence |
|---|---|---|
| action-conditioning gain | action-conditioned baseline minus passive and static baselines | held-out evaluation table |
| object permanence support | rate of disappear-reappear object events | visibility timelines and examples |
| viewpoint coverage | unique camera pose bins visited per episode | pose plots and histogram |
| hidden-state pressure | count of frames where task-relevant objects exist but are not visible | object existence vs visibility table |
| goal evidence quality | target visibility before, during, and after movement | target visibility timeline |

### Variety Metrics

These metrics decide whether generated data covers the intended variable space.

| Metric | Definition | Required evidence |
|---|---|---|
| scenario coverage | counts for desk, kitchen, room-to-object, future families | manifest histogram |
| object category coverage | occupied object category bins | object histogram |
| object instance coverage | unique assets per category | asset manifest |
| size coverage | occupied size bins per category | asset measurements |
| color coverage | occupied color bins per category | material metadata or image estimate |
| texture coverage | occupied material/texture bins | material metadata |
| layout coverage | occupied layout bins or layout cluster ids | scene manifest |
| state coverage | open, closed, filled, empty, upright, fallen, etc. | object-state metadata |
| policy coverage | random scan, scripted scan, target search, navigation | episode manifest |
| trajectory coverage | path length, turn count, camera-height bins, pitch/yaw bins | trajectory table |

### Validity Metrics

These metrics decide whether generated episodes are safe to train on.

| Metric | Definition | Required evidence |
|---|---|---|
| collision rejection rate | rejected scenes due to mesh/object overlap | validator report |
| support relation validity | objects placed on plausible support surfaces | sampled scene examples |
| navigation validity | target reachable from start pose | navigation check report |
| camera clipping rate | frames where camera intersects geometry | episode validator |
| blank/degenerated frame rate | blank, extreme exposure, or missing render frames | frame validator |
| label completeness | share of frames with all requested labels | annotation report |

### Generation Metrics

These metrics decide whether the pipeline can support fast research loops.

| Metric | Definition | Required evidence |
|---|---|---|
| raw frames per second | all generated frames divided by wall time | run log |
| valid frames per second | accepted frames divided by wall time | run log plus rejection counts |
| stage time share | time split by sampling, simulation, rendering, writing, validation | profiler report |
| storage per million frames | output size normalized by frame count | filesystem measurement |
| remote reproducibility | same seed generates same metadata and compatible frame count | local vs remote smoke test |

## Two-Step Generation Process

Step 1: fast embodied rollout generation.

Purpose:

- generate many valid episodes;
- test action-conditioned learning;
- measure variety, visibility, and trajectory coverage;
- find generator failures early.

Default backend:

- ProcTHOR / AI2-THOR for real scenes;
- mock backend only for schema and remote smoke tests.

Default output:

- RGB-D;
- semantic and instance masks;
- pose;
- action;
- object visibility;
- timing and validation reports.

Step 2: high-fidelity rendering subset.

Purpose:

- test whether models trained on fast-rendered data transfer to richer visual domains;
- create smaller visual validation and adaptation sets;
- study appearance variables such as material, lighting, texture, reflections, and sensor artifacts.

Default backend:

- BlenderProc or Infinigen Indoors first;
- Isaac Sim Replicator only when robotics-grade sensors or manipulation become central.

Pass condition for moving from step 1 to step 2:

- the fast dataset has valid episodes;
- action-conditioned baselines show measurable gain or reveal a clear failure mode;
- high-fidelity rendering is tied to a specific transfer or appearance question.

## Claim Boundary

This design does not yet claim that the dataset will improve real robot performance. The current
claim is narrower:

The dataset is good enough for phase-one research if it produces valid, varied, reproducible
egocentric episodes that can falsify whether action-conditioned training improves hidden-state
learning over static and passive baselines.

The next uncertainty is how much partial observability and trajectory diversity we can produce with
the first real ProcTHOR desk backend before needing custom tabletop generation.
