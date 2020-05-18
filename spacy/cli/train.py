import os
import tqdm
from pathlib import Path
from thinc.api import use_ops
from timeit import default_timer as timer
import shutil
import srsly
from wasabi import msg
import contextlib
import random

from ..util import create_default_optimizer
from ..util import use_gpu as set_gpu
from ..attrs import PROB, IS_OOV, CLUSTER, LANG
from ..gold import GoldCorpus
from .. import util
from .. import about


def train(
    # fmt: off
    lang: ("Model language", "positional", None, str),
    output_path: ("Output directory to store model in", "positional", None, Path),
    train_path: ("Location of JSON-formatted training data", "positional", None, Path),
    dev_path: ("Location of JSON-formatted development data", "positional", None, Path),
    raw_text: ("Path to jsonl file with unlabelled text documents.", "option", "rt", Path) = None,
    base_model: ("Name of model to update (optional)", "option", "b", str) = None,
    pipeline: ("Comma-separated names of pipeline components", "option", "p", str) = "tagger,parser,ner",
    vectors: ("Model to load vectors from", "option", "v", str) = None,
    replace_components: ("Replace components from base model", "flag", "R", bool) = False,
    n_iter: ("Number of iterations", "option", "n", int) = 30,
    n_early_stopping: ("Maximum number of training epochs without dev accuracy improvement", "option", "ne", int) = None,
    n_examples: ("Number of examples", "option", "ns", int) = 0,
    use_gpu: ("Use GPU", "option", "g", int) = -1,
    version: ("Model version", "option", "V", str) = "0.0.0",
    meta_path: ("Optional path to meta.json to use as base.", "option", "m", Path) = None,
    init_tok2vec: ("Path to pretrained weights for the token-to-vector parts of the models. See 'spacy pretrain'. Experimental.", "option", "t2v", Path) = None,
    parser_multitasks: ("Side objectives for parser CNN, e.g. 'dep' or 'dep,tag'", "option", "pt", str) = "",
    entity_multitasks: ("Side objectives for NER CNN, e.g. 'dep' or 'dep,tag'", "option", "et", str) = "",
    noise_level: ("Amount of corruption for data augmentation", "option", "nl", float) = 0.0,
    orth_variant_level: ("Amount of orthography variation for data augmentation", "option", "ovl", float) = 0.0,
    eval_beam_widths: ("Beam widths to evaluate, e.g. 4,8", "option", "bw", str) = "",
    gold_preproc: ("Use gold preprocessing", "flag", "G", bool) = False,
    learn_tokens: ("Make parser learn gold-standard tokenization", "flag", "T", bool) = False,
    textcat_multilabel: ("Textcat classes aren't mutually exclusive (multilabel)", "flag", "TML", bool) = False,
    textcat_arch: ("Textcat model architecture", "option", "ta", str) = "bow",
    textcat_positive_label: ("Textcat positive label for binary classes with two labels", "option", "tpl", str) = None,
    tag_map_path: ("Location of JSON-formatted tag map", "option", "tm", Path) = None,
    verbose: ("Display more information for debug", "flag", "VV", bool) = False,
    debug: ("Run data diagnostics before training", "flag", "D", bool) = False,
    # fmt: on
):
    """
    Train or update a spaCy model. Requires data to be formatted in spaCy's
    JSON format. To convert data from other formats, use the `spacy convert`
    command.
    """
    util.fix_random_seed()
    util.set_env_log(verbose)

    # Make sure all files and paths exists if they are needed
    train_path = util.ensure_path(train_path)
    dev_path = util.ensure_path(dev_path)
    meta_path = util.ensure_path(meta_path)
    output_path = util.ensure_path(output_path)
    if raw_text is not None:
        raw_text = list(srsly.read_jsonl(raw_text))
    if not train_path or not train_path.exists():
        msg.fail("Training data not found", train_path, exits=1)
    if not dev_path or not dev_path.exists():
        msg.fail("Development data not found", dev_path, exits=1)
    if meta_path is not None and not meta_path.exists():
        msg.fail("Can't find model meta.json", meta_path, exits=1)
    meta = srsly.read_json(meta_path) if meta_path else {}
    if output_path.exists() and [p for p in output_path.iterdir() if p.is_dir()]:
        msg.warn(
            "Output directory is not empty",
            "This can lead to unintended side effects when saving the model. "
            "Please use an empty directory or a different path instead. If "
            "the specified output path doesn't exist, the directory will be "
            "created for you.",
        )
    if not output_path.exists():
        output_path.mkdir()
        msg.good(f"Created output directory: {output_path}")

    tag_map = {}
    if tag_map_path is not None:
        tag_map = srsly.read_json(tag_map_path)
    # Take dropout and batch size as generators of values -- dropout
    # starts high and decays sharply, to force the optimizer to explore.
    # Batch size starts at 1 and grows, so that we make updates quickly
    # at the beginning of training.
    dropout_rates = util.decaying(
        util.env_opt("dropout_from", 0.2),
        util.env_opt("dropout_to", 0.2),
        util.env_opt("dropout_decay", 0.0),
    )
    batch_sizes = util.compounding(
        util.env_opt("batch_from", 100.0),
        util.env_opt("batch_to", 1000.0),
        util.env_opt("batch_compound", 1.001),
    )

    if not eval_beam_widths:
        eval_beam_widths = [1]
    else:
        eval_beam_widths = [int(bw) for bw in eval_beam_widths.split(",")]
        if 1 not in eval_beam_widths:
            eval_beam_widths.append(1)
        eval_beam_widths.sort()
    has_beam_widths = eval_beam_widths != [1]

    default_dir = Path(__file__).parent.parent / "ml" / "models" / "defaults"

    # Set up the base model and pipeline. If a base model is specified, load
    # the model and make sure the pipeline matches the pipeline setting. If
    # training starts from a blank model, intitalize the language class.
    pipeline = [p.strip() for p in pipeline.split(",")]
    msg.text(f"Training pipeline: {pipeline}")
    disabled_pipes = None
    pipes_added = False
    if use_gpu >= 0:
        activated_gpu = None
        try:
            activated_gpu = set_gpu(use_gpu)
        except Exception as e:
            msg.warn(f"Exception: {e}")
        if activated_gpu is not None:
            msg.text(f"Using GPU: {use_gpu}")
        else:
            msg.warn(f"Unable to activate GPU: {use_gpu}")
            msg.text("Using CPU only")
            use_gpu = -1
    if base_model:
        msg.text(f"Starting with base model '{base_model}'")
        nlp = util.load_model(base_model)
        if nlp.lang != lang:
            msg.fail(
                f"Model language ('{nlp.lang}') doesn't match language "
                f"specified as `lang` argument ('{lang}') ",
                exits=1,
            )
        if vectors:
            msg.text(f"Loading vectors from model '{vectors}'")
            _load_vectors(nlp, vectors)

        nlp.select_pipes(disable=[p for p in nlp.pipe_names if p not in pipeline])
        for pipe in pipeline:
            # first, create the model.
            # Bit of a hack after the refactor to get the vectors into a default config
            # use train-from-config instead :-)
            if pipe == "parser":
                config_loc = default_dir / "parser_defaults.cfg"
            elif pipe == "tagger":
                config_loc = default_dir / "tagger_defaults.cfg"
            elif pipe == "ner":
                config_loc = default_dir / "ner_defaults.cfg"
            elif pipe == "textcat":
                config_loc = default_dir / "textcat_defaults.cfg"
            elif pipe == "senter":
                config_loc = default_dir / "senter_defaults.cfg"
            else:
                raise ValueError(f"Component {pipe} currently not supported.")
            pipe_cfg = util.load_config(config_loc, create_objects=False)
            if vectors:
                pretrained_config = {
                    "@architectures": "spacy.VocabVectors.v1",
                    "name": vectors,
                }
                pipe_cfg["model"]["tok2vec"]["pretrained_vectors"] = pretrained_config

            if pipe == "parser":
                pipe_cfg["learn_tokens"] = learn_tokens
            elif pipe == "textcat":
                pipe_cfg["exclusive_classes"] = not textcat_multilabel
                pipe_cfg["architecture"] = textcat_arch
                pipe_cfg["positive_label"] = textcat_positive_label

            if pipe not in nlp.pipe_names:
                msg.text(f"Adding component to base model '{pipe}'")
                nlp.add_pipe(nlp.create_pipe(pipe, config=pipe_cfg))
                pipes_added = True
            elif replace_components:
                msg.text(f"Replacing component from base model '{pipe}'")
                nlp.replace_pipe(pipe, nlp.create_pipe(pipe, config=pipe_cfg))
                pipes_added = True
            else:
                if pipe == "textcat":
                    textcat_cfg = nlp.get_pipe("textcat").cfg
                    base_cfg = {
                        "exclusive_classes": textcat_cfg["exclusive_classes"],
                        "architecture": textcat_cfg["architecture"],
                        "positive_label": textcat_cfg["positive_label"],
                    }
                    if base_cfg != pipe_cfg:
                        msg.fail(
                            f"The base textcat model configuration does"
                            f"not match the provided training options. "
                            f"Existing cfg: {base_cfg}, provided cfg: {pipe_cfg}",
                            exits=1,
                        )
                msg.text(f"Extending component from base model '{pipe}'")
        disabled_pipes = nlp.select_pipes(
            disable=[p for p in nlp.pipe_names if p not in pipeline]
        )
    else:
        msg.text(f"Starting with blank model '{lang}'")
        lang_cls = util.get_lang_class(lang)
        nlp = lang_cls()

        if vectors:
            msg.text(f"Loading vectors from model '{vectors}'")
            _load_vectors(nlp, vectors)

        for pipe in pipeline:
            # first, create the model.
            # Bit of a hack after the refactor to get the vectors into a default config
            # use train-from-config instead :-)
            if pipe == "parser":
                config_loc = default_dir / "parser_defaults.cfg"
            elif pipe == "tagger":
                config_loc = default_dir / "tagger_defaults.cfg"
            elif pipe == "morphologizer":
                config_loc = default_dir / "morphologizer_defaults.cfg"
            elif pipe == "ner":
                config_loc = default_dir / "ner_defaults.cfg"
            elif pipe == "textcat":
                config_loc = default_dir / "textcat_defaults.cfg"
            elif pipe == "senter":
                config_loc = default_dir / "senter_defaults.cfg"
            else:
                raise ValueError(f"Component {pipe} currently not supported.")
            pipe_cfg = util.load_config(config_loc, create_objects=False)
            if vectors:
                pretrained_config = {
                    "@architectures": "spacy.VocabVectors.v1",
                    "name": vectors,
                }
                pipe_cfg["model"]["tok2vec"]["pretrained_vectors"] = pretrained_config

            if pipe == "parser":
                pipe_cfg["learn_tokens"] = learn_tokens
            elif pipe == "textcat":
                pipe_cfg["exclusive_classes"] = not textcat_multilabel
                pipe_cfg["architecture"] = textcat_arch
                pipe_cfg["positive_label"] = textcat_positive_label

            pipe = nlp.create_pipe(pipe, config=pipe_cfg)
            nlp.add_pipe(pipe)

    # Update tag map with provided mapping
    nlp.vocab.morphology.tag_map.update(tag_map)

    # Multitask objectives
    multitask_options = [("parser", parser_multitasks), ("ner", entity_multitasks)]
    for pipe_name, multitasks in multitask_options:
        if multitasks:
            if pipe_name not in pipeline:
                msg.fail(
                    f"Can't use multitask objective without '{pipe_name}' in "
                    f"the pipeline"
                )
            pipe = nlp.get_pipe(pipe_name)
            for objective in multitasks.split(","):
                pipe.add_multitask_objective(objective)

    # Prepare training corpus
    msg.text(f"Counting training words (limit={n_examples})")
    corpus = GoldCorpus(train_path, dev_path, limit=n_examples)
    n_train_words = corpus.count_train()

    if base_model and not pipes_added:
        # Start with an existing model, use default optimizer
        optimizer = create_default_optimizer()
    else:
        # Start with a blank model, call begin_training
        cfg = {"device": use_gpu}
        optimizer = nlp.begin_training(lambda: corpus.train_examples, **cfg)
    nlp._optimizer = None

    # Load in pretrained weights (TODO: this may be broken in the config rewrite)
    if init_tok2vec is not None:
        components = _load_pretrained_tok2vec(nlp, init_tok2vec)
        msg.text(f"Loaded pretrained tok2vec for: {components}")

    # Verify textcat config
    if "textcat" in pipeline:
        textcat_labels = nlp.get_pipe("textcat").cfg.get("labels", [])
        if textcat_positive_label and textcat_positive_label not in textcat_labels:
            msg.fail(
                f"The textcat_positive_label (tpl) '{textcat_positive_label}' "
                f"does not match any label in the training data.",
                exits=1,
            )
        if textcat_positive_label and len(textcat_labels) != 2:
            msg.fail(
                "A textcat_positive_label (tpl) '{textcat_positive_label}' was "
                "provided for training data that does not appear to be a "
                "binary classification problem with two labels.",
                exits=1,
            )
        train_data = corpus.train_data(
            nlp,
            noise_level=noise_level,
            gold_preproc=gold_preproc,
            max_length=0,
            ignore_misaligned=True,
        )
        train_labels = set()
        if textcat_multilabel:
            multilabel_found = False
            for ex in train_data:
                train_labels.update(ex.gold.cats.keys())
                if list(ex.gold.cats.values()).count(1.0) != 1:
                    multilabel_found = True
            if not multilabel_found and not base_model:
                msg.warn(
                    "The textcat training instances look like they have "
                    "mutually-exclusive classes. Remove the flag "
                    "'--textcat-multilabel' to train a classifier with "
                    "mutually-exclusive classes."
                )
        if not textcat_multilabel:
            for ex in train_data:
                train_labels.update(ex.gold.cats.keys())
                if list(ex.gold.cats.values()).count(1.0) != 1 and not base_model:
                    msg.warn(
                        "Some textcat training instances do not have exactly "
                        "one positive label. Modifying training options to "
                        "include the flag '--textcat-multilabel' for classes "
                        "that are not mutually exclusive."
                    )
                    nlp.get_pipe("textcat").cfg["exclusive_classes"] = False
                    textcat_multilabel = True
                    break
        if base_model and set(textcat_labels) != train_labels:
            msg.fail(
                f"Cannot extend textcat model using data with different "
                f"labels. Base model labels: {textcat_labels}, training data "
                f"labels: {list(train_labels)}",
                exits=1,
            )
        if textcat_multilabel:
            msg.text(
                f"Textcat evaluation score: ROC AUC score macro-averaged across "
                f"the labels '{', '.join(textcat_labels)}'"
            )
        elif textcat_positive_label and len(textcat_labels) == 2:
            msg.text(
                f"Textcat evaluation score: F1-score for the "
                f"label '{textcat_positive_label}'"
            )
        elif len(textcat_labels) > 1:
            if len(textcat_labels) == 2:
                msg.warn(
                    "If the textcat component is a binary classifier with "
                    "exclusive classes, provide '--textcat_positive_label' for "
                    "an evaluation on the positive class."
                )
            msg.text(
                f"Textcat evaluation score: F1-score macro-averaged across "
                f"the labels '{', '.join(textcat_labels)}'"
            )
        else:
            msg.fail(
                "Unsupported textcat configuration. Use `spacy debug-data` "
                "for more information."
            )

    # fmt: off
    row_head, output_stats = _configure_training_output(pipeline, use_gpu, has_beam_widths)
    row_widths = [len(w) for w in row_head]
    row_settings = {"widths": row_widths, "aligns": tuple(["r" for i in row_head]), "spacing": 2}
    # fmt: on
    print("")
    msg.row(row_head, **row_settings)
    msg.row(["-" * width for width in row_settings["widths"]], **row_settings)
    try:
        iter_since_best = 0
        best_score = 0.0
        for i in range(n_iter):
            train_data = corpus.train_dataset(
                nlp,
                noise_level=noise_level,
                orth_variant_level=orth_variant_level,
                gold_preproc=gold_preproc,
                max_length=0,
                ignore_misaligned=True,
            )
            if raw_text:
                random.shuffle(raw_text)
                raw_batches = util.minibatch(
                    (nlp.make_doc(rt["text"]) for rt in raw_text), size=8
                )
            words_seen = 0
            with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
                losses = {}
                for batch in util.minibatch_by_words(train_data, size=batch_sizes):
                    if not batch:
                        continue
                    try:
                        nlp.update(
                            batch,
                            sgd=optimizer,
                            drop=next(dropout_rates),
                            losses=losses,
                        )
                    except ValueError as e:
                        err = "Error during training"
                        if init_tok2vec:
                            err += " Did you provide the same parameters during 'train' as during 'pretrain'?"
                        msg.fail(err, f"Original error message: {e}", exits=1)
                    if raw_text:
                        # If raw text is available, perform 'rehearsal' updates,
                        # which use unlabelled data to reduce overfitting.
                        raw_batch = list(next(raw_batches))
                        nlp.rehearse(raw_batch, sgd=optimizer, losses=losses)
                    docs = [ex.doc for ex in batch]
                    if not int(os.environ.get("LOG_FRIENDLY", 0)):
                        pbar.update(sum(len(doc) for doc in docs))
                    words_seen += sum(len(doc) for doc in docs)
            with nlp.use_params(optimizer.averages):
                util.set_env_log(False)
                epoch_model_path = output_path / f"model{i}"
                nlp.to_disk(epoch_model_path)
                nlp_loaded = util.load_model_from_path(epoch_model_path)
                for beam_width in eval_beam_widths:
                    for name, component in nlp_loaded.pipeline:
                        if hasattr(component, "cfg"):
                            component.cfg["beam_width"] = beam_width
                    dev_dataset = list(
                        corpus.dev_dataset(
                            nlp_loaded,
                            gold_preproc=gold_preproc,
                            ignore_misaligned=True,
                        )
                    )
                    nwords = sum(len(ex.doc) for ex in dev_dataset)
                    start_time = timer()
                    scorer = nlp_loaded.evaluate(dev_dataset, verbose=verbose)
                    end_time = timer()
                    if use_gpu < 0:
                        gpu_wps = None
                        cpu_wps = nwords / (end_time - start_time)
                    else:
                        gpu_wps = nwords / (end_time - start_time)
                        with use_ops("numpy"):
                            nlp_loaded = util.load_model_from_path(epoch_model_path)
                            for name, component in nlp_loaded.pipeline:
                                if hasattr(component, "cfg"):
                                    component.cfg["beam_width"] = beam_width
                            dev_dataset = list(
                                corpus.dev_dataset(
                                    nlp_loaded,
                                    gold_preproc=gold_preproc,
                                    ignore_misaligned=True,
                                )
                            )
                            start_time = timer()
                            scorer = nlp_loaded.evaluate(dev_dataset, verbose=verbose)
                            end_time = timer()
                            cpu_wps = nwords / (end_time - start_time)
                    acc_loc = output_path / f"model{i}" / "accuracy.json"
                    srsly.write_json(acc_loc, scorer.scores)

                    # Update model meta.json
                    meta["lang"] = nlp.lang
                    meta["pipeline"] = nlp.pipe_names
                    meta["spacy_version"] = f">={about.__version__}"
                    if beam_width == 1:
                        meta["speed"] = {
                            "nwords": nwords,
                            "cpu": cpu_wps,
                            "gpu": gpu_wps,
                        }
                        meta.setdefault("accuracy", {})
                        for component in nlp.pipe_names:
                            for metric in _get_metrics(component):
                                meta["accuracy"][metric] = scorer.scores[metric]
                    else:
                        meta.setdefault("beam_accuracy", {})
                        meta.setdefault("beam_speed", {})
                        for component in nlp.pipe_names:
                            for metric in _get_metrics(component):
                                meta["beam_accuracy"][metric] = scorer.scores[metric]
                        meta["beam_speed"][beam_width] = {
                            "nwords": nwords,
                            "cpu": cpu_wps,
                            "gpu": gpu_wps,
                        }
                    meta["vectors"] = {
                        "width": nlp.vocab.vectors_length,
                        "vectors": len(nlp.vocab.vectors),
                        "keys": nlp.vocab.vectors.n_keys,
                        "name": nlp.vocab.vectors.name,
                    }
                    meta.setdefault("name", f"model{i}")
                    meta.setdefault("version", version)
                    meta["labels"] = nlp.meta["labels"]
                    meta_loc = output_path / f"model{i}" / "meta.json"
                    srsly.write_json(meta_loc, meta)
                    util.set_env_log(verbose)

                    progress = _get_progress(
                        i,
                        losses,
                        scorer.scores,
                        output_stats,
                        beam_width=beam_width if has_beam_widths else None,
                        cpu_wps=cpu_wps,
                        gpu_wps=gpu_wps,
                    )
                    if i == 0 and "textcat" in pipeline:
                        textcats_per_cat = scorer.scores.get("textcats_per_cat", {})
                        for cat, cat_score in textcats_per_cat.items():
                            if cat_score.get("roc_auc_score", 0) < 0:
                                msg.warn(
                                    f"Textcat ROC AUC score is undefined due to "
                                    f"only one value in label '{cat}'."
                                )
                    msg.row(progress, **row_settings)
                # Early stopping
                if n_early_stopping is not None:
                    current_score = _score_for_model(meta)
                    if current_score < best_score:
                        iter_since_best += 1
                    else:
                        iter_since_best = 0
                        best_score = current_score
                    if iter_since_best >= n_early_stopping:
                        msg.text(
                            f"Early stopping, best iteration is: {i - iter_since_best}"
                        )
                        msg.text(
                            f"Best score = {best_score}; Final iteration score = {current_score}"
                        )
                        break
    except Exception as e:
        msg.warn(f"Aborting and saving final best model. Encountered exception: {e}")
    finally:
        best_pipes = nlp.pipe_names
        if disabled_pipes:
            disabled_pipes.restore()
        with nlp.use_params(optimizer.averages):
            final_model_path = output_path / "model-final"
            nlp.to_disk(final_model_path)
            meta_loc = output_path / "model-final" / "meta.json"
            final_meta = srsly.read_json(meta_loc)
            final_meta.setdefault("accuracy", {})
            final_meta["accuracy"].update(meta.get("accuracy", {}))
            final_meta.setdefault("speed", {})
            final_meta["speed"].setdefault("cpu", None)
            final_meta["speed"].setdefault("gpu", None)
            meta.setdefault("speed", {})
            meta["speed"].setdefault("cpu", None)
            meta["speed"].setdefault("gpu", None)
            # combine cpu and gpu speeds with the base model speeds
            if final_meta["speed"]["cpu"] and meta["speed"]["cpu"]:
                speed = _get_total_speed(
                    [final_meta["speed"]["cpu"], meta["speed"]["cpu"]]
                )
                final_meta["speed"]["cpu"] = speed
            if final_meta["speed"]["gpu"] and meta["speed"]["gpu"]:
                speed = _get_total_speed(
                    [final_meta["speed"]["gpu"], meta["speed"]["gpu"]]
                )
                final_meta["speed"]["gpu"] = speed
            # if there were no speeds to update, overwrite with meta
            if (
                final_meta["speed"]["cpu"] is None
                and final_meta["speed"]["gpu"] is None
            ):
                final_meta["speed"].update(meta["speed"])
            # note: beam speeds are not combined with the base model
            if has_beam_widths:
                final_meta.setdefault("beam_accuracy", {})
                final_meta["beam_accuracy"].update(meta.get("beam_accuracy", {}))
                final_meta.setdefault("beam_speed", {})
                final_meta["beam_speed"].update(meta.get("beam_speed", {}))
            srsly.write_json(meta_loc, final_meta)
        msg.good("Saved model to output directory", final_model_path)
        with msg.loading("Creating best model..."):
            best_model_path = _collate_best_model(final_meta, output_path, best_pipes)
        msg.good("Created best model", best_model_path)


