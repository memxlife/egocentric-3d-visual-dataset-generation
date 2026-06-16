# Egocentric Embodied Synthetic Dataset Toolchain

This repo is the phase-one implementation workspace for an egocentric visual scanning dataset for
embodied AI research. The checked-in specification starts at
[`docs/spec/README.md`](docs/spec/README.md), with a Codex/browser-friendly viewer at
[`docs/spec/viewer.html`](docs/spec/viewer.html).

The immediate goal is to build a seed-driven dataset generator that can run remote smoke tests and
large generation jobs on the RTX 5090 server.

## Phase-One Scope

Prototype scenario:

- computer desk exploration
- egocentric RGB-D trajectories
- action labels, camera poses, semantic/instance masks
- scene and episode seeds for exact regeneration
- quality checks and manifests from the first run

The first backend in this repo is `mock`, which creates deterministic synthetic episodes with
the same file layout as the real generator. It is intentionally simple so we can test schema,
sharding, validation, and remote job orchestration before installing heavier simulators.

## Remote-First Quick Start

All smoke tests and dataset generation runs should execute on the remote RTX 5090 server. Local
commands are for editing code and static checks only; do not treat local generated data as research
evidence.

Configure the server:

```bash
export EGO5090_HOST="user@host"
export EGO5090_WORKDIR="/path/on/server/egocentric-dataset-toolchain"
export EGO5090_DATASET_ROOT="/path/on/server/datasets/ego_phase1"
export EGO5090_CUDA_VISIBLE_DEVICES="4,5,6,7"
```

Run setup and the scenario-card smoke test:

```bash
scripts/remote_setup_5090.sh
scripts/remote_generate.sh configs/phase1_desk_mock.yaml 4 12 scenario_smoke
```

After AI2-THOR is installed on the remote server, run the real simulator smoke:

```bash
scripts/remote_generate.sh configs/phase1_ai2thor_smoke.yaml 1 8 ai2thor_smoke
```

After ProcTHOR is available through `prior`, run the procedural-house smoke:

```bash
scripts/remote_generate.sh configs/phase1_procthor_smoke.yaml 1 8 procthor_smoke
```

Build a static visual preview on the remote server:

```bash
ssh "$EGO5090_HOST" \
  "cd '$EGO5090_WORKDIR' && . .venv/bin/activate && egodata preview \
    --dataset '$EGO5090_DATASET_ROOT/procthor_smoke' \
    --output '$EGO5090_DATASET_ROOT/previews/procthor_smoke' \
    --max-episodes 8 --max-frames 12"
```

Serve the preview from the remote server and access it through an SSH tunnel:

```bash
ssh "$EGO5090_HOST" \
  "cd '$EGO5090_DATASET_ROOT/previews/procthor_smoke' && python -m http.server 8899"

ssh -L 8899:127.0.0.1:8899 "$EGO5090_HOST"
```

Then open `http://127.0.0.1:8899`.

Expected remote output layout:

```bash
${EGO5090_DATASET_ROOT}/scenario_smoke/
  metadata/
    dataset_manifest.jsonl
    scene_manifest.jsonl
    episode_manifest.jsonl
    action_space.json
    object_taxonomy.json
    scenario_card.json
    run_report.json
  episodes/
    episode_000000000/
      episode.json
      trajectory.parquet
      frames/
        000000.rgb.webp
        000000.depth.png
        000000.semantic.png
        000000.instance.png
```

Once SSH details are known, the same workflow can install `.[ai2thor]` and run a ProcTHOR backend.

## Architecture

The repo mirrors the proposal's five modules:

- scene sampler: config and backend seed inputs
- validity checker: scene/episode/dataset QC
- episode policy engine: random/scripted/target-search action streams
- renderer/annotator: backend-specific observation generation
- dataset writer: manifests, episode folders, frame files, trajectory tables

The stable API is:

```python
generate_episode(scene_seed, episode_seed, scenario_family, policy, render_profile)
```

Backends must return episode frames plus diagnostics; writers and validators stay backend-agnostic.
