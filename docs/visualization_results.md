# Visualization And Results

## Current State

Real simulator smoke datasets have been generated on the remote server. The current viewer target is
a static HTML preview generated from a dataset folder. This preview is for visual QA only; it does
not replace metric validation or learning experiments.

## Required Viewer

The first dataset viewer is `egodata preview`. It should show both aggregate metrics and examples.
It must explain what each visual artifact proves and what it does not prove.

## Panels

### Panel 1: Dataset Run Summary

Data source:

- `metadata/dataset_manifest.jsonl`;
- run timing report.

Should show:

- scenes proposed;
- scenes accepted;
- episodes proposed;
- episodes accepted;
- frames written;
- raw frames per second;
- valid frames per second;
- output size.

Interpretation:

- this panel proves whether generation is fast enough to support iteration;
- it does not prove that episodes contain useful hidden-state structure.

### Panel 2: Rejection Reason Histogram

Data source:

- scene and episode validator reports.

Should show:

- count by rejection reason;
- rejection share by stage.

Interpretation:

- this panel identifies which generator stage is blocking scale;
- it does not prove that accepted episodes are semantically rich.

### Panel 3: Variety Coverage

Data source:

- scene manifest;
- episode manifest;
- asset manifest;
- trajectory table.

Should show:

- object category histogram;
- object instance histogram;
- size/color/texture bins;
- layout bins;
- policy distribution;
- camera-height, yaw, pitch, and path-length distributions.

Interpretation:

- this panel proves which variable bins are occupied;
- it does not prove the combinations are realistic unless paired with visual examples.

### Panel 4: Visibility Timeline

Data source:

- per-frame visible object records;
- full scene object records.

Should show:

- object identity on the y-axis;
- frame index on the x-axis;
- visible/not visible state;
- action labels below the timeline.

Interpretation:

- this panel proves whether an episode contains object permanence events;
- it does not prove that a model can learn those events.

### Panel 5: Egocentric Contact Sheet

Data source:

- RGB frames;
- depth frames;
- semantic masks;
- instance masks.

Should show:

- selected frames from the same episode;
- action and pose under each frame;
- visible target objects.

Interpretation:

- this panel lets a human check whether movement and labels match the visual sequence;
- it does not replace aggregate validity metrics.

### Panel 6: Learning Baseline Table

Data source:

- baseline training logs.

Should show:

- static frame model score;
- passive temporal model score;
- action-conditioned model score;
- held-out scene score;
- held-out object score;
- object permanence score.

Interpretation:

- this panel tests the main research conjecture;
- it is only valid if train and validation splits are episode-level and leakage-free.

## Results Ledger

### 2026-06-15 Local Mock Code Check

What was tested:

- package install;
- `egodata generate`;
- `egodata validate`;
- mock RGB/depth/semantic/instance frame writing;
- episode and scene manifests.

Evidence:

- generated 3 episodes;
- generated 36 frames;
- validator returned `valid: true`;
- no missing files were reported.

What passed:

- local schema writing;
- local dataset validation;
- basic episode manifest creation.

What failed:

- no real simulator was used;
- no real physics, object placement, occlusion, or rendering quality was tested;
- no throughput profile was recorded.

Conclusion:

- the schema smoke path is ready as code;
- this is not dataset evidence because it did not run on the remote server;
- the next result must be a remote 5090 smoke test, followed by the first real ProcTHOR desk backend
  micro-test.

### 2026-06-16 Local Scenario-Card Metric Code Check

What was tested:

- `desk_active_scan_mock` scenario card loading;
- generation speed metric;
- realism metric;
- per-scenario comprehensiveness metric;
- cross-scenario diversity metric;
- episode rejection path with metric failures enabled;
- run report writing.

Evidence:

- generated 4 episodes;
- generated 48 frames;
- validator returned `valid: true`;
- run report wrote valid frames per second;
- each episode manifest row included `four_metrics`.

What passed:

- scenario card was copied to dataset metadata;
- all four metric groups passed for the mock scenario card;
- run-level rejection reasons were recorded.

What failed:

