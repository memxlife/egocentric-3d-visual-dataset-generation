# Preview Generation

## Purpose

Preview pages provide visual evidence for whether the dataset generator is producing meaningful
egocentric clips. A preview should make failures obvious: empty frames, bad starts, invalid motion,
poor segmentation, weak depth, or copy-forward clips.

## Build Preview On Remote

```bash
ssh "$EGO5090_HOST" \
  "cd '$EGO5090_WORKDIR' && . .venv/bin/activate && egodata preview \
    --dataset '$EGO5090_DATASET_ROOT/procthor_smoke' \
    --output '$EGO5090_DATASET_ROOT/previews/procthor_smoke' \
    --max-episodes 8 --max-frames 12"
```

## Serve Preview Through Tunnel

On the remote server:

```bash
ssh "$EGO5090_HOST" \
  "cd '$EGO5090_DATASET_ROOT/previews/procthor_smoke' && python -m http.server 8899"
```

On the local machine:

```bash
ssh -L 8899:127.0.0.1:8899 "$EGO5090_HOST"
```

Then open:

```text
http://127.0.0.1:8899
```

## Preview Upgrade Target

The preview should eventually show:

- accepted and rejected examples;
- rejection reasons;
- visual-content metrics per frame;
- pose path;
- action or primitive timeline;
- anchor visibility timeline;
- frame-to-frame visual delta;
- first-to-last visual delta.
