# coding: utf8
from __future__ import unicode_literals, print_function

from pathlib import Path
from collections import Counter
import plac
import sys
import srsly
from wasabi import Printer, MESSAGES

from ..gold import GoldCorpus, read_json_object
from ..util import load_model, get_lang_class


# Minimum number of expected occurences of label in data to train new label
NEW_LABEL_THRESHOLD = 50
# Minimum number of expected examples to train a blank model
BLANK_MODEL_MIN_THRESHOLD = 100
BLANK_MODEL_THRESHOLD = 2000


@plac.annotations(
    lang=("model language", "positional", None, str),
    train_path=("location of JSON-formatted training data", "positional", None, Path),
    dev_path=("location of JSON-formatted development data", "positional", None, Path),
    base_model=("name of model to update (optional)", "option", "b", str),
    pipeline=(
        "Comma-separated names of pipeline components to train",
        "option",
        "p",
        str,
    ),
    ignore_warnings=("Ignore warnings, only show stats and errors", "flag", "IW", bool),
    ignore_validation=(
        "Don't exit if JSON format validation fails",
        "flag",
        "IV",
        bool,
    ),
    verbose=("Print additional information and explanations", "flag", "V", bool),
    no_format=("Don't pretty-print the results", "flag", "NF", bool),
)
def debug_data(
    lang,
    train_path,
    dev_path,
    base_model=None,
    pipeline="tagger,parser,ner",
    ignore_warnings=False,
    ignore_validation=False,
    verbose=False,
    no_format=False,
):
    msg = Printer(pretty=not no_format, ignore_warnings=ignore_warnings)

    # Make sure all files and paths exists if they are needed
    if not train_path.exists():
        msg.fail("Training data not found", train_path, exits=1)
    if not dev_path.exists():
        msg.fail("Development data not found", dev_path, exits=1)

    # Initialize the model and pipeline
    pipeline = [p.strip() for p in pipeline.split(",")]
    if base_model:
        nlp = load_model(base_model)
    else:
        lang_cls = get_lang_class(lang)
        nlp = lang_cls()

    msg.divider("Data format validation")
    # Load the data in one – might take a while but okay in this case
    train_data = _load_file(train_path, msg)
    dev_data = _load_file(dev_path, msg)

    # Validate data format using the JSON schema
    # TODO: update once the new format is ready
    train_data_errors = []  # TODO: validate_json
    dev_data_errors = []  # TODO: validate_json
    if not train_data_errors:
        msg.good("Training data JSON format is valid")
    if not dev_data_errors:
        msg.good("Development data JSON format is valid")
    for error in train_data_errors:
        msg.fail("Training data: {}".format(error))
    for error in dev_data_errors:
        msg.fail("Develoment data: {}".format(error))
    if (train_data_errors or dev_data_errors) and not ignore_validation:
        sys.exit(1)

    # Create the gold corpus to be able to better analyze data
    with msg.loading("Analyzing corpus..."):
        train_data = read_json_object(train_data)
        dev_data = read_json_object(dev_data)
        corpus = GoldCorpus(train_data, dev_data)
        train_docs = list(corpus.train_docs(nlp))
        dev_docs = list(corpus.dev_docs(nlp))
    msg.good("Corpus is loadable")

    # Create all gold data here to avoid iterating over the train_docs constantly
    gold_data = _compile_gold(train_docs, pipeline)
    train_texts = gold_data["texts"]
    dev_texts = set([doc.text for doc, gold in dev_docs])

    msg.divider("Training stats")
    msg.text("Training pipeline: {}".format(", ".join(pipeline)))
    for pipe in [p for p in pipeline if p not in nlp.factories]:
        msg.fail("Pipeline component '{}' not available in factories".format(pipe))
    if base_model:
        msg.text("Starting with base model '{}'".format(base_model))
    else:
        msg.text("Starting with blank model '{}'".format(lang))
    msg.text("{} training docs".format(len(train_docs)))
    msg.text("{} evaluation docs".format(len(dev_docs)))

    overlap = len(train_texts.intersection(dev_texts))
    if overlap:
        msg.warn("{} training examples also in evaluation data".format(overlap))
    else:
        msg.good("No overlap between training and evaluation data")
    if not base_model and len(train_docs) < BLANK_MODEL_THRESHOLD:
        text = "Low number of examples to train from a blank model ({})".format(
            len(train_docs)
        )
        if len(train_docs) < BLANK_MODEL_MIN_THRESHOLD:
            msg.fail(text)
        else:
            msg.warn(text)
        msg.text(
            "It's recommended to use at least {} examples (minimum {})".format(
                BLANK_MODEL_THRESHOLD, BLANK_MODEL_MIN_THRESHOLD
            ),
            show=verbose,
        )

    msg.divider("Vocab & Vectors")
    n_words = gold_data["n_words"]
    msg.info(
        "{} total {} in the data ({} unique)".format(
            n_words, "word" if n_words == 1 else "words", len(gold_data["words"])
        )
    )
    most_common_words = gold_data["words"].most_common(10)
    msg.text(
        "10 most common words: {}".format(
            _format_labels(most_common_words, counts=True)
        ),
        show=verbose,
    )
    if len(nlp.vocab.vectors):
        msg.info(
            "{} vectors ({} unique keys, {} dimensions)".format(
                len(nlp.vocab.vectors),
                nlp.vocab.vectors.n_keys,
                nlp.vocab.vectors_length,
            )
        )
    else:
        msg.info("No word vectors present in the model")

    if "ner" in pipeline:
        # Get all unique NER labels present in the data
        labels = set(label for label in gold_data["ner"] if label not in ("O", "-"))
        label_counts = gold_data["ner"]
        model_labels = _get_labels_from_model(nlp, "ner")
        new_labels = [l for l in labels if l not in model_labels]
        existing_labels = [l for l in labels if l in model_labels]
        has_low_data_warning = False
        has_no_neg_warning = False
        has_ws_ents_error = False

        msg.divider("Named Entity Recognition")
        msg.info(
            "{} new {}, {} existing {}".format(
                len(new_labels),
                "label" if len(new_labels) == 1 else "labels",
                len(existing_labels),
                "label" if len(existing_labels) == 1 else "labels",
            )
        )
        missing_values = label_counts["-"]
        msg.text(
            "{} missing {} (tokens with '-' label)".format(
                missing_values, "value" if missing_values == 1 else "values"
            )
        )
        if new_labels:
            labels_with_counts = [
                (label, count)
                for label, count in label_counts.most_common()
                if label != "-"
            ]
            labels_with_counts = _format_labels(labels_with_counts, counts=True)
            msg.text("New: {}".format(labels_with_counts), show=verbose)
        if existing_labels:
            msg.text(
                "Existing: {}".format(_format_labels(existing_labels)), show=verbose
            )

        if gold_data["ws_ents"]:
            msg.fail("{} invalid whitespace entity spans".format(gold_data["ws_ents"]))
            has_ws_ents_error = True

        for label in new_labels:
            if label_counts[label] <= NEW_LABEL_THRESHOLD:
                msg.warn(
                    "Low number of examples for new label '{}' ({})".format(
                        label, label_counts[label]
                    )
                )
                has_low_data_warning = True

                with msg.loading("Analyzing label distribution..."):
                    neg_docs = _get_examples_without_label(train_docs, label)
                if neg_docs == 0:
                    msg.warn(
                        "No examples for texts WITHOUT new label '{}'".format(label)
                    )
                    has_no_neg_warning = True

        if not has_low_data_warning:
            msg.good("Good amount of examples for all labels")
        if not has_no_neg_warning:
            msg.good("Examples without occurences available for all labels")
        if not has_ws_ents_error:
            msg.good("No entities consisting of or starting/ending with whitespace")

        if has_low_data_warning:
            msg.text(
                "To train a new entity type, your data should include at "
                "least {} insteances of the new label".format(NEW_LABEL_THRESHOLD),
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
                "As of spaCy v2.1.0, entity spans consisting of or starting/ending "
                "with whitespace characters are considered invalid."
            )

    if "textcat" in pipeline:
        msg.divider("Text Classification")
        labels = [label for label in gold_data["textcat"]]
        model_labels = _get_labels_from_model(nlp, "textcat")
        new_labels = [l for l in labels if l not in model_labels]
        existing_labels = [l for l in labels if l in model_labels]
        msg.info(
            "Text Classification: {} new label(s), {} existing label(s)".format(
                len(new_labels), len(existing_labels)
            )
        )
        if new_labels:
            labels_with_counts = _format_labels(
                gold_data["textcat"].most_common(), counts=True
            )
            msg.text("New: {}".format(labels_with_counts), show=verbose)
        if existing_labels:
            msg.text(
                "Existing: {}".format(_format_labels(existing_labels)), show=verbose
            )

    if "tagger" in pipeline:
        msg.divider("Part-of-speech Tagging")
        labels = [label for label in gold_data["tags"]]
        tag_map = nlp.Defaults.tag_map
        msg.info(
            "{} {} in data ({} {} in tag map)".format(
                len(labels),
                "label" if len(labels) == 1 else "labels",
                len(tag_map),
                "label" if len(tag_map) == 1 else "labels",
            )
        )
        labels_with_counts = _format_labels(
            gold_data["tags"].most_common(), counts=True
        )
        msg.text(labels_with_counts, show=verbose)
        non_tagmap = [l for l in labels if l not in tag_map]
        if not non_tagmap:
            msg.good("All labels present in tag map for language '{}'".format(nlp.lang))
        for label in non_tagmap:
            msg.fail(
                "Label '{}' not found in tag map for language '{}'".format(
                    label, nlp.lang
                )
            )

    if "parser" in pipeline:
        msg.divider("Dependency Parsing")
        labels = [label for label in gold_data["deps"]]
        msg.info(
            "{} {} in data".format(
                len(labels), "label" if len(labels) == 1 else "labels"
            )
        )
        labels_with_counts = _format_labels(
            gold_data["deps"].most_common(), counts=True
        )
        msg.text(labels_with_counts, show=verbose)

    msg.divider("Summary")
    good_counts = msg.counts[MESSAGES.GOOD]
    warn_counts = msg.counts[MESSAGES.WARN]
    fail_counts = msg.counts[MESSAGES.FAIL]
    if good_counts:
        msg.good(
            "{} {} passed".format(
                good_counts, "check" if good_counts == 1 else "checks"
            )
        )
    if warn_counts:
        msg.warn(
            "{} {}".format(warn_counts, "warning" if warn_counts == 1 else "warnings")
        )
    if fail_counts:
        msg.fail("{} {}".format(fail_counts, "error" if fail_counts == 1 else "errors"))

    if fail_counts:
        sys.exit(1)


