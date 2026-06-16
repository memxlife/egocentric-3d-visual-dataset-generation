#!/usr/bin/env bash
set -euo pipefail

: "${EGO5090_HOST:?Set EGO5090_HOST, for example user@host}"
: "${EGO5090_WORKDIR:?Set EGO5090_WORKDIR on the remote server}"

rsync -az --delete \
  --exclude .git \
  --exclude .venv \
  --exclude runs \
  ./ "${EGO5090_HOST}:${EGO5090_WORKDIR}/"

ssh "${EGO5090_HOST}" "cd '${EGO5090_WORKDIR}' && python3 -m venv .venv && . .venv/bin/activate && python -m pip install --upgrade pip && python -m pip install -e ."
