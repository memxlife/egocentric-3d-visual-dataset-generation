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

## Documentation

The project separates three document types:

- dataset specification: [`docs/spec/README.md`](docs/spec/README.md)
- implementation roadmap: [`docs/implementation/roadmap.md`](docs/implementation/roadmap.md)
- remote runbooks: [`docs/runbook/remote_5090.md`](docs/runbook/remote_5090.md),
  [`docs/runbook/smoke_tests.md`](docs/runbook/smoke_tests.md), and
  [`docs/runbook/preview_generation.md`](docs/runbook/preview_generation.md)

All smoke tests and dataset generation runs should execute on the remote RTX 5090 server. Local
commands are for editing code and static checks only; do not treat local generated data as research
evidence.

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
