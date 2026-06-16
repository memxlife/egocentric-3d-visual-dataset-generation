from __future__ import annotations

import argparse
import json
from pathlib import Path

from egodataset.config import load_config
from egodataset.generator import generate_dataset
from egodataset.preview import build_preview
from egodataset.validators import validate_dataset


def main() -> None:
    parser = argparse.ArgumentParser(prog="egodata")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Generate dataset episodes.")
    generate.add_argument("--config", type=Path, required=True)
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--episodes", type=int, required=True)
    generate.add_argument("--frames", type=int, default=None)
    generate.add_argument("--overwrite", action="store_true")

    validate = subparsers.add_parser("validate", help="Validate a generated dataset root.")
    validate.add_argument("--dataset", type=Path, required=True)

    preview = subparsers.add_parser("preview", help="Build a static HTML dataset preview.")
    preview.add_argument("--dataset", type=Path, required=True)
    preview.add_argument("--output", type=Path, required=True)
    preview.add_argument("--max-episodes", type=int, default=12)
    preview.add_argument("--max-frames", type=int, default=12)

    args = parser.parse_args()
    if args.command == "generate":
        cfg = load_config(args.config)
        result = generate_dataset(
            cfg=cfg,
            output=args.output,
            episodes=args.episodes,
            frames=args.frames,
            overwrite=args.overwrite,
        )
    elif args.command == "validate":
        result = validate_dataset(args.dataset)
    elif args.command == "preview":
        result = build_preview(
            dataset_root=args.dataset,
            output_root=args.output,
            max_episodes=args.max_episodes,
            max_frames=args.max_frames,
        )
    else:
        raise AssertionError(args.command)

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
