from pathlib import Path
import logging
from typing import Optional

import numpy
import wasabi.tables

from ._util import app, Arg, Opt
from .. import util
from ..pipeline import MultiLabel_TextCategorizer
from ..tokens import DocBin

_DEFAULTS = {
    "average": "micro",
    "pipe_name": None,
    "n_trials": 10,
    "beta": 1,
}


@app.command(
    "find-threshold",
    context_settings={"allow_extra_args": False, "ignore_unknown_options": True},
)
def find_threshold_cli(
    # fmt: off
    model_path: Path = Arg(..., help="Path to model file", exists=True, allow_dash=True),
    doc_path: Path = Arg(..., help="Path to doc bin file", exists=True, allow_dash=True),
    average: str = Arg(_DEFAULTS["average"], help="How to aggregate F-scores over labels. One of ('micro', 'macro')", exists=True, allow_dash=True),
    pipe_name: Optional[str] = Opt(_DEFAULTS["pipe_name"], "--pipe_name", "-p", help="Name of pipe to examine thresholds for"),
    n_trials: int = Opt(_DEFAULTS["n_trials"], "--n_trials", "-n", help="Number of trials to determine optimal thresholds"),
    beta: float = Opt(_DEFAULTS["beta"], "--beta", help="Beta for F1 calculation. Ignored if different metric is used"),
    verbose: bool = Opt(False, "--verbose", "-V", "-VV", help="Display more information for debugging purposes"),
    # fmt: on
):
    """
    Runs prediction trials for `textcat` models with varying tresholds to maximize the specified metric from CLI.
    model_path (Path): Path to file with trained model.
    doc_path (Path): Path to file with DocBin with docs to use for threshold search.
    average (str): How to average F-scores across labels. One of ('micro', 'macro').
    pipe_name (Optional[str]): Name of pipe to examine thresholds for. If None, pipe of type MultiLabel_TextCategorizer
        is seleted. If there are multiple, an error is raised.
    n_trials (int): Number of trials to determine optimal thresholds
    beta (float): Beta for F1 calculation. Ignored if different metric is used.
    verbose (bool): Display more information for debugging purposes
    """

    util.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    find_threshold(
        model_path,
        doc_path,
        average=average,
        pipe_name=pipe_name,
        n_trials=n_trials,
        beta=beta,
    )