def _load_file(file_path, msg):
    file_name = file_path.parts[-1]
    if file_path.suffix == ".json":
        with msg.loading("Loading {}...".format(file_name)):
            data = srsly.read_json(file_path)
        msg.good("Loaded {}".format(file_name))
        return data
    elif file_path.suffix == ".jsonl":
        with msg.loading("Loading {}...".format(file_name)):
            data = srsly.read_jsonl(file_path)
        msg.good("Loaded {}".format(file_name))
        return data
    msg.fail(
        "Can't load file extension {}".format(file_path.suffix),
        "Expected .json or .jsonl",
        exits=1,
    )


def _compile_gold(train_docs, pipeline):
    data = {
        "ner": Counter(),
        "cats": Counter(),
        "tags": Counter(),
        "deps": Counter(),
        "words": Counter(),
        "ws_ents": 0,
        "n_words": 0,
        "texts": set(),
    }
    for doc, gold in train_docs:
        data["words"].update(gold.words)
        data["n_words"] += len(gold.words)
        data["texts"].add(doc.text)
        if "ner" in pipeline:
            for i, label in enumerate(gold.ner):
                if label.startswith(("B-", "U-", "L-")) and doc[i].is_space:
                    # "Illegal" whitespace entity
                    data["ws_ents"] += 1
                if label.startswith(("B-", "U-")):
                    combined_label = label.split("-")[1]
                    data["ner"][combined_label] += 1
                elif label == "-":
                    data["ner"]["-"] += 1
        if "textcat" in pipeline:
            data["cats"].update(gold.cats)
        if "tagger" in pipeline:
            data["tags"].update(gold.tags)
        if "parser" in pipeline:
            data["deps"].update(gold.labels)
    return data


def _format_labels(labels, counts=False):
    if counts:
        return ", ".join(["'{}' ({})".format(l, c) for l, c in labels])
    return ", ".join(["'{}'".format(l) for l in labels])


def _get_examples_without_label(data, label):
    count = 0
    for doc, gold in data:
        labels = [label.split("-")[1] for label in gold.ner if label not in ("O", "-")]
        if label not in labels:
            count += 1
    return count


def _get_labels_from_model(nlp, pipe_name):
    if pipe_name not in nlp.pipe_names:
        return set()
    pipe = nlp.get_pipe(pipe_name)
    return pipe.labels