def _score_for_model(meta):
    """ Returns mean score between tasks in pipeline that can be used for early stopping. """
    mean_acc = list()
    pipes = meta["pipeline"]
    acc = meta["accuracy"]
    if "tagger" in pipes:
        mean_acc.append(acc["tags_acc"])
    if "morphologizer" in pipes:
        mean_acc.append((acc["morphs_acc"] + acc["pos_acc"]) / 2)
    if "parser" in pipes:
        mean_acc.append((acc["uas"] + acc["las"]) / 2)
    if "ner" in pipes:
        mean_acc.append((acc["ents_p"] + acc["ents_r"] + acc["ents_f"]) / 3)
    if "textcat" in pipes:
        mean_acc.append(acc["textcat_score"])
    if "senter" in pipes:
        mean_acc.append((acc["sent_p"] + acc["sent_r"] + acc["sent_f"]) / 3)
    return sum(mean_acc) / len(mean_acc)


@contextlib.contextmanager
def _create_progress_bar(total):
    if int(os.environ.get("LOG_FRIENDLY", 0)):
        yield
    else:
        pbar = tqdm.tqdm(total=total, leave=False)
        yield pbar


def _load_vectors(nlp, vectors):
    loaded_model = util.load_model(vectors, vocab=nlp.vocab)
    for lex in nlp.vocab:
        values = {}
        for attr, func in nlp.vocab.lex_attr_getters.items():
            # These attrs are expected to be set by data. Others should
            # be set by calling the language functions.
            if attr not in (CLUSTER, PROB, IS_OOV, LANG):
                values[lex.vocab.strings[attr]] = func(lex.orth_)
        lex.set_attrs(**values)
        lex.is_oov = False
    return loaded_model


