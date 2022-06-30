from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union
from typing import cast, overload
from pathlib import Path
from collections import Counter
import sys
import srsly
from wasabi import Printer, MESSAGES, msg
import typer
import math

from ._util import app, Arg, Opt, show_validation_error, parse_config_overrides
from ._util import import_code, debug_cli
from ..training import Example, remove_bilu_prefix
from ..training.initialize import get_sourced_components
from ..schemas import ConfigSchemaTraining
from ..pipeline._parser_internals import nonproj
from ..pipeline._parser_internals.nonproj import DELIMITER
from ..pipeline import Morphologizer, SpanCategorizer
from ..morphology import Morphology
from ..language import Language
from ..util import registry, resolve_dot_names
from ..compat import Literal
from ..vectors import Mode as VectorsMode
from .. import util


# Minimum number of expected occurrences of NER label in data to train new label
NEW_LABEL_THRESHOLD = 50
# Minimum number of expected occurrences of dependency labels
DEP_LABEL_THRESHOLD = 20
# Minimum number of expected examples to train a new pipeline
BLANK_MODEL_MIN_THRESHOLD = 100
BLANK_MODEL_THRESHOLD = 2000
# Arbitrary threshold where SpanCat performs well
SPAN_DISTINCT_THRESHOLD = 1
# Arbitrary threshold where SpanCat performs well
BOUNDARY_DISTINCT_THRESHOLD = 1
# Arbitrary threshold for filtering span lengths during reporting (percentage)
SPAN_LENGTH_THRESHOLD_PERCENTAGE = 90


