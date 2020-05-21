# coding: utf8
from __future__ import unicode_literals, print_function

from pathlib import Path
from collections import Counter
import plac
import sys
import srsly
from wasabi import Printer, MESSAGES

from ..gold import GoldCorpus
from ..syntax import nonproj
from ..util import load_model, get_lang_class


# Minimum number of expected occurrences of NER label in data to train new label
NEW_LABEL_THRESHOLD = 50
# Minimum number of expected occurrences of dependency labels
DEP_LABEL_THRESHOLD = 20
# Minimum number of expected examples to train a blank model
BLANK_MODEL_MIN_THRESHOLD = 100
BLANK_MODEL_THRESHOLD = 2000


@plac.annotations(
    # fmt: off
    lang=("model language", "positional", None, str),
    train_path=("location of JSON-formatted training data", "positional", None, Path),
    dev_path=("location of JSON-formatted development data", "positional", None, Path),
    tag_map_path=("Location of JSON-formatted tag map", "option", "tm", Path),
    base_model=("name of model to update (optional)", "option", "b", str),
    pipeline=("Comma-separated names of pipeline components to train", "option", "p", str),
    ignore_warnings=("Ignore warnings, only show stats and errors", "flag", "IW", bool),
    verbose=("Print additional information and explanations", "flag", "V", bool),
    no_format=("Don't pretty-print the results", "flag", "NF", bool),
    # fmt: on
)
def debug_data(
    lang,
    train_path,
    dev_path,
    tag_map_path=None,
    base_model=None,
    pipeline="tagger,parser,ner",
    ignore_warnings=False,
    verbose=False,
    no_format=False,
):
    """
    Analyze, debug and validate your training and development data, get useful
    stats, and find problems like invalid entity annotations, cyclic
    dependencies, low data labels and more.
    """
    msg = Printer(pretty=not no_format, ignore_warnings=ignore_warnings)

    # Make sure all files and paths exists if they are needed
    if not train_path.exists():
        msg.fail("Training data not found", train_path, exits=1)
    if not dev_path.exists():
        msg.fail("Development data not found", dev_path, exits=1)

    tag_map = {}
    if tag_map_path is not None:
        tag_map = srsly.read_json(tag_map_path)

    # Initialize the model and pipeline
    pipeline = [p.strip() for p in pipeline.split(",")]
    if base_model:
        nlp = load_model(base_model)
    else:
        lang_cls = get_lang_class(lang)
        nlp = lang_cls()
    # Update tag map with provided mapping
    nlp.vocab.morphology.tag_map.update(tag_map)

    msg.divider("Data format validation")

    # TODO: Validate data format using the JSON schema
    # TODO: update once the new format is ready
    # TODO: move validation to GoldCorpus in order to be able to load from dir

    # Create the gold corpus to be able to better analyze data
    loading_train_error_message = ""
    loading_dev_error_message = ""
    with msg.loading("Loading corpus..."):
        corpus = GoldCorpus(train_path, dev_path)
        try:
            train_docs = list(corpus.train_docs(nlp))
            train_docs_unpreprocessed = list(
                corpus.train_docs_without_preprocessing(nlp)
            )
        except ValueError as e:
            loading_train_error_message = "Training data cannot be loaded: {}".format(
                str(e)
            )
        try:
            dev_docs = list(corpus.dev_docs(nlp))
        except ValueError as e:
            loading_dev_error_message = "Development data cannot be loaded: {}".format(
                str(e)
            )
    if loading_train_error_message or loading_dev_error_message:
        if loading_train_error_message:
            msg.fail(loading_train_error_message)
        if loading_dev_error_message:
            msg.fail(loading_dev_error_message)
        sys.exit(1)
    msg.good("Corpus is loadable")

    # Create all gold data here to avoid iterating over the train_docs constantly
    gold_train_data = _compile_gold(train_docs, pipeline, nlp)
    gold_train_unpreprocessed_data = _compile_gold(
        train_docs_unpreprocessed, pipeline, nlp
    )
    gold_dev_data = _compile_gold(dev_docs, pipeline, nlp)

    train_texts = gold_train_data["texts"]
    dev_texts = gold_dev_data["texts"]

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

    if not len(dev_docs):
        msg.fail("No evaluation docs")
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
    n_words = gold_train_data["n_words"]
    msg.info(
        "{} total {} in the data ({} unique)".format(
            n_words, "word" if n_words == 1 else "words", len(gold_train_data["words"])
        )
    )
    if gold_train_data["n_misaligned_words"] > 0:
        msg.warn(
            "{} misaligned tokens in the training data".format(
                gold_train_data["n_misaligned_words"]
            )
        )
    if gold_dev_data["n_misaligned_words"] > 0:
        msg.warn(
            "{} misaligned tokens in the dev data".format(
                gold_dev_data["n_misaligned_words"]
            )
        )
    most_common_words = gold_train_data["words"].most_common(10)
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
        n_missing_vectors = sum(gold_train_data["words_missing_vectors"].values())
        msg.warn(
            "{} words in training data without vectors ({:0.2f}%)".format(
                n_missing_vectors, n_missing_vectors / gold_train_data["n_words"],
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
        msg.info("No word vectors present in the model")

    if "ner" in pipeline:
        # Get all unique NER labels present in the data
        labels = set(
            label for label in gold_train_data["ner"] if label not in ("O", "-")
        )
        label_counts = gold_train_data["ner"]
        model_labels = _get_labels_from_model(nlp, "ner")
        new_labels = [l for l in labels if l not in model_labels]
        existing_labels = [l for l in labels if l in model_labels]
        has_low_data_warning = False
        has_no_neg_warning = False
        has_ws_ents_error = False
        has_punct_ents_warning = False

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
        for label in new_labels:
            if len(label) == 0:
                msg.fail("Empty label found in new labels")
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

        if gold_train_data["ws_ents"]:
            msg.fail(
                "{} invalid whitespace entity span(s)".format(
                    gold_train_data["ws_ents"]
                )
            )
            has_ws_ents_error = True

        if gold_train_data["punct_ents"]:
            msg.warn(
                "{} entity span(s) with punctuation".format(
                    gold_train_data["punct_ents"]
                )
            )
            has_punct_ents_warning = True

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
            msg.good("Examples without occurrences available for all labels")
        if not has_ws_ents_error:
            msg.good("No entities consisting of or starting/ending with whitespace")
        if not has_punct_ents_warning:
            msg.good("No entities consisting of or starting/ending with punctuation")

        if has_low_data_warning:
            msg.text(
                "To train a new entity type, your data should include at "
                "least {} instances of the new label".format(NEW_LABEL_THRESHOLD),
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

        if has_punct_ents_warning:
            msg.text(
                "Entity spans consisting of or starting/ending "
                "with punctuation can not be trained with a noise level > 0."
            )

    if "textcat" in pipeline:
        msg.divider("Text Classification")
        labels = [label for label in gold_train_data["cats"]]
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
                gold_train_data["cats"].most_common(), counts=True
            )
            msg.text("New: {}".format(labels_with_counts), show=verbose)
        if existing_labels:
            msg.text(
                "Existing: {}".format(_format_labels(existing_labels)), show=verbose
            )
        if set(gold_train_data["cats"]) != set(gold_dev_data["cats"]):
            msg.fail(
                "The train and dev labels are not the same. "
                "Train labels: {}. "
                "Dev labels: {}.".format(
                    _format_labels(gold_train_data["cats"]),
                    _format_labels(gold_dev_data["cats"]),
                )
            )
        if gold_train_data["n_cats_multilabel"] > 0:
            msg.info(
                "The train data contains instances without "
                "mutually-exclusive classes. Use '--textcat-multilabel' "
                "when training."
            )
            if gold_dev_data["n_cats_multilabel"] == 0:
                msg.warn(
                    "Potential train/dev mismatch: the train data contains "
                    "instances without mutually-exclusive classes while the "
                    "dev data does not."
                )
        else:
            msg.info(
                "The train data contains only instances with "
                "mutually-exclusive classes."
            )
            if gold_dev_data["n_cats_multilabel"] > 0:
                msg.fail(
                    "Train/dev mismatch: the dev data contains instances "
                    "without mutually-exclusive classes while the train data "
                    "contains only instances with mutually-exclusive classes."
                )

    if "tagger" in pipeline:
        msg.divider("Part-of-speech Tagging")
        labels = [label for label in gold_train_data["tags"]]
        tag_map = nlp.vocab.morphology.tag_map
        msg.info(
            "{} {} in data ({} {} in tag map)".format(
                len(labels),
                "label" if len(labels) == 1 else "labels",
                len(tag_map),
                "label" if len(tag_map) == 1 else "labels",
            )
        )
        labels_with_counts = _format_labels(
            gold_train_data["tags"].most_common(), counts=True
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
        has_low_data_warning = False
        msg.divider("Dependency Parsing")

        # profile sentence length
        msg.info(
            "Found {} sentence{} with an average length of {:.1f} words.".format(
                gold_train_data["n_sents"],
                "s" if len(train_docs) > 1 else "",
                gold_train_data["n_words"] / gold_train_data["n_sents"],
            )
        )

        # check for documents with multiple sentences
        sents_per_doc = gold_train_data["n_sents"] / len(gold_train_data["texts"])
        if sents_per_doc < 1.1:
            msg.warn(
                "The training data contains {:.2f} sentences per "
                "document. When there are very few documents containing more "
                "than one sentence, the parser will not learn how to segment "
                "longer texts into sentences.".format(sents_per_doc)
            )

        # profile labels
        labels_train = [label for label in gold_train_data["deps"]]
        labels_train_unpreprocessed = [
            label for label in gold_train_unpreprocessed_data["deps"]
        ]
        labels_dev = [label for label in gold_dev_data["deps"]]

        if gold_train_unpreprocessed_data["n_nonproj"] > 0:
            msg.info(
                "Found {} nonprojective train sentence{}".format(
                    gold_train_unpreprocessed_data["n_nonproj"],
                    "s" if gold_train_unpreprocessed_data["n_nonproj"] > 1 else "",
                )
            )
        if gold_dev_data["n_nonproj"] > 0:
            msg.info(
                "Found {} nonprojective dev sentence{}".format(
                    gold_dev_data["n_nonproj"],
                    "s" if gold_dev_data["n_nonproj"] > 1 else "",
                )
            )

        msg.info(
            "{} {} in train data".format(
                len(labels_train_unpreprocessed),
                "label" if len(labels_train) == 1 else "labels",
            )
        )
        msg.info(
            "{} {} in projectivized train data".format(
                len(labels_train), "label" if len(labels_train) == 1 else "labels"
            )
        )

        labels_with_counts = _format_labels(
            gold_train_unpreprocessed_data["deps"].most_common(), counts=True
        )
        msg.text(labels_with_counts, show=verbose)

        # rare labels in train
        for label in gold_train_unpreprocessed_data["deps"]:
            if gold_train_unpreprocessed_data["deps"][label] <= DEP_LABEL_THRESHOLD:
                msg.warn(
                    "Low number of examples for label '{}' ({})".format(
                        label, gold_train_unpreprocessed_data["deps"][label]
                    )
                )
                has_low_data_warning = True

        # rare labels in projectivized train
        rare_projectivized_labels = []
        for label in gold_train_data["deps"]:
            if gold_train_data["deps"][label] <= DEP_LABEL_THRESHOLD and "||" in label:
                rare_projectivized_labels.append(
                    "{}: {}".format(label, str(gold_train_data["deps"][label]))
                )

        if len(rare_projectivized_labels) > 0:
            msg.warn(
                "Low number of examples for {} label{} in the "
                "projectivized dependency trees used for training. You may "
                "want to projectivize labels such as punct before "
                "training in order to improve parser performance.".format(
                    len(rare_projectivized_labels),
                    "s" if len(rare_projectivized_labels) > 1 else "",
                )
            )
            msg.warn(
                "Projectivized labels with low numbers of examples: "
                "{}".format("\n".join(rare_projectivized_labels)),
                show=verbose,
            )
            has_low_data_warning = True

        # labels only in train
        if set(labels_train) - set(labels_dev):
            msg.warn(
                "The following labels were found only in the train data: "
                "{}".format(", ".join(set(labels_train) - set(labels_dev))),
                show=verbose,
            )

        # labels only in dev
        if set(labels_dev) - set(labels_train):
            msg.warn(
                "The following labels were found only in the dev data: "
                + ", ".join(set(labels_dev) - set(labels_train)),
                show=verbose,
            )

        if has_low_data_warning:
            msg.text(
                "To train a parser, your data should include at "
                "least {} instances of each label.".format(DEP_LABEL_THRESHOLD),
                show=verbose,
            )

        # multiple root labels
        if len(gold_train_unpreprocessed_data["roots"]) > 1:
            msg.warn(
                "Multiple root labels ({}) ".format(
                    ", ".join(gold_train_unpreprocessed_data["roots"])
                )
                + "found in training data. spaCy's parser uses a single root "
                "label ROOT so this distinction will not be available."
            )

        # these should not happen, but just in case
        if gold_train_data["n_nonproj"] > 0:
            msg.fail(
                "Found {} nonprojective projectivized train sentence{}".format(
                    gold_train_data["n_nonproj"],
                    "s" if gold_train_data["n_nonproj"] > 1 else "",
                )
            )
        if gold_train_data["n_cycles"] > 0:
            msg.fail(
                "Found {} projectivized train sentence{} with cycles".format(
                    gold_train_data["n_cycles"],
                    "s" if gold_train_data["n_cycles"] > 1 else "",
                )
            )

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


def _compile_gold(train_docs, pipeline, nlp):
    data = {
        "ner": Counter(),
        "cats": Counter(),
        "tags": Counter(),
        "deps": Counter(),
        "words": Counter(),
        "roots": Counter(),
        "ws_ents": 0,
        "punct_ents": 0,
        "n_words": 0,
        "n_misaligned_words": 0,
        "words_missing_vectors": Counter(),
        "n_sents": 0,
        "n_nonproj": 0,
        "n_cycles": 0,
        "n_cats_multilabel": 0,
        "texts": set(),
    }
    for doc, gold in train_docs:
        valid_words = [x for x in gold.words if x is not None]
        data["words"].update(valid_words)
        data["n_words"] += len(valid_words)
        data["n_misaligned_words"] += len(gold.words) - len(valid_words)
        data["texts"].add(doc.text)
        if len(nlp.vocab.vectors):
            for word in valid_words:
                if nlp.vocab.strings[word] not in nlp.vocab.vectors:
                    data["words_missing_vectors"].update([word])
        if "ner" in pipeline:
            for i, label in enumerate(gold.ner):
                if label is None:
                    continue
                if label.startswith(("B-", "U-", "L-")) and doc[i].is_space:
                    # "Illegal" whitespace entity
                    data["ws_ents"] += 1
                if label.startswith(("B-", "U-", "L-")) and doc[i].text in [
                    ".",
                    "'",
                    "!",
                    "?",
                    ",",
                ]:
                    # punctuation entity: could be replaced by whitespace when training with noise,
                    # so add a warning to alert the user to this unexpected side effect.
                    data["punct_ents"] += 1
                if label.startswith(("B-", "U-")):
                    combined_label = label.split("-")[1]
                    data["ner"][combined_label] += 1
                elif label == "-":
                    data["ner"]["-"] += 1
        if "textcat" in pipeline:
            data["cats"].update(gold.cats)
            if list(gold.cats.values()).count(1.0) != 1:
                data["n_cats_multilabel"] += 1
        if "tagger" in pipeline:
            data["tags"].update([x for x in gold.tags if x is not None])
        if "parser" in pipeline:
            data["deps"].update([x for x in gold.labels if x is not None])
            for i, (dep, head) in enumerate(zip(gold.labels, gold.heads)):
                if head == i:
                    data["roots"].update([dep])
                    data["n_sents"] += 1
            if nonproj.is_nonproj_tree(gold.heads):
                data["n_nonproj"] += 1
            if nonproj.contains_cycle(gold.heads):
                data["n_cycles"] += 1
    return data


def _format_labels(labels, counts=False):
    if counts:
        return ", ".join(["'{}' ({})".format(l, c) for l, c in labels])
    return ", ".join(["'{}'".format(l) for l in labels])


def _get_examples_without_label(data, label):
    count = 0
    for doc, gold in data:
        labels = [
            label.split("-")[1]
            for label in gold.ner
            if label is not None and label not in ("O", "-")
        ]
        if label not in labels:
            count += 1
    return count


def _get_labels_from_model(nlp, pipe_name):
    if pipe_name not in nlp.pipe_names:
        return set()
    pipe = nlp.get_pipe(pipe_name)
    return pipe.labels
