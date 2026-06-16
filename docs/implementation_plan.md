# Implementation Plan

## 0. Repo and Smoke Toolchain

Status: started.

Deliverables:

- package install via `pip install -e .`
- `egodata generate` CLI
- deterministic mock backend
- dataset manifests and episode folders
- dataset validator
- remote setup and generation scripts

Success criterion:

- local smoke generation creates valid RGB/depth/semantic/instance/pose/action episodes
- remote script can execute the same command on the 5090 server

## 1. Minimal Desk Generator

Backend target: ProcTHOR / AI2-THOR first, BlenderProc later for high-fidelity subset.

Deliverables:

- 20 desk templates
- constrained desk object taxonomy
- random, scripted scan, and target-search policies
- RGB-D + pose + action export
- semantic and instance masks where supported
- episode-level QC rejection

Initial scale:

- 10,000 short trajectories
- 100,000 to 1,000,000 frames after the schema is stable

## 2. Kitchen Counter Generator

Add counters, cabinets, drawers, object states, and stronger support constraints.

## 3. Room-to-Object Navigation

Use ProcTHOR room/house scenes for object-goal trajectories and held-out layout splits.

## 4. High-Fidelity Subset

Use BlenderProc or Infinigen Indoors for smaller photorealistic validation scenes.

## Engineering Rules

- Episodes, not frames, are the dataset unit.
- All episodes must be reproducible from scene seed, episode seed, backend, policy, and render profile.
- Reject invalid episodes automatically.
- Split at scene/layout/object/task levels, never adjacent frames.
- Keep high-fidelity rendering as a subset until the action-conditioned learning loop is validated.