def _load_pretrained_tok2vec(nlp, loc):
    """Load pretrained weights for the 'token-to-vector' part of the component
    models, which is typically a CNN. See 'spacy pretrain'. Experimental.
    """
    with loc.open("rb") as file_:
        weights_data = file_.read()
    loaded = []
    for name, component in nlp.pipeline:
        if hasattr(component, "model") and component.model.has_ref("tok2vec"):
            component.get_ref("tok2vec").from_bytes(weights_data)
            loaded.append(name)
    return loaded


def _collate_best_model(meta, output_path, components):
    bests = {}
    meta.setdefault("accuracy", {})
    for component in components:
        bests[component] = _find_best(output_path, component)
    best_dest = output_path / "model-best"
    shutil.copytree(str(output_path / "model-final"), str(best_dest))
    for component, best_component_src in bests.items():
        shutil.rmtree(str(best_dest / component))
        shutil.copytree(str(best_component_src / component), str(best_dest / component))
        accs = srsly.read_json(best_component_src / "accuracy.json")
        for metric in _get_metrics(component):
            meta["accuracy"][metric] = accs[metric]
    srsly.write_json(best_dest / "meta.json", meta)
    return best_dest


def _find_best(experiment_dir, component):
    accuracies = []
    for epoch_model in experiment_dir.iterdir():
        if epoch_model.is_dir() and epoch_model.parts[-1] != "model-final":
            accs = srsly.read_json(epoch_model / "accuracy.json")
            scores = [accs.get(metric, 0.0) for metric in _get_metrics(component)]
            # remove per_type dicts from score list for max() comparison
            scores = [score for score in scores if isinstance(score, float)]
            accuracies.append((scores, epoch_model))
    if accuracies:
        return max(accuracies)[1]
    else:
        return None


