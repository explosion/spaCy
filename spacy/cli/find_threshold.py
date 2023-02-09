import functools
import operator
from pathlib import Path
import logging
from typing import Optional, Tuple, Any, Dict, List
import numpy
from wasabi import msg, row
from radicli import Arg, ExistingPath, ExistingFilePath

from ..pipeline import TextCategorizer, MultiLabel_TextCategorizer
from ..errors import Errors
from ..training import Corpus
from ._util import cli, import_code, setup_gpu
from .. import util

DEFAULT_N_TRIALS: int = 11
DEFAULT_USE_GPU: int = -1
DEFAULT_GOLD_PREPROC: bool = False


@cli.command(
    "find-threshold",
    # fmt: off
    model=Arg(help="Model name or path"),
    data_path=Arg(help="Location of binary evaluation data in .spacy format"),
    pipe_name=Arg(help="Name of pipe to examine thresholds for"),
    threshold_key=Arg(help="Key of threshold attribute in component's configuration"),
    scores_key=Arg(help="Metric to optimize"),
    n_trials=Arg("--n_trials", "-n", help="Number of trials to determine optimal thresholds"),
    code_path=Arg("--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    use_gpu=Arg("--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    gold_preproc=Arg("--gold-preproc", "-G", help="Use gold preprocessing"),
    verbose=Arg("--verbose", "-V", help="Display more information for debugging purposes"),
    # fmt: on
)
def find_threshold_cli(
    model: str,
    data_path: ExistingPath,
    pipe_name: str,
    threshold_key: str,
    scores_key: str,
    n_trials: int = DEFAULT_N_TRIALS,
    code_path: Optional[ExistingFilePath] = None,
    use_gpu: int = DEFAULT_USE_GPU,
    gold_preproc: bool = DEFAULT_GOLD_PREPROC,
    verbose: bool = False,
):
    """
    Runs prediction trials for a trained model with varying tresholds to maximize
    the specified metric. The search space for the threshold is traversed linearly
    from 0 to 1 in `n_trials` steps. Results are displayed in a table on `stdout`
    (the corresponding API call to `spacy.cli.find_threshold.find_threshold()`
    returns all results).

    This is applicable only for components whose predictions are influenced by
    thresholds - e.g. `textcat_multilabel` and `spancat`, but not `textcat`. Note
    that the full path to the corresponding threshold attribute in the config has to
    be provided.

    DOCS: https://spacy.io/api/cli#find-threshold
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
    n_trials: int = DEFAULT_N_TRIALS,
    use_gpu: int = DEFAULT_USE_GPU,
    gold_preproc: bool = DEFAULT_GOLD_PREPROC,
    silent: bool = True,
) -> Tuple[float, float, Dict[float, float]]:
    """
    Runs prediction trials for models with varying tresholds to maximize the specified metric.
    model (Union[str, Path]): Pipeline to evaluate. Can be a package or a path to a data directory.
    data_path (Path): Path to file with DocBin with docs to use for threshold search.
    pipe_name (str): Name of pipe to examine thresholds for.
    threshold_key (str): Key of threshold attribute in component's configuration.
    scores_key (str): Name of score to metric to optimize.
    n_trials (int): Number of trials to determine optimal thresholds.
    use_gpu (int): GPU ID or -1 for CPU.
    gold_preproc (bool): Whether to use gold preprocessing. Gold preprocessing helps the annotations align to the
        tokenization, and may result in sequences of more consistent length. However, it may reduce runtime accuracy due
        to train/test skew.
    silent (bool): Whether to print non-error-related output to stdout.
    RETURNS (Tuple[float, float, Dict[float, float]]): Best found threshold, the corresponding score, scores for all
        evaluated thresholds.
    """
    setup_gpu(use_gpu, silent=silent)
    data_path = util.ensure_path(data_path)
    if not data_path.exists():
        msg.fail("Evaluation data not found", data_path, exits=1)
    nlp = util.load_model(model)
    if pipe_name not in nlp.component_names:
        err = Errors.E001.format(name=pipe_name, opts=nlp.component_names)
        raise AttributeError(err)
    pipe = nlp.get_pipe(pipe_name)
    if not hasattr(pipe, "scorer"):
        raise AttributeError(Errors.E1045)
    if type(pipe) == TextCategorizer:
        msg.warn(
            "The `textcat` component doesn't use a threshold as it's not applicable to the concept of "
            "exclusive classes. All thresholds will yield the same results."
        )
    if not silent:
        text = f"Optimizing for {scores_key} for component '{pipe_name}' with {n_trials} trials."
        msg.info(text)
    # Load evaluation corpus.
    corpus = Corpus(data_path, gold_preproc=gold_preproc)
    dev_dataset = list(corpus(nlp))
    config_keys = threshold_key.split(".")

    def set_nested_item(
        config: Dict[str, Any], keys: List[str], value: float
    ) -> Dict[str, Any]:
        """Set item in nested dictionary. Adapted from https://stackoverflow.com/a/54138200.
        config (Dict[str, Any]): Configuration dictionary.
        keys (List[Any]): Path to value to set.
        value (float): Value to set.
        RETURNS (Dict[str, Any]): Updated dictionary.
        """
        functools.reduce(operator.getitem, keys[:-1], config)[keys[-1]] = value
        return config

    def filter_config(
        config: Dict[str, Any], keys: List[str], full_key: str
    ) -> Dict[str, Any]:
        """Filters provided config dictionary so that only the specified keys path remains.
        config (Dict[str, Any]): Configuration dictionary.
        keys (List[Any]): Path to value to set.
        full_key (str): Full user-specified key.
        RETURNS (Dict[str, Any]): Filtered dictionary.
        """
        if keys[0] not in config:
            msg.fail(
                f"Failed to look up `{full_key}` in config: sub-key {[keys[0]]} not found.",
                f"Make sure you specified {[keys[0]]} correctly. The following sub-keys are available instead: "
                f"{list(config.keys())}",
                exits=1,
            )
        return {
            keys[0]: filter_config(config[keys[0]], keys[1:], full_key)
            if len(keys) > 1
            else config[keys[0]]
        }

    # Evaluate with varying threshold values.
    scores: Dict[float, float] = {}
    config_keys_full = ["components", pipe_name, *config_keys]
    table_col_widths = (10, 10)
    thresholds = numpy.linspace(0, 1, n_trials)
    print(row(["Threshold", f"{scores_key}"], widths=table_col_widths))
    for threshold in thresholds:
        # Reload pipeline with overrides specifying the new threshold.
        nlp = util.load_model(
            model,
            config=set_nested_item(
                filter_config(
                    nlp.config, config_keys_full, ".".join(config_keys_full)
                ).copy(),
                config_keys_full,
                threshold,
            ),
        )
        if hasattr(pipe, "cfg"):
            setattr(
                nlp.get_pipe(pipe_name),
                "cfg",
                set_nested_item(getattr(pipe, "cfg"), config_keys, threshold),
            )
        eval_scores = nlp.evaluate(dev_dataset)
        if scores_key not in eval_scores:
            msg.fail(
                title=f"Failed to look up score `{scores_key}` in evaluation results.",
                text=f"Make sure you specified the correct value for `scores_key`. The following scores are "
                f"available: {list(eval_scores.keys())}",
                exits=1,
            )
        scores[threshold] = eval_scores[scores_key]
        if not isinstance(scores[threshold], (float, int)):
            msg.fail(
                f"Returned score for key '{scores_key}' is not numeric. Threshold "
                f"optimization only works for numeric scores.",
                exits=1,
            )
        data = [round(threshold, 3), round(scores[threshold], 3)]
        print(row(data, widths=table_col_widths))
    best_threshold = max(scores.keys(), key=(lambda key: scores[key]))
    # If all scores are identical, emit warning.
    if len(set(scores.values())) == 1:
        msg.warn(
            "All scores are identical. Verify that all settings are correct.",
            text=""
            if (
                not isinstance(pipe, MultiLabel_TextCategorizer)
                or scores_key in ("cats_macro_f", "cats_micro_f")
            )
            else "Use `cats_macro_f` or `cats_micro_f` when optimizing the threshold for `textcat_multilabel`.",
        )
    else:
        if not silent:
            print(
                f"\nBest threshold: {round(best_threshold, ndigits=4)} with "
                f"{scores_key} value of {scores[best_threshold]}."
            )
    return best_threshold, scores[best_threshold], scores
