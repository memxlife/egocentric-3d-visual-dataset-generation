from __future__ import annotations

import html
import json
import math
import shutil
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


MODALITIES = ["rgb", "depth", "semantic", "instance"]


def build_preview(
    dataset_root: Path,
    output_root: Path,
    max_episodes: int = 12,
    max_frames: int = 12,
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    episodes = _load_episode_manifest(dataset_root)[:max_episodes]
    run_report = _read_json(dataset_root / "metadata" / "run_report.json", default={})
    dataset_manifest = _read_first_jsonl(dataset_root / "metadata" / "dataset_manifest.jsonl")
    episode_summaries = []

    for record in episodes:
        episode_id = record["episode_id"]
        episode_dir = dataset_root / "episodes" / episode_id
        episode = _read_json(episode_dir / "episode.json", default={})
        episode_output = output_root / episode_id
        episode_output.mkdir(parents=True, exist_ok=True)
        frames = episode.get("frames", [])[:max_frames]
        frame_assets = _build_episode_assets(episode_dir, episode_output, frames)
        episode_summaries.append(
            {
                "episode_id": episode_id,
                "policy": episode.get("policy"),
                "scenario_family": episode.get("scenario_family"),
                "frames": len(episode.get("frames", [])),
                "scene_id": episode.get("scene_id"),
                "diagnostics": episode.get("diagnostics", {}),
                "assets": frame_assets,
                "frame_table": _frame_table_rows(frames),
            }
        )

    index_path = output_root / "index.html"
    index_path.write_text(
        _render_html(
            dataset_root=dataset_root,
            run_report=run_report,
            dataset_manifest=dataset_manifest,
            episodes=episode_summaries,
        )
    )
    return {
        "dataset": str(dataset_root),
        "output": str(output_root),
        "index": str(index_path),
        "episodes": len(episode_summaries),
    }


def _build_episode_assets(
    episode_dir: Path,
    output_dir: Path,
    frames: list[dict[str, Any]],
) -> dict[str, str]:
    assets: dict[str, str] = {}
    rgb_images: list[Image.Image] = []
    for modality in MODALITIES:
        images = []
        labels = []
        for frame in frames:
            path = episode_dir / frame[modality]
            if not path.exists():
                continue
            image = _load_preview_image(path, modality)
            images.append(image)
            labels.append(f"{frame['frame_index']:06d}  {frame.get('action', '')}")
            if modality == "rgb":
                rgb_images.append(image.copy())
        if images:
            sheet = _contact_sheet(images, labels)
            filename = f"{modality}_contact_sheet.webp"
            sheet.save(output_dir / filename, "WEBP", quality=86)
            assets[f"{modality}_contact_sheet"] = filename
    if rgb_images:
        animation_frames = [img.resize((256, 256)) for img in rgb_images]
        animation_path = output_dir / "rgb_sequence.webp"
        animation_frames[0].save(
            animation_path,
            "WEBP",
            save_all=True,
            append_images=animation_frames[1:],
            duration=180,
            loop=0,
            quality=85,
        )
        assets["rgb_sequence"] = animation_path.name
    return assets


def _load_preview_image(path: Path, modality: str) -> Image.Image:
    image = Image.open(path)
    if modality == "depth":
        array = np.asarray(image).astype(np.float32)
        if array.max() > array.min():
            array = (array - array.min()) / (array.max() - array.min())
        else:
            array = np.zeros_like(array)
        depth_rgb = np.stack(
            [
                (array * 255),
                (np.sqrt(array) * 220),
                ((1.0 - array) * 120),
            ],
            axis=-1,
        ).clip(0, 255).astype(np.uint8)
        return Image.fromarray(depth_rgb, "RGB")
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image


def _contact_sheet(images: list[Image.Image], labels: list[str]) -> Image.Image:
    thumb_w, thumb_h = 192, 144
    label_h = 24
    columns = min(4, max(1, len(images)))
    rows = math.ceil(len(images) / columns)
    margin = 12
    gap = 10
    width = margin * 2 + columns * thumb_w + (columns - 1) * gap
    height = margin * 2 + rows * (thumb_h + label_h) + (rows - 1) * gap
    sheet = Image.new("RGB", (width, height), (248, 250, 252))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, image in enumerate(images):
        row, col = divmod(index, columns)
        x = margin + col * (thumb_w + gap)
        y = margin + row * (thumb_h + label_h + gap)
        thumb = _fit_image(image, (thumb_w, thumb_h))
        sheet.paste(thumb, (x, y))
        draw.rectangle((x, y, x + thumb_w - 1, y + thumb_h - 1), outline=(203, 213, 225))
        draw.text((x, y + thumb_h + 6), labels[index], fill=(15, 23, 42), font=font)
    return sheet


def _fit_image(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, (226, 232, 240))
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    x = (size[0] - copy.width) // 2
    y = (size[1] - copy.height) // 2
    canvas.paste(copy, (x, y))
    return canvas


def _frame_table_rows(frames: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for frame in frames:
        visible = frame.get("visible_objects", [])
        categories = sorted({str(obj.get("category", "unknown")) for obj in visible})
        pose = frame.get("pose", {})
        rows.append(
            {
                "frame": frame.get("frame_index"),
                "action": frame.get("action"),
                "pose": {
                    "x": _round(pose.get("x")),
                    "y": _round(pose.get("y")),
                    "z": _round(pose.get("z")),
                    "yaw": _round(pose.get("yaw")),
                    "pitch": _round(pose.get("pitch")),
                },
                "visible": ", ".join(categories[:8]),
            }
        )
    return rows


def _render_html(
    dataset_root: Path,
    run_report: dict[str, Any],
    dataset_manifest: dict[str, Any],
    episodes: list[dict[str, Any]],
) -> str:
    cards = "\n".join(_episode_card(ep) for ep in episodes)
    metrics = _metric_tiles(run_report, dataset_manifest, len(episodes))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Egocentric Dataset Preview</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f8fafc;
      --panel: #ffffff;
      --ink: #0f172a;
      --muted: #64748b;
      --line: #dbe3ef;
      --accent: #2563eb;
      --ok: #047857;
      --warn: #b45309;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      padding: 28px 32px 18px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    h1 {{ margin: 0 0 8px; font-size: 28px; line-height: 1.15; letter-spacing: 0; }}
    h2 {{ margin: 0 0 14px; font-size: 19px; letter-spacing: 0; }}
    h3 {{ margin: 18px 0 10px; font-size: 15px; letter-spacing: 0; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
    main {{ padding: 24px 32px 40px; max-width: 1480px; margin: 0 auto; }}
    .subtle {{ color: var(--muted); }}
    .tiles {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin: 20px 0 24px;
    }}
    .tile {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px;
    }}
    .tile .label {{ color: var(--muted); font-size: 12px; }}
    .tile .value {{ margin-top: 5px; font-size: 22px; font-weight: 650; }}
    .episode {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      margin: 0 0 22px;
      padding: 18px;
    }}
    .episode-head {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      border-bottom: 1px solid var(--line);
      padding-bottom: 14px;
      margin-bottom: 16px;
    }}
    .status {{ color: var(--ok); font-weight: 650; }}
    .media-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 14px;
    }}
    figure {{ margin: 0; }}
    figcaption {{ color: var(--muted); font-size: 12px; margin-bottom: 6px; }}
    img {{
      width: 100%;
      height: auto;
      display: block;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #e2e8f0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
      font-size: 12px;
    }}
    th, td {{ text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 650; }}
    details {{ margin-top: 12px; }}
    summary {{ cursor: pointer; color: var(--accent); font-weight: 650; }}
    pre {{
      white-space: pre-wrap;
      overflow-wrap: anywhere;
      background: #0f172a;
      color: #e2e8f0;
      padding: 12px;
      border-radius: 6px;
      max-height: 320px;
      overflow: auto;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Egocentric Dataset Preview</h1>
    <div class="subtle">Dataset: <code>{html.escape(str(dataset_root))}</code></div>
  </header>
  <main>
    {metrics}
    {cards}
  </main>
</body>
</html>
"""


def _metric_tiles(run_report: dict[str, Any], dataset_manifest: dict[str, Any], episode_count: int) -> str:
    values = [
        ("previewed episodes", episode_count),
        ("generated episodes", run_report.get("generated", dataset_manifest.get("episodes", "n/a"))),
        ("frames", run_report.get("frames", dataset_manifest.get("frames", "n/a"))),
        ("rejected", run_report.get("rejected", "n/a")),
        ("valid FPS", _round(run_report.get("valid_frames_per_second"))),
        ("scenario card", run_report.get("scenario_card", dataset_manifest.get("scenario_card", "n/a"))),
    ]
    tiles = "\n".join(
        f'<div class="tile"><div class="label">{html.escape(str(label))}</div><div class="value">{html.escape(str(value))}</div></div>'
        for label, value in values
    )
    return f'<section class="tiles">{tiles}</section>'


def _episode_card(episode: dict[str, Any]) -> str:
    diagnostics = episode.get("diagnostics", {})
    four_metrics = diagnostics.get("four_metrics", {})
    assets_html = _assets_html(episode)
    frame_rows = _frame_rows_html(episode.get("frame_table", []))
    metrics_json = html.escape(json.dumps(four_metrics, indent=2, sort_keys=True))
    diagnostics_json = html.escape(json.dumps(diagnostics, indent=2, sort_keys=True))
    return f"""
<section class="episode">
  <div class="episode-head">
    <div>
      <h2>{html.escape(episode['episode_id'])}</h2>
      <div class="subtle">scene {html.escape(str(episode.get('scene_id')))} · policy {html.escape(str(episode.get('policy')))} · {html.escape(str(episode.get('frames')))} frames</div>
    </div>
    <div class="status">{_metrics_status(four_metrics)}</div>
  </div>
  {assets_html}
  <h3>Frame Actions And Visible Objects</h3>
  {frame_rows}
  <details><summary>Four metric payload</summary><pre>{metrics_json}</pre></details>
  <details><summary>Diagnostics</summary><pre>{diagnostics_json}</pre></details>
</section>
"""


def _assets_html(episode: dict[str, Any]) -> str:
    episode_id = episode["episode_id"]
    labels = {
        "rgb_sequence": "RGB sequence",
        "rgb_contact_sheet": "RGB contact sheet",
        "depth_contact_sheet": "Depth contact sheet",
        "semantic_contact_sheet": "Semantic contact sheet",
        "instance_contact_sheet": "Instance contact sheet",
    }
    figures = []
    for key, label in labels.items():
        filename = episode.get("assets", {}).get(key)
        if not filename:
            continue
        src = f"{episode_id}/{filename}"
        figures.append(
            f'<figure><figcaption>{html.escape(label)}</figcaption><img src="{html.escape(src)}" alt="{html.escape(label)} for {html.escape(episode_id)}"></figure>'
        )
    return f'<div class="media-grid">{"".join(figures)}</div>'


def _frame_rows_html(rows: list[dict[str, Any]]) -> str:
    body = []
    for row in rows:
        pose = row["pose"]
        body.append(
            "<tr>"
            f"<td>{html.escape(str(row['frame']))}</td>"
            f"<td>{html.escape(str(row['action']))}</td>"
            f"<td>x={pose['x']} y={pose['y']} z={pose['z']} yaw={pose['yaw']} pitch={pose['pitch']}</td>"
            f"<td>{html.escape(row['visible'])}</td>"
            "</tr>"
        )
    return (
        "<table><thead><tr><th>frame</th><th>action</th><th>pose</th><th>visible categories</th></tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table>"
    )


def _metrics_status(metrics: dict[str, Any]) -> str:
    if not metrics:
        return "metrics missing"
    failures = [
        name for name, payload in metrics.items() if isinstance(payload, dict) and not payload.get("passed")
    ]
    return "all four gates passed" if not failures else f"failed: {', '.join(failures)}"


def _load_episode_manifest(dataset_root: Path) -> list[dict[str, Any]]:
    path = dataset_root / "metadata" / "episode_manifest.jsonl"
    if not path.exists():
        raise FileNotFoundError(path)
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text())


def _read_first_jsonl(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    for line in path.read_text().splitlines():
        if line.strip():
            return json.loads(line)
    return {}


def _round(value: Any) -> Any:
    if value is None:
        return "n/a"
    try:
        return round(float(value), 3)
    except Exception:
        return value