@debug_cli.command(
    "data", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
@app.command(
    "debug-data",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    hidden=True,  # hide this from main CLI help but still allow it to work with warning
)
def debug_data_cli(
    # fmt: off
    ctx: typer.Context,  # This is only used to read additional arguments
    config_path: Path = Arg(..., help="Path to config file", exists=True, allow_dash=True),
    code_path: Optional[Path] = Opt(None, "--code-path", "--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    ignore_warnings: bool = Opt(False, "--ignore-warnings", "-IW", help="Ignore warnings, only show stats and errors"),
    verbose: bool = Opt(False, "--verbose", "-V", help="Print additional information and explanations"),
    no_format: bool = Opt(False, "--no-format", "-NF", help="Don't pretty-print the results"),
    # fmt: on
):
    """
    Analyze, debug and validate your training and development data. Outputs
    useful stats, and can help you find problems like invalid entity annotations,
    cyclic dependencies, low data labels and more.

    DOCS: https://spacy.io/api/cli#debug-data
    """
    if ctx.command.name == "debug-data":
        msg.warn(
            "The debug-data command is now available via the 'debug data' "
            "subcommand (without the hyphen). You can run python -m spacy debug "
            "--help for an overview of the other available debugging commands."
        )
    overrides = parse_config_overrides(ctx.args)
    import_code(code_path)
    debug_data(
        config_path,
        config_overrides=overrides,
        ignore_warnings=ignore_warnings,
        verbose=verbose,
        no_format=no_format,
        silent=False,
    )


def debug_data(
    config_path: Path,
    *,
    config_overrides: Dict[str, Any] = {},
    ignore_warnings: bool = False,
    verbose: bool = False,
    no_format: bool = True,
    silent: bool = True,
):
    msg = Printer(
        no_print=silent, pretty=not no_format, ignore_warnings=ignore_warnings
    )
    # Make sure all files and paths exists if they are needed
    with show_validation_error(config_path):
        cfg = util.load_config(config_path, overrides=config_overrides)
        nlp = util.load_model_from_config(cfg)
        config = nlp.config.interpolate()
        T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    # Use original config here, not resolved version
    sourced_components = get_sourced_components(cfg)
    frozen_components = T["frozen_components"]
    resume_components = [p for p in sourced_components if p not in frozen_components]
    pipeline = nlp.pipe_names
    factory_names = [nlp.get_pipe_meta(pipe).factory for pipe in nlp.pipe_names]
    msg.divider("Data file validation")

    # Create the gold corpus to be able to better analyze data
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    train_corpus, dev_corpus = resolve_dot_names(config, dot_names)

    nlp.initialize(lambda: train_corpus(nlp))
    msg.good("Pipeline can be initialized with data")

    train_dataset = list(train_corpus(nlp))
    dev_dataset = list(dev_corpus(nlp))
    msg.good("Corpus is loadable")

    # Create all gold data here to avoid iterating over the train_dataset constantly
    gold_train_data = _compile_gold(train_dataset, factory_names, nlp, make_proj=True)
    gold_train_unpreprocessed_data = _compile_gold(
        train_dataset, factory_names, nlp, make_proj=False
    )
    gold_dev_data = _compile_gold(dev_dataset, factory_names, nlp, make_proj=True)

    train_texts = gold_train_data["texts"]
    dev_texts = gold_dev_data["texts"]
    frozen_components = T["frozen_components"]

    msg.divider("Training stats")
    msg.text(f"Language: {nlp.lang}")
    msg.text(f"Training pipeline: {', '.join(pipeline)}")
    if resume_components:
        msg.text(f"Components from other pipelines: {', '.join(resume_components)}")
    if frozen_components:
        msg.text(f"Frozen components: {', '.join(frozen_components)}")
    msg.text(f"{len(train_dataset)} training docs")
    msg.text(f"{len(dev_dataset)} evaluation docs")

    if not len(gold_dev_data):
        msg.fail("No evaluation docs")
    overlap = len(train_texts.intersection(dev_texts))
    if overlap:
        msg.warn(f"{overlap} training examples also in evaluation data")
    else:
        msg.good("No overlap between training and evaluation data")
    # TODO: make this feedback more fine-grained and report on updated
    # components vs. blank components
    if not resume_components and len(train_dataset) < BLANK_MODEL_THRESHOLD:
        text = f"Low number of examples to train a new pipeline ({len(train_dataset)})"
        if len(train_dataset) < BLANK_MODEL_MIN_THRESHOLD:
            msg.fail(text)
        else:
            msg.warn(text)
        msg.text(
            f"It's recommended to use at least {BLANK_MODEL_THRESHOLD} examples "
            f"(minimum {BLANK_MODEL_MIN_THRESHOLD})",
            show=verbose,
        )

    msg.divider("Vocab & Vectors")
    n_words = gold_train_data["n_words"]
    msg.info(
        f"{n_words} total word(s) in the data ({len(gold_train_data['words'])} unique)"
    )
    if gold_train_data["n_misaligned_words"] > 0:
        n_misaligned = gold_train_data["n_misaligned_words"]
        msg.warn(f"{n_misaligned} misaligned tokens in the training data")
    if gold_dev_data["n_misaligned_words"] > 0:
        n_misaligned = gold_dev_data["n_misaligned_words"]
        msg.warn(f"{n_misaligned} misaligned tokens in the dev data")
    most_common_words = gold_train_data["words"].most_common(10)
    msg.text(
        f"10 most common words: {_format_labels(most_common_words, counts=True)}",
        show=verbose,
    )
    if len(nlp.vocab.vectors):
        if nlp.vocab.vectors.mode == VectorsMode.floret:
            msg.info(
                f"floret vectors with {len(nlp.vocab.vectors)} vectors, "
                f"{nlp.vocab.vectors_length} dimensions, "
                f"{nlp.vocab.vectors.minn}-{nlp.vocab.vectors.maxn} char "
                f"n-gram subwords"
            )
        else:
            msg.info(
                f"{len(nlp.vocab.vectors)} vectors ({nlp.vocab.vectors.n_keys} "
                f"unique keys, {nlp.vocab.vectors_length} dimensions)"
            )
            n_missing_vectors = sum(gold_train_data["words_missing_vectors"].values())
            msg.warn(
                "{} words in training data without vectors ({:.0f}%)".format(
                    n_missing_vectors,
                    100 * (n_missing_vectors / gold_train_data["n_words"]),
                ),
            )
            msg.text(
                "10 most common words without vectors: {}".format(
                    _format_labels(
                        gold_train_data["words_missing_vectors"].most_common(10),
                        counts=True,
                    )
                ),
                show=verbose,
            )
    else:
        msg.info("No word vectors present in the package")

    if "spancat" in factory_names:
        model_labels_spancat = _get_labels_from_spancat(nlp)
        has_low_data_warning = False
        has_no_neg_warning = False

        msg.divider("Span Categorization")
        msg.table(model_labels_spancat, header=["Spans Key", "Labels"], divider=True)

        msg.text("Label counts in train data: ", show=verbose)
        for spans_key, data_labels in gold_train_data["spancat"].items():
            msg.text(
                f"Key: {spans_key}, {_format_labels(data_labels.items(), counts=True)}",
                show=verbose,
            )
        # Data checks: only take the spans keys in the actual spancat components
        data_labels_in_component = {
            spans_key: gold_train_data["spancat"][spans_key]
            for spans_key in model_labels_spancat.keys()
        }
        for spans_key, data_labels in data_labels_in_component.items():
            for label, count in data_labels.items():
                # Check for missing labels
                spans_key_in_model = spans_key in model_labels_spancat.keys()
                if (spans_key_in_model) and (
                    label not in model_labels_spancat[spans_key]
                ):
                    msg.warn(
                        f"Label '{label}' is not present in the model labels of key '{spans_key}'. "
                        "Performance may degrade after training."
                    )
                # Check for low number of examples per label
                if count <= NEW_LABEL_THRESHOLD:
                    msg.warn(
                        f"Low number of examples for label '{label}' in key '{spans_key}' ({count})"
                    )
                    has_low_data_warning = True
                # Check for negative examples
                with msg.loading("Analyzing label distribution..."):
                    neg_docs = _get_examples_without_label(
                        train_dataset, label, "spancat", spans_key
                    )
                if neg_docs == 0:
                    msg.warn(f"No examples for texts WITHOUT new label '{label}'")
                    has_no_neg_warning = True

            with msg.loading("Obtaining span characteristics..."):
                span_characteristics = _get_span_characteristics(
                    train_dataset, gold_train_data, spans_key
                )

            msg.info(f"Span characteristics for spans_key '{spans_key}'")
            msg.info("SD = Span Distinctiveness, BD = Boundary Distinctiveness")
            _print_span_characteristics(span_characteristics)

            _span_freqs = _get_spans_length_freq_dist(
                gold_train_data["spans_length"][spans_key]
            )
            _filtered_span_freqs = _filter_spans_length_freq_dist(
                _span_freqs, threshold=SPAN_LENGTH_THRESHOLD_PERCENTAGE
            )

            msg.info(
                f"Over {SPAN_LENGTH_THRESHOLD_PERCENTAGE}% of spans have lengths of 1 -- "
                f"{max(_filtered_span_freqs.keys())} "
                f"(min={span_characteristics['min_length']}, max={span_characteristics['max_length']}). "
                f"The most common span lengths are: {_format_freqs(_filtered_span_freqs)}. "
                "If you are using the n-gram suggester, note that omitting "
                "infrequent n-gram lengths can greatly improve speed and "
                "memory usage."
            )

            msg.text(
                f"Full distribution of span lengths: {_format_freqs(_span_freqs)}",
                show=verbose,
            )

            # Add report regarding span characteristics
            if span_characteristics["avg_sd"] < SPAN_DISTINCT_THRESHOLD:
                msg.warn("Spans may not be distinct from the rest of the corpus")
            else:
                msg.good("Spans are distinct from the rest of the corpus")

            p_spans = span_characteristics["p_spans"].values()
            all_span_tokens: Counter = sum(p_spans, Counter())
            most_common_spans = [w for w, _ in all_span_tokens.most_common(10)]
            msg.text(
                "10 most common span tokens: {}".format(
                    _format_labels(most_common_spans)
                ),
                show=verbose,
            )

            # Add report regarding span boundary characteristics
            if span_characteristics["avg_bd"] < BOUNDARY_DISTINCT_THRESHOLD:
                msg.warn("Boundary tokens are not distinct from the rest of the corpus")
            else:
                msg.good("Boundary tokens are distinct from the rest of the corpus")

            p_bounds = span_characteristics["p_bounds"].values()
            all_span_bound_tokens: Counter = sum(p_bounds, Counter())
            most_common_bounds = [w for w, _ in all_span_bound_tokens.most_common(10)]
            msg.text(
                "10 most common span boundary tokens: {}".format(
                    _format_labels(most_common_bounds)
                ),
                show=verbose,
            )

        if has_low_data_warning:
            msg.text(
                f"To train a new span type, your data should include at "
                f"least {NEW_LABEL_THRESHOLD} instances of the new label",
                show=verbose,
            )
        else:
            msg.good("Good amount of examples for all labels")

        if has_no_neg_warning:
            msg.text(
                "Training data should always include examples of spans "
                "in context, as well as examples without a given span "
                "type.",
                show=verbose,
            )
        else:
            msg.good("Examples without ocurrences available for all labels")

    if "ner" in factory_names:
        # Get all unique NER labels present in the data
        labels = set(
            label for label in gold_train_data["ner"] if label not in ("O", "-", None)
        )
        label_counts = gold_train_data["ner"]
        model_labels = _get_labels_from_model(nlp, "ner")
        has_low_data_warning = False
        has_no_neg_warning = False
        has_ws_ents_error = False
        has_boundary_cross_ents_warning = False

        msg.divider("Named Entity Recognition")
        msg.info(f"{len(model_labels)} label(s)")
        missing_values = label_counts["-"]
        msg.text(f"{missing_values} missing value(s) (tokens with '-' label)")
        for label in labels:
            if len(label) == 0:
                msg.fail("Empty label found in train data")
        labels_with_counts = [
            (label, count)
            for label, count in label_counts.most_common()
            if label != "-"
        ]
        labels_with_counts = _format_labels(labels_with_counts, counts=True)
        msg.text(f"Labels in train data: {labels_with_counts}", show=verbose)
        missing_labels = model_labels - labels
        if missing_labels:
            msg.warn(
                "Some model labels are not present in the train data. The "
                "model performance may be degraded for these labels after "
                f"training: {_format_labels(missing_labels)}."
            )
        if gold_train_data["ws_ents"]:
            msg.fail(f"{gold_train_data['ws_ents']} invalid whitespace entity spans")
            has_ws_ents_error = True

        for label in labels:
            if label_counts[label] <= NEW_LABEL_THRESHOLD:
                msg.warn(
                    f"Low number of examples for label '{label}' ({label_counts[label]})"
                )
                has_low_data_warning = True

                with msg.loading("Analyzing label distribution..."):
                    neg_docs = _get_examples_without_label(train_dataset, label, "ner")
                if neg_docs == 0:
                    msg.warn(f"No examples for texts WITHOUT new label '{label}'")
                    has_no_neg_warning = True

        if gold_train_data["boundary_cross_ents"]:
            msg.warn(
                f"{gold_train_data['boundary_cross_ents']} entity span(s) crossing sentence boundaries"
            )
            has_boundary_cross_ents_warning = True

        if not has_low_data_warning:
            msg.good("Good amount of examples for all labels")
        if not has_no_neg_warning:
            msg.good("Examples without occurrences available for all labels")
        if not has_ws_ents_error:
            msg.good("No entities consisting of or starting/ending with whitespace")
        if not has_boundary_cross_ents_warning:
            msg.good("No entities crossing sentence boundaries")

        if has_low_data_warning:
            msg.text(
                f"To train a new entity type, your data should include at "
                f"least {NEW_LABEL_THRESHOLD} instances of the new label",
                show=verbose,
            )
        if has_no_neg_warning:
            msg.text(
                "Training data should always include examples of entities "
                "in context, as well as examples without a given entity "
                "type.",
                show=verbose,
            )
        if has_ws_ents_error:
            msg.text(
                "Entity spans consisting of or starting/ending "
                "with whitespace characters are considered invalid."
            )

    if "textcat" in factory_names:
        msg.divider("Text Classification (Exclusive Classes)")
        labels = _get_labels_from_model(nlp, "textcat")
        msg.info(f"Text Classification: {len(labels)} label(s)")
        msg.text(f"Labels: {_format_labels(labels)}", show=verbose)
        missing_labels = labels - set(gold_train_data["cats"])
        if missing_labels:
            msg.warn(
                "Some model labels are not present in the train data. The "
                "model performance may be degraded for these labels after "
                f"training: {_format_labels(missing_labels)}."
            )
        if set(gold_train_data["cats"]) != set(gold_dev_data["cats"]):
            msg.warn(
                "Potential train/dev mismatch: the train and dev labels are "
                "not the same. "
                f"Train labels: {_format_labels(gold_train_data['cats'])}. "
                f"Dev labels: {_format_labels(gold_dev_data['cats'])}."
            )
        if len(labels) < 2:
            msg.fail(
                "The model does not have enough labels. 'textcat' requires at "
                "least two labels due to mutually-exclusive classes, e.g. "
                "LABEL/NOT_LABEL or POSITIVE/NEGATIVE for a binary "
                "classification task."
            )
        if (
            gold_train_data["n_cats_bad_values"] > 0
            or gold_dev_data["n_cats_bad_values"] > 0
        ):
            msg.fail(
                "Unsupported values for cats: the supported values are "
                "1.0/True and 0.0/False."
            )
        if gold_train_data["n_cats_multilabel"] > 0:
            # Note: you should never get here because you run into E895 on
            # initialization first.
            msg.fail(
                "The train data contains instances without mutually-exclusive "
                "classes. Use the component 'textcat_multilabel' instead of "
                "'textcat'."
            )
        if gold_dev_data["n_cats_multilabel"] > 0:
            msg.fail(
                "The dev data contains instances without mutually-exclusive "
                "classes. Use the component 'textcat_multilabel' instead of "
                "'textcat'."
            )

    if "textcat_multilabel" in factory_names:
        msg.divider("Text Classification (Multilabel)")
        labels = _get_labels_from_model(nlp, "textcat_multilabel")
        msg.info(f"Text Classification: {len(labels)} label(s)")
        msg.text(f"Labels: {_format_labels(labels)}", show=verbose)
        missing_labels = labels - set(gold_train_data["cats"])
        if missing_labels:
            msg.warn(
                "Some model labels are not present in the train data. The "
                "model performance may be degraded for these labels after "
                f"training: {_format_labels(missing_labels)}."
            )
        if set(gold_train_data["cats"]) != set(gold_dev_data["cats"]):
            msg.warn(
                "Potential train/dev mismatch: the train and dev labels are "
                "not the same. "
                f"Train labels: {_format_labels(gold_train_data['cats'])}. "
                f"Dev labels: {_format_labels(gold_dev_data['cats'])}."
            )
        if (
            gold_train_data["n_cats_bad_values"] > 0
            or gold_dev_data["n_cats_bad_values"] > 0
        ):
            msg.fail(
                "Unsupported values for cats: the supported values are "
                "1.0/True and 0.0/False."
            )
        if gold_train_data["n_cats_multilabel"] > 0:
            if gold_dev_data["n_cats_multilabel"] == 0:
                msg.warn(
                    "Potential train/dev mismatch: the train data contains "
                    "instances without mutually-exclusive classes while the "
                    "dev data contains only instances with mutually-exclusive "
                    "classes."
                )
        else:
            msg.warn(
                "The train data contains only instances with "
                "mutually-exclusive classes. You can potentially use the "
                "component 'textcat' instead of 'textcat_multilabel'."
            )
            if gold_dev_data["n_cats_multilabel"] > 0:
                msg.fail(
                    "Train/dev mismatch: the dev data contains instances "
                    "without mutually-exclusive classes while the train data "
                    "contains only instances with mutually-exclusive classes."
                )

    if "tagger" in factory_names:
        msg.divider("Part-of-speech Tagging")
        label_list = [label for label in gold_train_data["tags"]]
        model_labels = _get_labels_from_model(nlp, "tagger")
        msg.info(f"{len(label_list)} label(s) in train data")
        labels = set(label_list)
        missing_labels = model_labels - labels
        if missing_labels:
            msg.warn(
                "Some model labels are not present in the train data. The "
                "model performance may be degraded for these labels after "
                f"training: {_format_labels(missing_labels)}."
            )
        labels_with_counts = _format_labels(
            gold_train_data["tags"].most_common(), counts=True
        )
        msg.text(labels_with_counts, show=verbose)

    if "morphologizer" in factory_names:
        msg.divider("Morphologizer (POS+Morph)")
        label_list = [label for label in gold_train_data["morphs"]]
        model_labels = _get_labels_from_model(nlp, "morphologizer")
        msg.info(f"{len(label_list)} label(s) in train data")
        labels = set(label_list)
        missing_labels = model_labels - labels
        if missing_labels:
            msg.warn(
                "Some model labels are not present in the train data. The "
                "model performance may be degraded for these labels after "
                f"training: {_format_labels(missing_labels)}."
            )
        labels_with_counts = _format_labels(
            gold_train_data["morphs"].most_common(), counts=True
        )
        msg.text(labels_with_counts, show=verbose)

    if "parser" in factory_names:
        has_low_data_warning = False
        msg.divider("Dependency Parsing")

        # profile sentence length
        msg.info(
            f"Found {gold_train_data['n_sents']} sentence(s) with an average "
            f"length of {gold_train_data['n_words'] / gold_train_data['n_sents']:.1f} words."
        )

        # check for documents with multiple sentences
        sents_per_doc = gold_train_data["n_sents"] / len(gold_train_data["texts"])
        if sents_per_doc < 1.1:
            msg.warn(
                f"The training data contains {sents_per_doc:.2f} sentences per "
                f"document. When there are very few documents containing more "
                f"than one sentence, the parser will not learn how to segment "
                f"longer texts into sentences."
            )

        # profile labels
        labels_train = [label for label in gold_train_data["deps"]]
        labels_train_unpreprocessed = [
            label for label in gold_train_unpreprocessed_data["deps"]
        ]
        labels_dev = [label for label in gold_dev_data["deps"]]

        if gold_train_unpreprocessed_data["n_nonproj"] > 0:
            n_nonproj = gold_train_unpreprocessed_data["n_nonproj"]
            msg.info(f"Found {n_nonproj} nonprojective train sentence(s)")
        if gold_dev_data["n_nonproj"] > 0:
            n_nonproj = gold_dev_data["n_nonproj"]
            msg.info(f"Found {n_nonproj} nonprojective dev sentence(s)")
        msg.info(f"{len(labels_train_unpreprocessed)} label(s) in train data")
        msg.info(f"{len(labels_train)} label(s) in projectivized train data")
        labels_with_counts = _format_labels(
            gold_train_unpreprocessed_data["deps"].most_common(), counts=True
        )
        msg.text(labels_with_counts, show=verbose)

        # rare labels in train
        for label in gold_train_unpreprocessed_data["deps"]:
            if gold_train_unpreprocessed_data["deps"][label] <= DEP_LABEL_THRESHOLD:
                msg.warn(
                    f"Low number of examples for label '{label}' "
                    f"({gold_train_unpreprocessed_data['deps'][label]})"
                )
                has_low_data_warning = True

        # rare labels in projectivized train
        rare_projectivized_labels = []
        for label in gold_train_data["deps"]:
            if (
                gold_train_data["deps"][label] <= DEP_LABEL_THRESHOLD
                and DELIMITER in label
            ):
                rare_projectivized_labels.append(
                    f"{label}: {gold_train_data['deps'][label]}"
                )

        if len(rare_projectivized_labels) > 0:
            msg.warn(
                f"Low number of examples for {len(rare_projectivized_labels)} "
                "label(s) in the projectivized dependency trees used for "
                "training. You may want to projectivize labels such as punct "
                "before training in order to improve parser performance."
            )
            msg.warn(
                f"Projectivized labels with low numbers of examples: ",
                ", ".join(rare_projectivized_labels),
                show=verbose,
            )
            has_low_data_warning = True

        # labels only in train
        if set(labels_train) - set(labels_dev):
            msg.warn(
                "The following labels were found only in the train data:",
                ", ".join(set(labels_train) - set(labels_dev)),
                show=verbose,
            )

        # labels only in dev
        if set(labels_dev) - set(labels_train):
            msg.warn(
                "The following labels were found only in the dev data:",
                ", ".join(set(labels_dev) - set(labels_train)),
                show=verbose,
            )

        if has_low_data_warning:
            msg.text(
                f"To train a parser, your data should include at "
                f"least {DEP_LABEL_THRESHOLD} instances of each label.",
                show=verbose,
            )

        # multiple root labels
        if len(gold_train_unpreprocessed_data["roots"]) > 1:
            msg.warn(
                f"Multiple root labels "
                f"({', '.join(gold_train_unpreprocessed_data['roots'])}) "
                f"found in training data. spaCy's parser uses a single root "
                f"label ROOT so this distinction will not be available."
            )

        # these should not happen, but just in case
        if gold_train_data["n_nonproj"] > 0:
            msg.fail(
                f"Found {gold_train_data['n_nonproj']} nonprojective "
                f"projectivized train sentence(s)"
            )
        if gold_train_data["n_cycles"] > 0:
            msg.fail(
                f"Found {gold_train_data['n_cycles']} projectivized train sentence(s) with cycles"
            )

    msg.divider("Summary")
    good_counts = msg.counts[MESSAGES.GOOD]
    warn_counts = msg.counts[MESSAGES.WARN]
    fail_counts = msg.counts[MESSAGES.FAIL]
    if good_counts:
        msg.good(f"{good_counts} {'check' if good_counts == 1 else 'checks'} passed")
    if warn_counts:
        msg.warn(f"{warn_counts} {'warning' if warn_counts == 1 else 'warnings'}")
    if fail_counts:
        msg.fail(f"{fail_counts} {'error' if fail_counts == 1 else 'errors'}")
        sys.exit(1)


def _load_file(file_path: Path, msg: Printer) -> None:
    file_name = file_path.parts[-1]
    if file_path.suffix == ".json":
        with msg.loading(f"Loading {file_name}..."):
            data = srsly.read_json(file_path)
        msg.good(f"Loaded {file_name}")
        return data
    elif file_path.suffix == ".jsonl":
        with msg.loading(f"Loading {file_name}..."):
            data = srsly.read_jsonl(file_path)
        msg.good(f"Loaded {file_name}")
        return data
    msg.fail(
        f"Can't load file extension {file_path.suffix}",
        "Expected .json or .jsonl",
        exits=1,
    )


def _compile_gold(
    examples: Sequence[Example],
    factory_names: List[str],
    nlp: Language,
    make_proj: bool,
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "ner": Counter(),
        "cats": Counter(),
        "tags": Counter(),
        "morphs": Counter(),
        "deps": Counter(),
        "words": Counter(),
        "roots": Counter(),
        "spancat": dict(),
        "spans_length": dict(),
        "spans_per_type": dict(),
        "sb_per_type": dict(),
        "ws_ents": 0,
        "boundary_cross_ents": 0,
        "n_words": 0,
        "n_misaligned_words": 0,
        "words_missing_vectors": Counter(),
        "n_sents": 0,
        "n_nonproj": 0,
        "n_cycles": 0,
        "n_cats_multilabel": 0,
        "n_cats_bad_values": 0,
        "texts": set(),
    }
    for eg in examples:
        gold = eg.reference
        doc = eg.predicted
        valid_words = [x.text for x in gold]
        data["words"].update(valid_words)
        data["n_words"] += len(valid_words)
        align = eg.alignment
        for token in doc:
            if token.orth_.isspace():
                continue
            if align.x2y.lengths[token.i] != 1:
                data["n_misaligned_words"] += 1
        data["texts"].add(doc.text)
        if len(nlp.vocab.vectors):
            for word in [t.text for t in doc]:
                if nlp.vocab.strings[word] not in nlp.vocab.vectors:
                    data["words_missing_vectors"].update([word])
        if "ner" in factory_names:
            sent_starts = eg.get_aligned_sent_starts()
            for i, label in enumerate(eg.get_aligned_ner()):
                if label is None:
                    continue
                if label.startswith(("B-", "U-", "L-")) and doc[i].is_space:
                    # "Illegal" whitespace entity
                    data["ws_ents"] += 1
                if label.startswith(("B-", "U-")):
                    combined_label = remove_bilu_prefix(label)
                    data["ner"][combined_label] += 1
                if sent_starts[i] and label.startswith(("I-", "L-")):
                    data["boundary_cross_ents"] += 1
                elif label == "-":
                    data["ner"]["-"] += 1
        if "spancat" in factory_names:
            for spans_key in list(eg.reference.spans.keys()):
                # Obtain the span frequency
                if spans_key not in data["spancat"]:
                    data["spancat"][spans_key] = Counter()
                for i, span in enumerate(eg.reference.spans[spans_key]):
                    if span.label_ is None:
                        continue
                    else:
                        data["spancat"][spans_key][span.label_] += 1

                # Obtain the span length
                if spans_key not in data["spans_length"]:
                    data["spans_length"][spans_key] = dict()
                for span in gold.spans[spans_key]:
                    if span.label_ is None:
                        continue
                    if span.label_ not in data["spans_length"][spans_key]:
                        data["spans_length"][spans_key][span.label_] = []
                    data["spans_length"][spans_key][span.label_].append(len(span))

                # Obtain spans per span type
                if spans_key not in data["spans_per_type"]:
                    data["spans_per_type"][spans_key] = dict()
                for span in gold.spans[spans_key]:
                    if span.label_ not in data["spans_per_type"][spans_key]:
                        data["spans_per_type"][spans_key][span.label_] = []
                    data["spans_per_type"][spans_key][span.label_].append(span)

                # Obtain boundary tokens per span type
                window_size = 1
                if spans_key not in data["sb_per_type"]:
                    data["sb_per_type"][spans_key] = dict()
                for span in gold.spans[spans_key]:
                    if span.label_ not in data["sb_per_type"][spans_key]:
                        # Creating a data structure that holds the start and
                        # end tokens for each span type
                        data["sb_per_type"][spans_key][span.label_] = {
                            "start": [],
                            "end": [],
                        }
                    for offset in range(window_size):
                        sb_start_idx = span.start - (offset + 1)
                        if sb_start_idx >= 0:
                            data["sb_per_type"][spans_key][span.label_]["start"].append(
                                gold[sb_start_idx : sb_start_idx + 1]
                            )

                        sb_end_idx = span.end + (offset + 1)
                        if sb_end_idx <= len(gold):
                            data["sb_per_type"][spans_key][span.label_]["end"].append(
                                gold[sb_end_idx - 1 : sb_end_idx]
                            )

        if "textcat" in factory_names or "textcat_multilabel" in factory_names:
            data["cats"].update(gold.cats)
            if any(val not in (0, 1) for val in gold.cats.values()):
                data["n_cats_bad_values"] += 1
            if list(gold.cats.values()).count(1) != 1:
                data["n_cats_multilabel"] += 1
        if "tagger" in factory_names:
            tags = eg.get_aligned("TAG", as_string=True)
            data["tags"].update([x for x in tags if x is not None])
        if "morphologizer" in factory_names:
            pos_tags = eg.get_aligned("POS", as_string=True)
            morphs = eg.get_aligned("MORPH", as_string=True)
            for pos, morph in zip(pos_tags, morphs):
                # POS may align (same value for multiple tokens) when morph
                # doesn't, so if either is misaligned (None), treat the
                # annotation as missing so that truths doesn't end up with an
                # unknown morph+POS combination
                if pos is None or morph is None:
                    pass
                # If both are unset, the annotation is missing (empty morph
                # converted from int is "_" rather than "")
                elif pos == "" and morph == "":
                    pass
                # Otherwise, generate the combined label
                else:
                    label_dict = Morphology.feats_to_dict(morph)
                    if pos:
                        label_dict[Morphologizer.POS_FEAT] = pos
                    label = eg.reference.vocab.strings[
                        eg.reference.vocab.morphology.add(label_dict)
                    ]
                    data["morphs"].update([label])
        if "parser" in factory_names:
            aligned_heads, aligned_deps = eg.get_aligned_parse(projectivize=make_proj)
            data["deps"].update([x for x in aligned_deps if x is not None])
            for i, (dep, head) in enumerate(zip(aligned_deps, aligned_heads)):
                if head == i:
                    data["roots"].update([dep])
                    data["n_sents"] += 1
            if nonproj.is_nonproj_tree(aligned_heads):
                data["n_nonproj"] += 1
            if nonproj.contains_cycle(aligned_heads):
                data["n_cycles"] += 1
    return data


@overload
def _format_labels(labels: Iterable[str], counts: Literal[False] = False) -> str:
    ...


@overload
def _format_labels(
    labels: Iterable[Tuple[str, int]],
    counts: Literal[True],
) -> str:
    ...


def _format_labels(
    labels: Union[Iterable[str], Iterable[Tuple[str, int]]],
    counts: bool = False,
) -> str:
    if counts:
        return ", ".join(
            [f"'{l}' ({c})" for l, c in cast(Iterable[Tuple[str, int]], labels)]
        )
    return ", ".join([f"'{l}'" for l in cast(Iterable[str], labels)])


def _format_freqs(freqs: Dict[int, float], sort: bool = True) -> str:
    if sort:
        freqs = dict(sorted(freqs.items()))

    _freqs = [(str(k), v) for k, v in freqs.items()]
    return ", ".join(
        [f"{l} ({c}%)" for l, c in cast(Iterable[Tuple[str, float]], _freqs)]
    )


def _get_examples_without_label(
    data: Sequence[Example],
    label: str,
    component: Literal["ner", "spancat"] = "ner",
    spans_key: Optional[str] = "sc",
) -> int:
    count = 0
    for eg in data:
        if component == "ner":
            labels = [
                remove_bilu_prefix(label)
                for label in eg.get_aligned_ner()
                if label not in ("O", "-", None)
            ]

        if component == "spancat":
            labels = (
                [span.label_ for span in eg.reference.spans[spans_key]]
                if spans_key in eg.reference.spans
                else []
            )

        if label not in labels:
            count += 1
    return count


def _get_labels_from_model(nlp: Language, factory_name: str) -> Set[str]:
    pipe_names = [
        pipe_name
        for pipe_name in nlp.pipe_names
        if nlp.get_pipe_meta(pipe_name).factory == factory_name
    ]
    labels: Set[str] = set()
    for pipe_name in pipe_names:
        pipe = nlp.get_pipe(pipe_name)
        labels.update(pipe.labels)
    return labels


def _get_labels_from_spancat(nlp: Language) -> Dict[str, Set[str]]:
    pipe_names = [
        pipe_name
        for pipe_name in nlp.pipe_names
        if nlp.get_pipe_meta(pipe_name).factory == "spancat"
    ]
    labels: Dict[str, Set[str]] = {}
    for pipe_name in pipe_names:
        pipe = nlp.get_pipe(pipe_name)
        assert isinstance(pipe, SpanCategorizer)
        if pipe.key not in labels:
            labels[pipe.key] = set()
        labels[pipe.key].update(pipe.labels)
    return labels


def _gmean(l: List) -> float:
    """Compute geometric mean of a list"""
    return math.exp(math.fsum(math.log(i) for i in l) / len(l))


def _wgt_average(metric: Dict[str, float], frequencies: Counter) -> float:
    total = sum(value * frequencies[span_type] for span_type, value in metric.items())
    return total / sum(frequencies.values())


def _get_distribution(docs, normalize: bool = True) -> Counter:
    """Get the frequency distribution given a set of Docs"""
    word_counts: Counter = Counter()
    for doc in docs:
        for token in doc:
            # Normalize the text
            t = token.text.lower().replace("``", '"').replace("''", '"')
            word_counts[t] += 1
    if normalize:
        total = sum(word_counts.values(), 0.0)
        word_counts = Counter({k: v / total for k, v in word_counts.items()})
    return word_counts


def _get_kl_divergence(p: Counter, q: Counter) -> float:
    """Compute the Kullback-Leibler divergence from two frequency distributions"""
    total = 0.0
    for word, p_word in p.items():
        total += p_word * math.log(p_word / q[word])
    return total


def _format_span_row(span_data: List[Dict], labels: List[str]) -> List[Any]:
    """Compile into one list for easier reporting"""
    d = {
        label: [label] + list(round(d[label], 2) for d in span_data) for label in labels
    }
    return list(d.values())


def _get_span_characteristics(
    examples: List[Example], compiled_gold: Dict[str, Any], spans_key: str
) -> Dict[str, Any]:
    """Obtain all span characteristics"""
    data_labels = compiled_gold["spancat"][spans_key]
    # Get lengths
    span_length = {
        label: _gmean(l)
        for label, l in compiled_gold["spans_length"][spans_key].items()
    }
    min_lengths = [min(l) for l in compiled_gold["spans_length"][spans_key].values()]
    max_lengths = [max(l) for l in compiled_gold["spans_length"][spans_key].values()]

    # Get relevant distributions: corpus, spans, span boundaries
    p_corpus = _get_distribution([eg.reference for eg in examples], normalize=True)
    p_spans = {
        label: _get_distribution(spans, normalize=True)
        for label, spans in compiled_gold["spans_per_type"][spans_key].items()
    }
    p_bounds = {
        label: _get_distribution(sb["start"] + sb["end"], normalize=True)
        for label, sb in compiled_gold["sb_per_type"][spans_key].items()
    }

    # Compute for actual span characteristics
    span_distinctiveness = {
        label: _get_kl_divergence(freq_dist, p_corpus)
        for label, freq_dist in p_spans.items()
    }
    sb_distinctiveness = {
        label: _get_kl_divergence(freq_dist, p_corpus)
        for label, freq_dist in p_bounds.items()
    }

    return {
        "sd": span_distinctiveness,
        "bd": sb_distinctiveness,
        "lengths": span_length,
        "min_length": min(min_lengths),
        "max_length": max(max_lengths),
        "avg_sd": _wgt_average(span_distinctiveness, data_labels),
        "avg_bd": _wgt_average(sb_distinctiveness, data_labels),
        "avg_length": _wgt_average(span_length, data_labels),
        "labels": list(data_labels.keys()),
        "p_spans": p_spans,
        "p_bounds": p_bounds,
    }


def _print_span_characteristics(span_characteristics: Dict[str, Any]):
    """Print all span characteristics into a table"""
    headers = ("Span Type", "Length", "SD", "BD")
    # Prepare table data with all span characteristics
    table_data = [
        span_characteristics["lengths"],
        span_characteristics["sd"],
        span_characteristics["bd"],
    ]
    table = _format_span_row(
        span_data=table_data, labels=span_characteristics["labels"]
    )
    # Prepare table footer with weighted averages
    footer_data = [
        span_characteristics["avg_length"],
        span_characteristics["avg_sd"],
        span_characteristics["avg_bd"],
    ]
    footer = ["Wgt. Average"] + [str(round(f, 2)) for f in footer_data]
    msg.table(table, footer=footer, header=headers, divider=True)


def _get_spans_length_freq_dist(
    length_dict: Dict, threshold=SPAN_LENGTH_THRESHOLD_PERCENTAGE
) -> Dict[int, float]:
    """Get frequency distribution of spans length under a certain threshold"""
    all_span_lengths = []
    for _, lengths in length_dict.items():
        all_span_lengths.extend(lengths)

    freq_dist: Counter = Counter()
    for i in all_span_lengths:
        if freq_dist.get(i):
            freq_dist[i] += 1
        else:
            freq_dist[i] = 1

    # We will be working with percentages instead of raw counts
    freq_dist_percentage = {}
    for span_length, count in freq_dist.most_common():
        percentage = (count / len(all_span_lengths)) * 100.0
        percentage = round(percentage, 2)
        freq_dist_percentage[span_length] = percentage

    return freq_dist_percentage


def _filter_spans_length_freq_dist(
    freq_dist: Dict[int, float], threshold: int
) -> Dict[int, float]:
    """Filter frequency distribution with respect to a threshold

    We're going to filter all the span lengths that fall
    around a percentage threshold when summed.
    """
    total = 0.0
    filtered_freq_dist = {}
    for span_length, dist in freq_dist.items():
        if total >= threshold:
            break
        else:
            filtered_freq_dist[span_length] = dist
        total += dist
    return filtered_freq_dist
