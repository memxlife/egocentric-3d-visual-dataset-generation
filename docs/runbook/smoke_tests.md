# Smoke Tests

## Purpose

Smoke tests verify that the pipeline can generate, validate, reject, preview, and store short clips
before any large dataset run.

## Remote-Only Rule

Run smoke tests on the remote RTX 5090 server. Do not treat local generated data as research
evidence.

## Mock Backend Smoke

```bash
scripts/remote_generate.sh configs/phase1_desk_mock.yaml 4 12 scenario_smoke
```

Pass condition:

- episode folders are written;
- manifests are written;
- validation passes;
- frame files and trajectory table exist.

## AI2-THOR Smoke

```bash
scripts/remote_generate.sh configs/phase1_ai2thor_smoke.yaml 1 8 ai2thor_smoke
```

Pass condition:

- AI2-THOR CloudRendering starts on the remote server;
- RGB/depth/semantic/instance frames are written;
- validation passes.

## ProcTHOR Smoke

```bash
scripts/remote_generate.sh configs/phase1_procthor_smoke.yaml 1 8 procthor_smoke
```

Pass condition:

- `prior` loads ProcTHOR-10K;
- one procedural house renders;
- visible object metadata is written;
- validation passes.

## Next Diagnostic Smoke

The next smoke should test object-aware starts rather than scale:

```text
5-10 procedural scenes
8-16 candidate starts per scene
1-2 clips per start
32 frames per clip
accepted and rejected previews
```
