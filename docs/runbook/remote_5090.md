# Remote 5090 Runbook

## Rule

All simulator tests, smoke tests, preview generation, and dataset generation should run on the
remote RTX 5090 server. Local commands are for editing code and static checks only.

Default GPU reservation:

```text
CUDA_VISIBLE_DEVICES=4,5,6,7
```

This leaves GPUs `0-3` available for other training jobs.

## Environment Variables

Configure the server:

```bash
export EGO5090_HOST="user@host"
export EGO5090_WORKDIR="/path/on/server/egocentric-dataset-toolchain"
export EGO5090_DATASET_ROOT="/path/on/server/datasets/ego_phase1"
export EGO5090_CUDA_VISIBLE_DEVICES="4,5,6,7"
```

Do not commit SSH passwords, tokens, or local auth helper files.

## Remote Setup

```bash
scripts/remote_setup_5090.sh
```

This syncs the repository to the remote workdir, creates a virtual environment, and installs the
package in editable mode.

## Remote Generation Command

```bash
scripts/remote_generate.sh configs/phase1_procthor_smoke.yaml 1 8 procthor_smoke
```

The script runs:

```text
egodata generate
egodata validate
```

on the remote server with the configured CUDA devices.
