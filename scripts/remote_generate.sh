#!/usr/bin/env bash
set -euo pipefail

: "${EGO5090_HOST:?Set EGO5090_HOST, for example user@host}"
: "${EGO5090_WORKDIR:?Set EGO5090_WORKDIR on the remote server}"
: "${EGO5090_DATASET_ROOT:?Set EGO5090_DATASET_ROOT on the remote server}"

EGO5090_CUDA_VISIBLE_DEVICES="${EGO5090_CUDA_VISIBLE_DEVICES:-4,5,6,7}"
CONFIG_PATH="${1:-configs/phase1_desk_mock.yaml}"
EPISODES="${2:-10}"
FRAMES="${3:-24}"
RUN_NAME="${4:-phase1_$(date +%Y%m%d_%H%M%S)}"
REMOTE_OUTPUT="${EGO5090_DATASET_ROOT}/${RUN_NAME}"

ssh "${EGO5090_HOST}" "cd '${EGO5090_WORKDIR}' && . .venv/bin/activate && CUDA_VISIBLE_DEVICES='${EGO5090_CUDA_VISIBLE_DEVICES}' egodata generate --config '${CONFIG_PATH}' --output '${REMOTE_OUTPUT}' --episodes '${EPISODES}' --frames '${FRAMES}' && egodata validate --dataset '${REMOTE_OUTPUT}'"