- this still used the mock backend;
- no real-world geometry, support relation, collision, navigability, or photorealism was tested;
- cross-scenario diversity is only episode-level evidence so far, not a full run-level diversity
  audit.

Conclusion:

- the four metric gates are now executable as code;
- this is not dataset evidence because it did not run on the remote server;
- the next concrete test is the same scenario-card smoke run on the remote 5090 server, then a real
  ProcTHOR desk active scan card.

### 2026-06-16 Remote AI2-THOR Backend Smoke Test

What was tested:

- remote AI2-THOR 5.0.0 install;
- remote `CloudRendering` dependency setup;
- Vulkan visibility on the RTX 5090 server;
- `egodata generate` with backend `ai2thor`;
- RGB, depth, semantic, instance, pose, action, and visible-object export;
- four metric gates on a real simulator episode.

Evidence:

- installed `libvulkan1` and `vulkan-tools` on the remote server;
- AI2-THOR controller probe loaded `FloorPlan1_physics`;
- controller probe produced RGB frame shape `256 x 256 x 3`, depth shape `256 x 256`, and 77 scene
  objects;
- `egodata generate` produced 1 accepted episode and 8 frames at
  `/home/zhicheng/datasets/ego_phase1/ai2thor_smoke`;
- validator returned `valid: true`;
- run report showed `valid_frames_per_second = 1.68`;
- episode diagnostics reported zero failed actions.

What passed:

- AI2-THOR can run headlessly with CloudRendering on the remote server;
- the real backend writes the same dataset layout as the mock backend;
- visible object categories are extracted from AI2-THOR metadata;
- all four metric gates were written into the episode manifest and passed for the smoke card.

What failed:

- this was a built-in kitchen scene smoke, not a ProcTHOR procedural desk scene;
- throughput includes controller startup overhead and should not be treated as steady-state speed;
- the smoke card is intentionally permissive and does not test strict desk coverage.

Conclusion:

- the toolchain can now generate real AI2-THOR episodes on the remote server;
- the next concrete test is a stricter multi-episode AI2-THOR run, followed by ProcTHOR scene loading
  and then the strict desk active scan card.

### 2026-06-16 Remote AI2-THOR Stability Smoke

What was tested:

- repeated real AI2-THOR generation through `egodata generate`;
- five controller episodes;
- validation over a 100-frame remote output.

Evidence:

- output path: `/home/zhicheng/datasets/ego_phase1/ai2thor_stability_smoke`;
- generated 5 accepted episodes;
- generated 100 frames;
- validator returned `valid: true`;
- run report showed `valid_frames_per_second = 6.18`;
- rejection count was 0.

Conclusion:

- repeated built-in-scene AI2-THOR generation is stable enough to move to ProcTHOR loading.

### 2026-06-16 Remote ProcTHOR Loading Smoke

What was tested:

- `prior.load_dataset("procthor-10k")`;
- train, validation, and test split availability;
- loading a procedural house into AI2-THOR CloudRendering;
- `egodata generate` with backend `procthor`;
- four metric gates on a procedural house episode.

Evidence:

- ProcTHOR-10K loaded with train length 10,000, validation length 1,000, and test length 1,000;
- a procedural house loaded into AI2-THOR with `scene_name = Procedural`;
- output path: `/home/zhicheng/datasets/ego_phase1/procthor_smoke`;
- generated 1 accepted episode;
- generated 8 frames;
- validator returned `valid: true`;
- visible categories included `Fridge` and `GarbageBag`;
- failed action count was 0;
- run report showed `valid_frames_per_second = 0.91`.

What passed:

- the toolchain can now generate real procedural ProcTHOR episodes on the remote server;
- the dataset layout and four metric payloads work for backend `procthor`.

What failed:

- the smoke scenario is permissive and only proves procedural loading, not desk coverage;
- the current trajectory policy is generic and does not choose camera starts or viewpoints to
  maximize useful object visibility;
- ProcTHOR dataset loading happens inside each run and should be cached at backend process scope for
  throughput.

Conclusion:

- the next concrete test is a ProcTHOR multi-scene smoke with better start/view selection, then the
  strict desk-active-scan scenario.
