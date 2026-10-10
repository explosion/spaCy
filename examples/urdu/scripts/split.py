"""Split source-grouped records with a fixed seed and no train/dev/test leakage.

If every record has a train/dev/test `split` field, that assignment is kept.
Cross-split duplicates are quarantined instead of reshuffling a benchmark.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def load_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"missing input file: {path}")
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            row = json.loads(raw)
            if "id" not in row or "text" not in row:
                raise ValueError(f"{path}:{line_no}: records need id and text")
            rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no JSONL records")
    return rows


def dedupe(rows: list[dict]) -> tuple[list[dict], int]:
    kept = []
    seen_exact = set()
    seen_near = set()
    dropped = 0
    for row in rows:
        exact = row["text"]
        near = normalize_text(row["text"])
        if exact in seen_exact or near in seen_near:
            dropped += 1
            continue
        seen_exact.add(exact)
        seen_near.add(near)
        kept.append(row)
    return kept, dropped


def source_id(row: dict) -> str:
    return row.get("source_id") or row["id"]


def split_groups(
    rows: list[dict],
    *,
    seed: int,
    train_frac: float,
    dev_frac: float,
) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[source_id(row)].append(row)
    keys = sorted(groups)
    rng = random.Random(seed)
    rng.shuffle(keys)
    n = len(keys)
    n_train = int(n * train_frac)
    n_dev = int(n * dev_frac)
    train_keys = set(keys[:n_train])
    dev_keys = set(keys[n_train : n_train + n_dev])
    test_keys = set(keys[n_train + n_dev :])
    if n and not test_keys:
        # Keep a non-empty held-out set when possible.
        if n >= 3 and train_keys:
            moved = keys[n_train + n_dev - 1] if n_dev else keys[-1]
            test_keys.add(moved)
            train_keys.discard(moved)
            dev_keys.discard(moved)
    splits = {"train": [], "dev": [], "test": []}
    for key, items in groups.items():
        if key in train_keys:
            splits["train"].extend(items)
        elif key in dev_keys:
            splits["dev"].extend(items)
        else:
            splits["test"].extend(items)
    return splits


def official_split_mode(rows: list[dict]) -> bool:
    marked = sum("split" in row for row in rows)
    if marked == 0:
        return False
    if marked != len(rows):
        raise ValueError(
            "some records have a split field and some do not; "
            "refusing to mix official and random splits"
        )
    return True


def _assign_official(rows: list[dict]) -> dict[str, list[dict]]:
    splits = {"train": [], "dev": [], "test": []}
    unknown = []
    for row in rows:
        name = row["split"]
        if name not in splits:
            unknown.append((row["id"], name))
            continue
        splits[name].append(row)
    if unknown:
        raise ValueError(f"unknown split values: {unknown[:5]}")
    return splits


def _contaminated_ids(splits: dict[str, list[dict]]) -> set[str]:
    near_to_splits: dict[str, set[str]] = defaultdict(set)
    near_rows: dict[str, list[dict]] = defaultdict(list)
    source_to_splits: dict[str, set[str]] = defaultdict(set)
    for name, items in splits.items():
        for row in items:
            near = normalize_text(row["text"])
            near_to_splits[near].add(name)
            near_rows[near].append(row)
            source_to_splits[source_id(row)].add(name)
    contaminated = set()
    for near, names in near_to_splits.items():
        if len(names) > 1:
            contaminated.update(row["id"] for row in near_rows[near])
    for sid, names in source_to_splits.items():
        if len(names) > 1:
            for items in splits.values():
                for row in items:
                    if source_id(row) == sid:
                        contaminated.add(row["id"])
    return contaminated


def preserve_official_splits(
    rows: list[dict],
) -> tuple[dict[str, list[dict]], list[dict]]:
    splits = _assign_official(rows)
    contaminated_ids = _contaminated_ids(splits)
    quarantined = []
    cleaned = {"train": [], "dev": [], "test": []}
    for name, items in splits.items():
        seen_near = set()
        for row in items:
            near = normalize_text(row["text"])
            if row["id"] in contaminated_ids or near in seen_near:
                quarantined.append(row)
                continue
            seen_near.add(near)
            cleaned[name].append(row)
    return cleaned, quarantined


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--train-frac", type=float, default=0.8)
    parser.add_argument("--dev-frac", type=float, default=0.1)
    parser.add_argument(
        "--preserve-official-splits",
        action="store_true",
        help="Require a split field on every record (also auto-detected).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.train_frac + args.dev_frac >= 1.0:
        raise SystemExit("train-frac + dev-frac must be < 1 so test stays held out")
    rows = load_jsonl(args.jsonl)
    official = official_split_mode(rows)
    if args.preserve_official_splits and not official:
        raise SystemExit(
            "preserve-official-splits requires a split field on every record"
        )
    quarantined: list[dict] = []
    dropped = 0
    if official:
        splits, quarantined = preserve_official_splits(rows)
        mode = "official"
    else:
        rows, dropped = dedupe(rows)
        splits = split_groups(
            rows, seed=args.seed, train_frac=args.train_frac, dev_frac=args.dev_frac
        )
        mode = "source-grouped"
    checksum = hashlib.sha256(
        json.dumps(
            {name: [row["id"] for row in items] for name, items in splits.items()},
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()[:12]
    for name, items in splits.items():
        write_jsonl(args.out_dir / f"{name}.jsonl", items)
    if quarantined:
        write_jsonl(args.out_dir / "contaminated.jsonl", quarantined)
    print(
        f"mode={mode} seed={args.seed} dropped_dupes={dropped} "
        f"quarantined={len(quarantined)} "
        f"train={len(splits['train'])} dev={len(splits['dev'])} "
        f"test={len(splits['test'])} id_checksum={checksum}"
    )


if __name__ == "__main__":
    main()