def _get_metrics(component):
    if component == "parser":
        return ("las", "uas", "las_per_type", "sent_f", "token_acc")
    elif component == "tagger":
        return ("tags_acc", "token_acc")
    elif component == "morphologizer":
        return ("morphs_acc", "pos_acc", "token_acc")
    elif component == "ner":
        return ("ents_f", "ents_p", "ents_r", "ents_per_type", "token_acc")
    elif component == "senter":
        return ("sent_f", "sent_p", "sent_r", "token_acc")
    elif component == "textcat":
        return ("textcat_score", "token_acc")
    return ("token_acc",)


def _configure_training_output(pipeline, use_gpu, has_beam_widths):
    row_head = ["Itn"]
    output_stats = []
    for pipe in pipeline:
        if pipe == "tagger":
            row_head.extend(["Tag Loss ", " Tag %  "])
            output_stats.extend(["tag_loss", "tags_acc"])
        elif pipe == "morphologizer" or pipe == "morphologizertagger":
            row_head.extend(["Morph Loss ", " Morph %  ", " POS % "])
            output_stats.extend(["morph_loss", "morphs_acc", "pos_acc"])
        elif pipe == "parser":
            row_head.extend(
                ["Dep Loss ", " UAS  ", " LAS  ", "Sent P", "Sent R", "Sent F"]
            )
            output_stats.extend(
                ["dep_loss", "uas", "las", "sent_p", "sent_r", "sent_f"]
            )
        elif pipe == "ner":
            row_head.extend(["NER Loss ", "NER P ", "NER R ", "NER F "])
            output_stats.extend(["ner_loss", "ents_p", "ents_r", "ents_f"])
        elif pipe == "textcat":
            row_head.extend(["Textcat Loss", "Textcat"])
            output_stats.extend(["textcat_loss", "textcat_score"])
        elif pipe == "senter":
            row_head.extend(["Senter Loss", "Sent P", "Sent R", "Sent F"])
            output_stats.extend(["senter_loss", "sent_p", "sent_r", "sent_f"])
    row_head.extend(["Token %", "CPU WPS"])
    output_stats.extend(["token_acc", "cpu_wps"])

    if use_gpu >= 0:
        row_head.extend(["GPU WPS"])
        output_stats.extend(["gpu_wps"])

    if has_beam_widths:
        row_head.insert(1, "Beam W.")
    # remove duplicates
    row_head_dict = {k: 1 for k in row_head}
    output_stats_dict = {k: 1 for k in output_stats}
    return row_head_dict.keys(), output_stats_dict.keys()


