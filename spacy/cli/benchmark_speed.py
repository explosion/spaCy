import random
import time
from itertools import islice
from pathlib import Path
from typing import Iterable, List, Optional

import numpy
import typer
from tqdm import tqdm
from wasabi import msg

from .. import util
from ..language import Language
from ..tokens import Doc
from ..training import Corpus
from ._util import Arg, Opt, benchmark_cli, setup_gpu


@benchmark_cli.command(
    "speed",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def benchmark_speed_cli(
    # fmt: off
    ctx: typer.Context,
    model: str = Arg(..., help="Model name or path"),
    data_path: Path = Arg(..., help="Location of binary evaluation data in .spacy format", exists=True),
    batch_size: Optional[int] = Opt(None, "--batch-size", "-b", min=1, help="Override the pipeline batch size"),
    no_shuffle: bool = Opt(False, "--no-shuffle", help="Do not shuffle benchmark data"),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    n_batches: int = Opt(50, "--batches", help="Minimum number of batches to benchmark", min=30,),
    warmup_epochs: int = Opt(3, "--warmup", "-w", min=0, help="Number of iterations over the data for warmup"),
    # fmt: on
):
    """
    Benchmark a pipeline. Expects a loadable spaCy pipeline and benchmark
    data in the binary .spacy format.
    """
    setup_gpu(use_gpu=use_gpu, silent=False)

    nlp = util.load_model(model)
    batch_size = batch_size if batch_size is not None else nlp.batch_size
    corpus = Corpus(data_path)
    docs = [eg.predicted for eg in corpus(nlp)]

    if len(docs) == 0:
        msg.fail("Cannot benchmark speed using an empty corpus.", exits=1)

    print(f"Warming up for {warmup_epochs} epochs...")
    warmup(nlp, docs, warmup_epochs, batch_size)

    print()
    print(f"Benchmarking {n_batches} batches...")
    wps = benchmark(nlp, docs, n_batches, batch_size, not no_shuffle)

    print()
    print_outliers(wps)
    print_mean_with_ci(wps)


# Lowercased, behaves as a context manager function.
class time_context:
    """Register the running time of a context."""

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.elapsed = time.perf_counter() - self.start


class Quartiles:
    """Calculate the q1, q2, q3 quartiles and the inter-quartile range (iqr)
    of a sample."""

    q1: float
    q2: float
    q3: float
    iqr: float

    def __init__(self, sample: numpy.ndarray) -> None:
        self.q1 = numpy.quantile(sample, 0.25)
        self.q2 = numpy.quantile(sample, 0.5)
        self.q3 = numpy.quantile(sample, 0.75)
        self.iqr = self.q3 - self.q1


def annotate(
    nlp: Language, docs: List[Doc], batch_size: Optional[int]
) -> numpy.ndarray:
    docs = nlp.pipe(tqdm(docs, unit="doc"), batch_size=batch_size)
    wps = []
    while True:
        with time_context() as elapsed:
            batch_docs = list(
                islice(docs, batch_size if batch_size else nlp.batch_size)
            )
        if len(batch_docs) == 0:
            break
        n_tokens = count_tokens(batch_docs)
        wps.append(n_tokens / elapsed.elapsed)

    return numpy.array(wps)


def benchmark(
    nlp: Language,
    docs: List[Doc],
    n_batches: int,
    batch_size: int,
    shuffle: bool,
) -> numpy.ndarray:
    if shuffle:
        bench_docs = [
            nlp.make_doc(random.choice(docs).text)
            for _ in range(n_batches * batch_size)
        ]
    else:
        bench_docs = [
            nlp.make_doc(docs[i % len(docs)].text)
            for i in range(n_batches * batch_size)
        ]

    return annotate(nlp, bench_docs, batch_size)


def bootstrap(x, statistic=numpy.mean, iterations=10000) -> numpy.ndarray:
    """Apply a statistic to repeated random samples of an array."""
    return numpy.fromiter(
        (
            statistic(numpy.random.choice(x, len(x), replace=True))
            for _ in range(iterations)
        ),
        numpy.float64,
    )


def count_tokens(docs: Iterable[Doc]) -> int:
    return sum(len(doc) for doc in docs)


def print_mean_with_ci(sample: numpy.ndarray):
    mean = numpy.mean(sample)
    bootstrap_means = bootstrap(sample)
    bootstrap_means.sort()

    # 95% confidence interval
    low = bootstrap_means[int(len(bootstrap_means) * 0.025)]
    high = bootstrap_means[int(len(bootstrap_means) * 0.975)]

    print(f"Mean: {mean:.1f} words/s (95% CI: {low-mean:.1f} +{high-mean:.1f})")


def print_outliers(sample: numpy.ndarray):
    quartiles = Quartiles(sample)

    n_outliers = numpy.sum(
        (sample < (quartiles.q1 - 1.5 * quartiles.iqr))
        | (sample > (quartiles.q3 + 1.5 * quartiles.iqr))
    )
    n_extreme_outliers = numpy.sum(
        (sample < (quartiles.q1 - 3.0 * quartiles.iqr))
        | (sample > (quartiles.q3 + 3.0 * quartiles.iqr))
    )
    print(
        f"Outliers: {(100 * n_outliers) / len(sample):.1f}%, extreme outliers: {(100 * n_extreme_outliers) / len(sample)}%"
    )


def warmup(
    nlp: Language, docs: List[Doc], warmup_epochs: int, batch_size: Optional[int]
) -> numpy.ndarray:
    docs = warmup_epochs * docs
    return annotate(nlp, docs, batch_size)
