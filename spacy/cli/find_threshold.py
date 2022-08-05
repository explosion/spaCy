from pathlib import Path
import logging
from typing import Optional

# import numpy

import spacy
from ._util import app, Arg, Opt
from .. import util
from ..pipeline import MultiLabel_TextCategorizer

_DEFAULTS = {
    "aggregation": "weighted",
    "pipe_name": None,
    "n_trials": 10,
    "beta": 1,
    "reverse": False,
}


@app.command(
    "find-threshold",
    context_settings={"allow_extra_args": False, "ignore_unknown_options": True},
)
def find_threshold_cli(
    # fmt: off
    model_path: Path = Arg(..., help="Path to model file", exists=True, allow_dash=True),
    doc_path: Path = Arg(..., help="Path to doc bin file", exists=True, allow_dash=True),
    aggregation: str = Arg(_DEFAULTS["aggregation"], help="How to aggregate F-scores over labels. One of ('micro', 'macro', 'weighted')", exists=True, allow_dash=True),
    pipe_name: Optional[str] = Opt(_DEFAULTS["pipe_name"], "--pipe_name", "-p", help="Name of pipe to examine thresholds for"),
    n_trials: int = Opt(_DEFAULTS["n_trials"], "--n_trials", "-n", help="Number of trials to determine optimal thresholds"),
    beta: float = Opt(_DEFAULTS["beta"], "--beta", help="Beta for F1 calculation. Ignored if different metric is used"),
    reverse: bool = Opt(_DEFAULTS["reverse"], "--reverse", "-r", help="Minimizes metric instead of maximizing it."),
    verbose: bool = Opt(False, "--verbose", "-V", "-VV", help="Display more information for debugging purposes"),
    # fmt: on
):
    """
    Runs prediction trials for `textcat` models with varying tresholds to maximize the specified metric from CLI.
    model_path (Path): Path to file with trained model.
    doc_path (Path): Path to file with DocBin with docs to use for threshold search.
    aggregation (str): How to aggregate F-scores across labels. One of ('micro', 'macro', 'weighted').
    pipe_name (Optional[str]): Name of pipe to examine thresholds for. If None, pipe of type MultiLabel_TextCategorizer
        is seleted. If there are multiple, an error is raised.
    n_trials (int): Number of trials to determine optimal thresholds
    beta (float): Beta for F1 calculation. Ignored if different metric is used.
    reverse (bool): Whether to minimize metric instead of maximizing it.
    verbose (bool): Display more information for debugging purposes
    """

    util.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    find_threshold(
        model_path,
        doc_path,
        aggregation=aggregation,
        pipe_name=pipe_name,
        n_trials=n_trials,
        beta=beta,
        reverse=reverse,
    )


def find_threshold(
    model_path: Path,
    doc_path: Path,
    *,
    aggregation: str = _DEFAULTS["aggregation"],
    pipe_name: Optional[str] = _DEFAULTS["pipe_name"],
    n_trials: int = _DEFAULTS["n_trials"],
    beta: float = _DEFAULTS["beta"],
    reverse: bool = _DEFAULTS["reverse"]
) -> None:
    """
    Runs prediction trials for `textcat` models with varying tresholds to maximize the specified metric.
    model_path (Path): Path to file with trained model.
    doc_path (Path): Path to file with DocBin with docs to use for threshold search.
    aggregation (str): How to aggregate F-scores across labels. One of ('micro', 'macro', 'weighted').
    pipe_name (Optional[str]): Name of pipe to examine thresholds for. If None, pipe of type MultiLabel_TextCategorizer
        is seleted. If there are multiple, an error is raised.
    n_trials (int): Number of trials to determine optimal thresholds
    beta (float): Beta for F1 calculation. Ignored if different metric is used.
    reverse (bool): Whether to minimize metric instead of maximizing it.
    """

    nlp = spacy.load(model_path)
    pipe: Optional[MultiLabel_TextCategorizer] = None
    selected_pipe_name: Optional[str] = pipe_name

    for _pipe_name, _pipe in nlp.pipeline:
        if pipe_name and _pipe_name == pipe_name:
            if not isinstance(_pipe, MultiLabel_TextCategorizer):
                # todo convert to error
                assert "Specified name is not a MultiLabel_TextCategorizer."
            pipe = _pipe
            break
        elif pipe_name is None:
            if isinstance(_pipe, MultiLabel_TextCategorizer):
                if pipe:
                    # todo convert to error
                    assert (
                        "Multiple components of type MultiLabel_TextCategorizer in pipeline. Please specify "
                        "component name."
                    )
                pipe = _pipe
                selected_pipe_name = _pipe_name

    # counts = {label: 0 for label in pipe.labels}
    # true_positive_counts = counts.copy()
    # false_positive_counts = counts.copy()
    # f_scores = counts.copy()
    # thresholds = numpy.linspace(0, 1, n_trials)

    # todo iterate over docs, assert categories are 1 or 0.
    # todo run pipe for all docs in docbin.
    # todo iterate over thresholds. for each:
    #   - iterate over all docs. for each:
    #       - iterate over all labels. for each:
    #           - mark as positive/negative based on current threshold
    #           - update count, f_score stats
    #   - compute f_scores for all labels
    #   - output best threshold
    print(selected_pipe_name, pipe.labels, pipe.predict([nlp("aaa")]))
