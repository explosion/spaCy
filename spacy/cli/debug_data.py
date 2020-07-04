from typing import Optional, List, Sequence, Dict, Any, Tuple
from pathlib import Path
from collections import Counter
import sys
import srsly
from wasabi import Printer, MESSAGES

from ._app import app, Arg, Opt
from ..gold import Corpus, Example
from ..syntax import nonproj
from ..language import Language
from ..util import load_model, get_lang_class


# Minimum number of expected occurrences of NER label in data to train new label
NEW_LABEL_THRESHOLD = 50
# Minimum number of expected occurrences of dependency labels
DEP_LABEL_THRESHOLD = 20
# Minimum number of expected examples to train a blank model
BLANK_MODEL_MIN_THRESHOLD = 100
BLANK_MODEL_THRESHOLD = 2000


@app.command("debug-data")
def debug_data_cli(
    # fmt: off
    lang: str = Arg(..., help="Model language"),
    train_path: Path = Arg(..., help="Location of JSON-formatted training data", exists=True),
    dev_path: Path = Arg(..., help="Location of JSON-formatted development data", exists=True),
    tag_map_path: Optional[Path] = Opt(None, "--tag-map-path", "-tm", help="Location of JSON-formatted tag map", exists=True, dir_okay=False),
    base_model: Optional[str] = Opt(None, "--base-model", "-b", help="Name of model to update (optional)"),
    pipeline: str = Opt("tagger,parser,ner", "--pipeline", "-p", help="Comma-separated names of pipeline components to train"),
    ignore_warnings: bool = Opt(False, "--ignore-warnings", "-IW", help="Ignore warnings, only show stats and errors"),
    verbose: bool = Opt(False, "--verbose", "-V", help="Print additional information and explanations"),
    no_format: bool = Opt(False, "--no-format", "-NF", help="Don't pretty-print the results"),
    # fmt: on
):
    """
    Analyze, debug and validate your training and development data, get useful
    stats, and find problems like invalid entity annotations, cyclic
    dependencies, low data labels and more.
    """
    debug_data(
        lang,
        train_path,
        dev_path,
        tag_map_path=tag_map_path,
        base_model=base_model,
        pipeline=[p.strip() for p in pipeline.split(",")],
        ignore_warnings=ignore_warnings,
        verbose=verbose,
        no_format=no_format,
        silent=False,
    )


