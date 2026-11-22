"""Optional runtime measurements for a trained pipeline.

Tiny fixture models are not a production benchmark. Pass a real held-out
sample and report hardware/dependency versions with the numbers.
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import spacy


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((q / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model")
    parser.add_argument("texts", type=Path, help="UTF-8 file, one document per line")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--warmup", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    texts = [
        line.strip()
        for line in args.texts.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    t0 = time.perf_counter()
    nlp = spacy.load(args.model)
    init_s = time.perf_counter() - t0
    for _ in range(args.warmup):
        list(nlp.pipe(texts[: min(len(texts), args.batch_size)]))
    latencies = []
    for text in texts:
        start = time.perf_counter()
        nlp(text)
        latencies.append((time.perf_counter() - start) * 1000)
    start = time.perf_counter()
    n_tok = 0
    for doc in nlp.pipe(texts, batch_size=args.batch_size):
        n_tok += len(doc)
    pipe_s = time.perf_counter() - start
    print(f"model={args.model}")
    print(f"docs={len(texts)} tokens={n_tok} batch_size={args.batch_size}")
    print(f"init_s={init_s:.3f}")
    print(f"pipe_docs_per_s={len(texts) / pipe_s if pipe_s else float('inf'):.1f}")
    print(f"single_ms_p50={percentile(latencies, 50):.2f}")
    print(f"single_ms_p95={percentile(latencies, 95):.2f}")
    if len(texts) < 50:
        print("not a production benchmark: fewer than 50 documents")


if __name__ == "__main__":
    main()