def find_threshold(
    model_path: Path,
    doc_path: Path,
    *,
    average: str = _DEFAULTS["average"],
    pipe_name: Optional[str] = _DEFAULTS["pipe_name"],
    n_trials: int = _DEFAULTS["n_trials"],
    beta: float = _DEFAULTS["beta"],
) -> None:
    """
    Runs prediction trials for `textcat` models with varying tresholds to maximize the specified metric.
    model_path (Path): Path to file with trained model.
    doc_path (Path): Path to file with DocBin with docs to use for threshold search.
    average (str): How to average F-scores across labels. One of ('micro', 'macro').
    pipe_name (Optional[str]): Name of pipe to examine thresholds for. If None, pipe of type MultiLabel_TextCategorizer
        is seleted. If there are multiple, an error is raised.
    n_trials (int): Number of trials to determine optimal thresholds
    beta (float): Beta for F1 calculation. Ignored if different metric is used.
    """

    nlp = util.load_model(model_path)
    pipe: Optional[MultiLabel_TextCategorizer] = None
    selected_pipe_name: Optional[str] = pipe_name

    if average not in ("micro", "macro"):
        wasabi.msg.fail(
            "Expected 'micro' or 'macro' for F-score averaging method, received '{avg_method}'.",
            exits=1,
        )

    for _pipe_name, _pipe in nlp.pipeline:
        if pipe_name and _pipe_name == pipe_name:
            if not isinstance(_pipe, MultiLabel_TextCategorizer):
                wasabi.msg.fail(
                    "Specified component {component} is not of type `MultiLabel_TextCategorizer`.",
                    exits=1,
                )
            pipe = _pipe
            break
        elif pipe_name is None:
            if isinstance(_pipe, MultiLabel_TextCategorizer):
                if pipe:
                    wasabi.msg.fail(
                        "Multiple components of type `MultiLabel_TextCategorizer` exist in pipeline. Specify name of "
                        "component to evaluate.",
                        exits=1,
                    )
                pipe = _pipe
                selected_pipe_name = _pipe_name

    if pipe is None:
        if pipe_name:
            wasabi.msg.fail(
                f"No component with name {pipe_name} found in pipeline.", exits=1
            )
        wasabi.msg.fail(
            "No component of type `MultiLabel_TextCategorizer` found in pipeline.",
            exits=1,
        )

    print(
        f"Searching threshold with the best {average} F-score for pipe '{selected_pipe_name}' with {n_trials} trials"
        f" and beta = {beta}."
    )

    thresholds = numpy.linspace(0, 1, n_trials)
    ref_pos_counts = {label: 0 for label in pipe.labels}
    pred_pos_counts = {
        t: {True: ref_pos_counts.copy(), False: ref_pos_counts.copy()}
        for t in thresholds
    }
    f_scores_per_label = {t: ref_pos_counts.copy() for t in thresholds}
    f_scores = {t: 0 for t in thresholds}

    # Count true/false positives for provided docs.
    doc_bin = DocBin()
    doc_bin.from_disk(doc_path)
    for ref_doc in doc_bin.get_docs(nlp.vocab):
        for label, score in ref_doc.cats.items():
            if score not in (0, 1):
                wasabi.msg.fail(
                    f"Expected category scores in evaluation dataset to be 0 <= x <= 1, received {score}.",
                    exits=1,
                )
            ref_pos_counts[label] += ref_doc.cats[label] == 1

        pred_doc = nlp(ref_doc.text)
        # Collect count stats per threshold value and label.
        for threshold in thresholds:
            for label, score in pred_doc.cats.items():
                label_value = int(score >= threshold)
                if label_value == ref_doc.cats[label] == 1:
                    pred_pos_counts[threshold][True][label] += 1
                elif label_value == 1 and ref_doc.cats[label] == 0:
                    pred_pos_counts[threshold][False][label] += 1

    # Compute f_scores.
    for threshold in thresholds:
        for label in ref_pos_counts:
            n_pos_preds = (
                pred_pos_counts[threshold][True][label]
                + pred_pos_counts[threshold][False][label]
            )
            precision = (
                (pred_pos_counts[threshold][True][label] / n_pos_preds)
                if n_pos_preds > 0
                else 0
            )
            recall = pred_pos_counts[threshold][True][label] / ref_pos_counts[label]
            f_scores_per_label[threshold][label] = (
                (
                    (1 + beta**2)
                    * (precision * recall / (precision * beta**2 + recall))
                )
                if precision
                else 0
            )

        # Aggregate F-scores.
        if average == "micro":
            f_scores[threshold] = sum(
                [
                    f_scores_per_label[threshold][label] * ref_pos_counts[label]
                    for label in ref_pos_counts
                ]
            ) / sum(ref_pos_counts.values())
        else:
            f_scores[threshold] = sum(
                [f_scores_per_label[threshold][label] for label in ref_pos_counts]
            ) / len(ref_pos_counts)

    best_threshold = max(f_scores, key=f_scores.get)
    print(
        f"Best threshold: {round(best_threshold, ndigits=4)} with F-score of {f_scores[best_threshold]}."
    )
    print(
        wasabi.tables.table(
            data=[
                (threshold, label, f_score)
                for threshold, label_f_scores in f_scores_per_label.items()
                for label, f_score in label_f_scores.items()
            ],
            header=["Threshold", "Label", "F-Score"],
        ),
        wasabi.tables.table(
            data=[(threshold, f_score) for threshold, f_score in f_scores.items()],
            header=["Threshold", f"F-Score ({average})"],
        ),
    )