def debug_data(
    lang: str,
    train_path: Path,
    dev_path: Path,
    *,
    tag_map_path: Optional[Path] = None,
    base_model: Optional[str] = None,
    pipeline: List[str] = ["tagger", "parser", "ner"],
    ignore_warnings: bool = False,
    verbose: bool = False,
    no_format: bool = True,
    silent: bool = True,
):
    msg = Printer(
        no_print=silent, pretty=not no_format, ignore_warnings=ignore_warnings
    )
    # Make sure all files and paths exists if they are needed
    if not train_path.exists():
        msg.fail("Training data not found", train_path, exits=1)
    if not dev_path.exists():
        msg.fail("Development data not found", dev_path, exits=1)

    tag_map = {}
    if tag_map_path is not None:
        tag_map = srsly.read_json(tag_map_path)

    # Initialize the model and pipeline
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
        corpus = Corpus(train_path, dev_path)
        try:
            train_dataset = list(corpus.train_dataset(nlp))
        except ValueError as e:
            loading_train_error_message = f"Training data cannot be loaded: {e}"
        try:
            dev_dataset = list(corpus.dev_dataset(nlp))
        except ValueError as e:
            loading_dev_error_message = f"Development data cannot be loaded: {e}"
    if loading_train_error_message or loading_dev_error_message:
        if loading_train_error_message:
            msg.fail(loading_train_error_message)
        if loading_dev_error_message:
            msg.fail(loading_dev_error_message)
        sys.exit(1)
    msg.good("Corpus is loadable")

    # Create all gold data here to avoid iterating over the train_dataset constantly
    gold_train_data = _compile_gold(train_dataset, pipeline, nlp, make_proj=True)
    gold_train_unpreprocessed_data = _compile_gold(
        train_dataset, pipeline, nlp, make_proj=False
    )
    gold_dev_data = _compile_gold(dev_dataset, pipeline, nlp, make_proj=True)

    train_texts = gold_train_data["texts"]
    dev_texts = gold_dev_data["texts"]

    msg.divider("Training stats")
    msg.text(f"Training pipeline: {', '.join(pipeline)}")
    for pipe in [p for p in pipeline if p not in nlp.factories]:
        msg.fail(f"Pipeline component '{pipe}' not available in factories")
    if base_model:
        msg.text(f"Starting with base model '{base_model}'")
    else:
        msg.text(f"Starting with blank model '{lang}'")
    msg.text(f"{len(train_dataset)} training docs")
    msg.text(f"{len(dev_dataset)} evaluation docs")

    if not len(gold_dev_data):
        msg.fail("No evaluation docs")
    overlap = len(train_texts.intersection(dev_texts))
    if overlap:
        msg.warn(f"{overlap} training examples also in evaluation data")
    else:
        msg.good("No overlap between training and evaluation data")
    if not base_model and len(train_dataset) < BLANK_MODEL_THRESHOLD:
        text = (
            f"Low number of examples to train from a blank model ({len(train_dataset)})"
        )
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
        msg.info(
            f"{len(nlp.vocab.vectors)} vectors ({nlp.vocab.vectors.n_keys} "
            f"unique keys, {nlp.vocab.vectors_length} dimensions)"
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
            label for label in gold_train_data["ner"] if label not in ("O", "-", None)
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
            f"{len(new_labels)} new label(s), {len(existing_labels)} existing label(s)"
        )
        missing_values = label_counts["-"]
        msg.text(f"{missing_values} missing value(s) (tokens with '-' label)")
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
            msg.text(f"New: {labels_with_counts}", show=verbose)
        if existing_labels:
            msg.text(f"Existing: {_format_labels(existing_labels)}", show=verbose)
        if gold_train_data["ws_ents"]:
            msg.fail(f"{gold_train_data['ws_ents']} invalid whitespace entity spans")
            has_ws_ents_error = True

        if gold_train_data["punct_ents"]:
            msg.warn(f"{gold_train_data['punct_ents']} entity span(s) with punctuation")
            has_punct_ents_warning = True

        for label in new_labels:
            if label_counts[label] <= NEW_LABEL_THRESHOLD:
                msg.warn(
                    f"Low number of examples for new label '{label}' ({label_counts[label]})"
                )
                has_low_data_warning = True

                with msg.loading("Analyzing label distribution..."):
                    neg_docs = _get_examples_without_label(train_dataset, label)
                if neg_docs == 0:
                    msg.warn(f"No examples for texts WITHOUT new label '{label}'")
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
            f"Text Classification: {len(new_labels)} new label(s), "
            f"{len(existing_labels)} existing label(s)"
        )
        if new_labels:
            labels_with_counts = _format_labels(
                gold_train_data["cats"].most_common(), counts=True
            )
            msg.text(f"New: {labels_with_counts}", show=verbose)
        if existing_labels:
            msg.text(f"Existing: {_format_labels(existing_labels)}", show=verbose)
        if set(gold_train_data["cats"]) != set(gold_dev_data["cats"]):
            msg.fail(
                f"The train and dev labels are not the same. "
                f"Train labels: {_format_labels(gold_train_data['cats'])}. "
                f"Dev labels: {_format_labels(gold_dev_data['cats'])}."
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
        msg.info(f"{len(labels)} label(s) in data ({len(tag_map)} label(s) in tag map)")
        labels_with_counts = _format_labels(
            gold_train_data["tags"].most_common(), counts=True
        )
        msg.text(labels_with_counts, show=verbose)
        non_tagmap = [l for l in labels if l not in tag_map]
        if not non_tagmap:
            msg.good(f"All labels present in tag map for language '{nlp.lang}'")
        for label in non_tagmap:
            msg.fail(f"Label '{label}' not found in tag map for language '{nlp.lang}'")

    if "parser" in pipeline:
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
        msg.info(f"{labels_train_unpreprocessed} label(s) in train data")
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
            if gold_train_data["deps"][label] <= DEP_LABEL_THRESHOLD and "||" in label:
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
    examples: Sequence[Example], pipeline: List[str], nlp: Language, make_proj: bool
) -> Dict[str, Any]:
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
    for eg in examples:
        gold = eg.reference
        doc = eg.predicted
        valid_words = [x for x in gold if x is not None]
        data["words"].update(valid_words)
        data["n_words"] += len(valid_words)
        data["n_misaligned_words"] += len(gold) - len(valid_words)
        data["texts"].add(doc.text)
        if len(nlp.vocab.vectors):
            for word in valid_words:
                if nlp.vocab.strings[word] not in nlp.vocab.vectors:
                    data["words_missing_vectors"].update([word])
        if "ner" in pipeline:
            for i, label in enumerate(eg.get_aligned_ner()):
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
            tags = eg.get_aligned("TAG", as_string=True)
            data["tags"].update([x for x in tags if x is not None])
        if "parser" in pipeline:
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


def _format_labels(labels: List[Tuple[str, int]], counts: bool = False) -> str:
    if counts:
        return ", ".join([f"'{l}' ({c})" for l, c in labels])
    return ", ".join([f"'{l}'" for l in labels])


def _get_examples_without_label(data: Sequence[Example], label: str) -> int:
    count = 0
    for eg in data:
        labels = [
            label.split("-")[1]
            for label in eg.get_aligned_ner()
            if label not in ("O", "-", None)
        ]
        if label not in labels:
            count += 1
    return count


def _get_labels_from_model(nlp: Language, pipe_name: str) -> Sequence[str]:
    if pipe_name not in nlp.pipe_names:
        return set()
    pipe = nlp.get_pipe(pipe_name)
    return pipe.labels
