from pathlib import Path
import logging
from typing import Optional, Tuple

import numpy
import wasabi.tables

from ._util import app, Arg, Opt, import_code, setup_gpu
from .. import util
from ..pipeline import MultiLabel_TextCategorizer, Pipe
from ..tokens import DocBin

_DEFAULTS = {"average": "micro", "n_trials": 10, "beta": 1, "use_gpu": -1}


@app.command(
    "find-threshold",
    context_settings={"allow_extra_args": False, "ignore_unknown_options": True},
)
def find_threshold_cli(
    # fmt: off
    model: str = Arg(..., help="Model name or path"),
    data_path: Path = Arg(..., help="Location of binary evaluation data in .spacy format", exists=True),
    pipe_name: str = Opt(..., "--pipe_name", "-p", help="Name of pipe to examine thresholds for"),
    average: str = Arg(_DEFAULTS["average"], help="How to aggregate F-scores over labels. One of ('micro', 'macro')", exists=True, allow_dash=True),
    n_trials: int = Opt(_DEFAULTS["n_trials"], "--n_trials", "-n", help="Number of trials to determine optimal thresholds"),
    beta: float = Opt(_DEFAULTS["beta"], "--beta", help="Beta for F1 calculation. Ignored if different metric is used"),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    use_gpu: int = Opt(_DEFAULTS["use_gpu"], "--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    verbose: bool = Opt(False, "--silent", "-V", "-VV", help="Display more information for debugging purposes"),
    # fmt: on
):
    """
    Runs prediction trials for `textcat` models with varying tresholds to maximize the specified metric from CLI.
    model (Path): Path to file with trained model.
    data_path (Path): Path to file with DocBin with docs to use for threshold search.
    pipe_name (str): Name of pipe to examine thresholds for.
    average (str): How to average F-scores across labels. One of ('micro', 'macro').
    n_trials (int): Number of trials to determine optimal thresholds
    beta (float): Beta for F1 calculation.
    code_path (Optional[Path]): Path to Python file with additional code (registered functions) to be imported.
    use_gpu (int): GPU ID or -1 for CPU.
    silent (bool): Display more information for debugging purposes
    """

    util.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    import_code(code_path)
    find_threshold(
        model,
        data_path,
        pipe_name=pipe_name,
        average=average,
        n_trials=n_trials,
        beta=beta,
        use_gpu=use_gpu,
        silent=False,
    )


def find_threshold(
    model: str,
    data_path: Path,
    *,
    pipe_name: str,  # type: ignore
    average: str = _DEFAULTS["average"],  # type: ignore
    n_trials: int = _DEFAULTS["n_trials"],  # type: ignore
    beta: float = _DEFAULTS["beta"],  # type: ignore,
    use_gpu: int = _DEFAULTS["use_gpu"],
    silent: bool = True,
) -> Tuple[float, float]:
    """
    Runs prediction trials for `textcat` models with varying tresholds to maximize the specified metric.
    model (Union[str, Path]): Path to file with trained model.
    data_path (Union[str, Path]): Path to file with DocBin with docs to use for threshold search.
    pipe_name (str): Name of pipe to examine thresholds for.
    average (str): How to average F-scores across labels. One of ('micro', 'macro').
    n_trials (int): Number of trials to determine optimal thresholds.
    beta (float): Beta for F1 calculation.
    use_gpu (int): GPU ID or -1 for CPU.
    silent (bool): Whether to print non-error-related output to stdout.
    RETURNS (Tuple[float, float]): Best found threshold with corresponding F-score.
    """

    setup_gpu(use_gpu, silent=silent)
    data_path = util.ensure_path(data_path)
    if not data_path.exists():
        wasabi.msg.fail("Evaluation data not found", data_path, exits=1)
    nlp = util.load_model(model)
    pipe: Optional[Pipe] = None
    selected_pipe_name: Optional[str] = pipe_name

    if average not in ("micro", "macro"):
        wasabi.msg.fail(
            "Expected 'micro' or 'macro' for F-score averaging method, received '{avg_method}'.",
            exits=1,
        )

    for _pipe_name, _pipe in nlp.pipeline:
        # todo instead of instance check, assert _pipe has a .threshold arg
        #   won't work, actually. e.g. spancat doesn't .threshold.
        if _pipe_name == pipe_name:
            if not isinstance(_pipe, MultiLabel_TextCategorizer):
                wasabi.msg.fail(
                    "Specified component '{component}' is not of type `MultiLabel_TextCategorizer`.".format(
                        component=pipe_name
                    ),
                    exits=1,
                )
            pipe = _pipe
            break

    if pipe is None:
        wasabi.msg.fail(
            f"No component with name {pipe_name} found in pipeline.", exits=1
        )
    # This is purely for MyPy. Type checking is done in loop above already.
    assert isinstance(pipe, MultiLabel_TextCategorizer)

    if silent:
        print(
            f"Searching threshold with the best {average} F-score for component '{selected_pipe_name}' with {n_trials} "
            f"trials and beta = {beta}."
        )

    thresholds = numpy.linspace(0, 1, n_trials)
    # todo use Scorer.score_cats. possibly to be extended?
    ref_pos_counts = {label: 0 for label in pipe.labels}
    pred_pos_counts = {
        t: {True: ref_pos_counts.copy(), False: ref_pos_counts.copy()}
        for t in thresholds
    }
    f_scores_per_label = {t: {label: 0.0 for label in pipe.labels} for t in thresholds}
    f_scores = {t: 0.0 for t in thresholds}

    # Count true/false positives for provided docs.
    doc_bin = DocBin()
    doc_bin.from_disk(data_path)
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
                if label not in pipe.labels:
                    continue
                label_value = int(score >= threshold)
                if label_value == ref_doc.cats[label] == 1:
                    pred_pos_counts[threshold][True][label] += 1
                elif label_value == 1 and ref_doc.cats[label] == 0:
                    pred_pos_counts[threshold][False][label] += 1

    # Compute F-scores.
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

    best_threshold = max(f_scores.keys(), key=(lambda key: f_scores[key]))
    if silent:
        print(
            f"Best threshold: {round(best_threshold, ndigits=4)} with F-score of {f_scores[best_threshold]}.",
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

    return best_threshold, f_scores[best_threshold]
