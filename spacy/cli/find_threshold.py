import functools
import operator
from pathlib import Path
import logging
from typing import Optional, Tuple, Any, Dict, List

import numpy
import wasabi.tables

from ..training import Corpus
from ._util import app, Arg, Opt, import_code, setup_gpu
from .. import util

_DEFAULTS = {
    "average": "micro",
    "n_trials": 10,
    "beta": 1,
    "use_gpu": -1,
    "gold_preproc": False,
}


@app.command(
    "find-threshold",
    context_settings={"allow_extra_args": False, "ignore_unknown_options": True},
)
def find_threshold_cli(
    # fmt: off
    model: str = Arg(..., help="Model name or path"),
    data_path: Path = Arg(..., help="Location of binary evaluation data in .spacy format", exists=True),
    pipe_name: str = Arg(..., help="Name of pipe to examine thresholds for"),
    threshold_key: str = Arg(..., help="Key of threshold attribute in component's configuration"),
    scores_key: str = Arg(..., help="Name of score to metric to optimize"),
    n_trials: int = Opt(_DEFAULTS["n_trials"], "--n_trials", "-n", help="Number of trials to determine optimal thresholds"),
    beta: float = Opt(_DEFAULTS["beta"], "--beta", help="Beta for F1 calculation. Ignored if different metric is used"),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    use_gpu: int = Opt(_DEFAULTS["use_gpu"], "--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    gold_preproc: bool = Opt(_DEFAULTS["gold_preproc"], "--gold-preproc", "-G", help="Use gold preprocessing"),
    verbose: bool = Opt(False, "--silent", "-V", "-VV", help="Display more information for debugging purposes"),
    # fmt: on
):
    """
    Runs prediction trials for `textcat` models with varying tresholds to maximize the specified metric from CLI.
    model (Path): Path to file with trained model.
    data_path (Path): Path to file with DocBin with docs to use for threshold search.
    pipe_name (str): Name of pipe to examine thresholds for.
    threshold_key (str): Key of threshold attribute in component's configuration.
    scores_key (str): Name of score to metric to optimize.
    n_trials (int): Number of trials to determine optimal thresholds
    beta (float): Beta for F1 calculation.
    code_path (Optional[Path]): Path to Python file with additional code (registered functions) to be imported.
    use_gpu (int): GPU ID or -1 for CPU.
    gold_preproc (bool): Whether to use gold preprocessing. Gold preprocessing helps the annotations align to the
        tokenization, and may result in sequences of more consistent length. However, it may reduce runtime accuracy due
        to train/test skew.
    silent (bool): Display more information for debugging purposes
    """

    util.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    import_code(code_path)
    find_threshold(
        model=model,
        data_path=data_path,
        pipe_name=pipe_name,
        threshold_key=threshold_key,
        scores_key=scores_key,
        n_trials=n_trials,
        beta=beta,
        use_gpu=use_gpu,
        gold_preproc=gold_preproc,
        silent=False,
    )


def find_threshold(
    model: str,
    data_path: Path,
    pipe_name: str,
    threshold_key: str,
    scores_key: str,
    *,
    n_trials: int = _DEFAULTS["n_trials"],
    beta: float = _DEFAULTS["beta"],
    use_gpu: int = _DEFAULTS["use_gpu"],
    gold_preproc: bool = _DEFAULTS["gold_preproc"],
    silent: bool = True,
) -> Tuple[float, float]:
    """
    Runs prediction trials for `textcat` models with varying tresholds to maximize the specified metric.
    model (Union[str, Path]): Path to file with trained model.
    data_path (Union[str, Path]): Path to file with DocBin with docs to use for threshold search.
    pipe_name (str): Name of pipe to examine thresholds for.
    threshold_key (str): Key of threshold attribute in component's configuration.
    scores_key (str): Name of score to metric to optimize.
    n_trials (int): Number of trials to determine optimal thresholds.
    beta (float): Beta for F1 calculation.
    use_gpu (int): GPU ID or -1 for CPU.
    gold_preproc (bool): Whether to use gold preprocessing. Gold preprocessing helps the annotations align to the
        tokenization, and may result in sequences of more consistent length. However, it may reduce runtime accuracy due
        to train/test skew.
    silent (bool): Whether to print non-error-related output to stdout.
    RETURNS (Tuple[float, float]): Best found threshold with corresponding F-score.
    """

    setup_gpu(use_gpu, silent=silent)
    data_path = util.ensure_path(data_path)
    if not data_path.exists():
        wasabi.msg.fail("Evaluation data not found", data_path, exits=1)
    nlp = util.load_model(model)

    try:
        pipe = nlp.get_pipe(pipe_name)
    except KeyError as err:
        wasabi.msg.fail(title=str(err), exits=1)

    if not silent:
        wasabi.msg.info(
            title=f"Optimizing for {scores_key} for component '{pipe_name}' with {n_trials} "
            f"trials and beta = {beta}."
        )

    # Load evaluation corpus.
    corpus = Corpus(data_path, gold_preproc=gold_preproc)
    dev_dataset = list(corpus(nlp))
    config_keys = threshold_key.split(".")

    def set_nested_item(
        config: Dict[str, Any], keys: List[str], value: float
    ) -> Dict[str, Any]:
        """Set item in nested dictionary. Adapated from https://stackoverflow.com/a/54138200.
        config (Dict[str, Any]): Configuration dictionary.
        keys (List[Any]):
        value (float): Value to set.
        RETURNS (Dict[str, Any]): Updated dictionary.
        """
        functools.reduce(operator.getitem, keys[:-1], config)[keys[-1]] = value
        return config

    # Evaluate with varying threshold values.
    scores: Dict[float, float] = {}
    for threshold in numpy.linspace(0, 1, n_trials):
        pipe.cfg = set_nested_item(pipe.cfg, config_keys, threshold)
        scores[threshold] = nlp.evaluate(dev_dataset)[scores_key]
        if not (
            isinstance(scores[threshold], float) or isinstance(scores[threshold], int)
        ):
            wasabi.msg.fail(
                f"Returned score for key '{scores_key}' is not numeric. Threshold optimization only works for numeric "
                f"scores.",
                exits=1,
            )

    best_threshold = max(scores.keys(), key=(lambda key: scores[key]))
    if not silent:
        print(
            f"Best threshold: {round(best_threshold, ndigits=4)} with value of {scores[best_threshold]}.",
            wasabi.tables.table(
                data=[(threshold, score) for threshold, score in scores.items()],
                header=["Threshold", f"{scores_key}"],
            ),
        )

    return best_threshold, scores[best_threshold]