def _get_progress(
    itn, losses, dev_scores, output_stats, beam_width=None, cpu_wps=0.0, gpu_wps=0.0
):
    scores = {}
    for stat in output_stats:
        scores[stat] = 0.0
    scores["dep_loss"] = losses.get("parser", 0.0)
    scores["ner_loss"] = losses.get("ner", 0.0)
    scores["tag_loss"] = losses.get("tagger", 0.0)
    scores["morph_loss"] = losses.get("morphologizer", 0.0)
    scores["textcat_loss"] = losses.get("textcat", 0.0)
    scores["senter_loss"] = losses.get("senter", 0.0)
    scores["cpu_wps"] = cpu_wps
    scores["gpu_wps"] = gpu_wps or 0.0
    scores.update(dev_scores)
    formatted_scores = []
    for stat in output_stats:
        format_spec = "{:.3f}"
        if stat.endswith("_wps"):
            format_spec = "{:.0f}"
        formatted_scores.append(format_spec.format(scores[stat]))
    result = [itn + 1]
    result.extend(formatted_scores)
    if beam_width is not None:
        result.insert(1, beam_width)
    return result


def _get_total_speed(speeds):
    seconds_per_word = 0.0
    for words_per_second in speeds:
        if words_per_second is None:
            return None
        seconds_per_word += 1.0 / words_per_second
    return 1.0 / seconds_per_word
