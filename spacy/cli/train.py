# coding: utf8
from __future__ import unicode_literals, division, print_function

import plac
import os
from pathlib import Path
import tqdm
from thinc.neural._classes.model import Model
from timeit import default_timer as timer
import shutil
import srsly
from wasabi import Printer
import contextlib
import random

from .._ml import create_default_optimizer
from ..attrs import PROB, IS_OOV, CLUSTER, LANG
from ..gold import GoldCorpus
from .. import util
from .. import about


@plac.annotations(
    lang=("Model language", "positional", None, str),
    output_path=("Output directory to store model in", "positional", None, Path),
    train_path=("Location of JSON-formatted training data", "positional", None, Path),
    dev_path=("Location of JSON-formatted development data", "positional", None, Path),
    raw_text=(
        "Path to jsonl file with unlabelled text documents.",
        "option",
        "rt",
        Path,
    ),
    base_model=("Name of model to update (optional)", "option", "b", str),
    pipeline=("Comma-separated names of pipeline components", "option", "p", str),
    vectors=("Model to load vectors from", "option", "v", str),
    n_iter=("Number of iterations", "option", "n", int),
    n_examples=("Number of examples", "option", "ns", int),
    use_gpu=("Use GPU", "option", "g", int),
    version=("Model version", "option", "V", str),
    meta_path=("Optional path to meta.json to use as base.", "option", "m", Path),
    init_tok2vec=(
        "Path to pretrained weights for the token-to-vector parts of the models. See 'spacy pretrain'. Experimental.",
        "option",
        "t2v",
        Path,
    ),
    parser_multitasks=(
        "Side objectives for parser CNN, e.g. 'dep' or 'dep,tag'",
        "option",
        "pt",
        str,
    ),
    entity_multitasks=(
        "Side objectives for NER CNN, e.g. 'dep' or 'dep,tag'",
        "option",
        "et",
        str,
    ),
    noise_level=("Amount of corruption for data augmentation", "option", "nl", float),
    eval_beam_widths=("Beam widths to evaluate, e.g. 4,8", "option", "bw", str),
    gold_preproc=("Use gold preprocessing", "flag", "G", bool),
    learn_tokens=("Make parser learn gold-standard tokenization", "flag", "T", bool),
    verbose=("Display more information for debug", "flag", "VV", bool),
    debug=("Run data diagnostics before training", "flag", "D", bool),
)
def train(
    lang,
    output_path,
    train_path,
    dev_path,
    raw_text=None,
    base_model=None,
    pipeline="tagger,parser,ner",
    vectors=None,
    n_iter=30,
    n_examples=0,
    use_gpu=-1,
    version="0.0.0",
    meta_path=None,
    init_tok2vec=None,
    parser_multitasks="",
    entity_multitasks="",
    noise_level=0.0,
    eval_beam_widths="",
    gold_preproc=False,
    learn_tokens=False,
    verbose=False,
    debug=False,
):
    """
    Train or update a spaCy model. Requires data to be formatted in spaCy's
    JSON format. To convert data from other formats, use the `spacy convert`
    command.
    """
    msg = Printer()
    util.fix_random_seed()
    util.set_env_log(verbose)

    # Make sure all files and paths exists if they are needed
    train_path = util.ensure_path(train_path)
    dev_path = util.ensure_path(dev_path)
    meta_path = util.ensure_path(meta_path)
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

    # Set up the base model and pipeline. If a base model is specified, load
    # the model and make sure the pipeline matches the pipeline setting. If
    # training starts from a blank model, intitalize the language class.
    pipeline = [p.strip() for p in pipeline.split(",")]
    msg.text("Training pipeline: {}".format(pipeline))
    if base_model:
        msg.text("Starting with base model '{}'".format(base_model))
        nlp = util.load_model(base_model)
        if nlp.lang != lang:
            msg.fail(
                "Model language ('{}') doesn't match language specified as "
                "`lang` argument ('{}') ".format(nlp.lang, lang),
                exits=1,
            )
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipeline]
        nlp.disable_pipes(*other_pipes)
        for pipe in pipeline:
            if pipe not in nlp.pipe_names:
                nlp.add_pipe(nlp.create_pipe(pipe))
    else:
        msg.text("Starting with blank model '{}'".format(lang))
        lang_cls = util.get_lang_class(lang)
        nlp = lang_cls()
        for pipe in pipeline:
            nlp.add_pipe(nlp.create_pipe(pipe))

    if learn_tokens:
        nlp.add_pipe(nlp.create_pipe("merge_subtokens"))

    if vectors:
        msg.text("Loading vector from model '{}'".format(vectors))
        _load_vectors(nlp, vectors)

    # Multitask objectives
    multitask_options = [("parser", parser_multitasks), ("ner", entity_multitasks)]
    for pipe_name, multitasks in multitask_options:
        if multitasks:
            if pipe_name not in pipeline:
                msg.fail(
                    "Can't use multitask objective without '{}' in the "
                    "pipeline".format(pipe_name)
                )
            pipe = nlp.get_pipe(pipe_name)
            for objective in multitasks.split(","):
                pipe.add_multitask_objective(objective)

    # Prepare training corpus
    msg.text("Counting training words (limit={})".format(n_examples))
    corpus = GoldCorpus(train_path, dev_path, limit=n_examples)
    n_train_words = corpus.count_train()

    if base_model:
        # Start with an existing model, use default optimizer
        optimizer = create_default_optimizer(Model.ops)
    else:
        # Start with a blank model, call begin_training
        optimizer = nlp.begin_training(lambda: corpus.train_tuples, device=use_gpu)

    nlp._optimizer = None

    # Load in pre-trained weights
    if init_tok2vec is not None:
        components = _load_pretrained_tok2vec(nlp, init_tok2vec)
        msg.text("Loaded pretrained tok2vec for: {}".format(components))

    # fmt: off
    row_head = ["Itn", "Dep Loss", "NER Loss", "UAS", "NER P", "NER R", "NER F", "Tag %", "Token %", "CPU WPS", "GPU WPS"]
    row_widths = [3, 10, 10, 7, 7, 7, 7, 7, 7, 7, 7]
    if has_beam_widths:
        row_head.insert(1, "Beam W.")
        row_widths.insert(1, 7)
    row_settings = {"widths": row_widths, "aligns": tuple(["r" for i in row_head]), "spacing": 2}
    # fmt: on
    print("")
    msg.row(row_head, **row_settings)
    msg.row(["-" * width for width in row_settings["widths"]], **row_settings)
    try:
        for i in range(n_iter):
            train_docs = corpus.train_docs(
                nlp, noise_level=noise_level, gold_preproc=gold_preproc, max_length=0
            )
            if raw_text:
                random.shuffle(raw_text)
                raw_batches = util.minibatch(
                    (nlp.make_doc(rt["text"]) for rt in raw_text), size=8
                )
            words_seen = 0
            with tqdm.tqdm(total=n_train_words, leave=False) as pbar:
                losses = {}
                for batch in util.minibatch_by_words(train_docs, size=batch_sizes):
                    if not batch:
                        continue
                    docs, golds = zip(*batch)
                    nlp.update(
                        docs,
                        golds,
                        sgd=optimizer,
                        drop=next(dropout_rates),
                        losses=losses,
                    )
                    if raw_text:
                        # If raw text is available, perform 'rehearsal' updates,
                        # which use unlabelled data to reduce overfitting.
                        raw_batch = list(next(raw_batches))
                        nlp.rehearse(raw_batch, sgd=optimizer, losses=losses)
                    if not int(os.environ.get("LOG_FRIENDLY", 0)):
                        pbar.update(sum(len(doc) for doc in docs))
                    words_seen += sum(len(doc) for doc in docs)
            with nlp.use_params(optimizer.averages):
                util.set_env_log(False)
                epoch_model_path = output_path / ("model%d" % i)
                nlp.to_disk(epoch_model_path)
                nlp_loaded = util.load_model_from_path(epoch_model_path)
                for beam_width in eval_beam_widths:
                    for name, component in nlp_loaded.pipeline:
                        if hasattr(component, "cfg"):
                            component.cfg["beam_width"] = beam_width
                    dev_docs = list(
                        corpus.dev_docs(nlp_loaded, gold_preproc=gold_preproc)
                    )
                    nwords = sum(len(doc_gold[0]) for doc_gold in dev_docs)
                    start_time = timer()
                    scorer = nlp_loaded.evaluate(dev_docs, debug)
                    end_time = timer()
                    if use_gpu < 0:
                        gpu_wps = None
                        cpu_wps = nwords / (end_time - start_time)
                    else:
                        gpu_wps = nwords / (end_time - start_time)
                        with Model.use_device("cpu"):
                            nlp_loaded = util.load_model_from_path(epoch_model_path)
                            nlp_loaded.parser.cfg["beam_width"]
                            dev_docs = list(
                                corpus.dev_docs(nlp_loaded, gold_preproc=gold_preproc)
                            )
                            start_time = timer()
                            scorer = nlp_loaded.evaluate(dev_docs)
                            end_time = timer()
                            cpu_wps = nwords / (end_time - start_time)
                    acc_loc = output_path / ("model%d" % i) / "accuracy.json"
                    srsly.write_json(acc_loc, scorer.scores)

                    # Update model meta.json
                    meta["lang"] = nlp.lang
                    meta["pipeline"] = nlp.pipe_names
                    meta["spacy_version"] = ">=%s" % about.__version__
                    if beam_width == 1:
                        meta["speed"] = {
                            "nwords": nwords,
                            "cpu": cpu_wps,
                            "gpu": gpu_wps,
                        }
                        meta["accuracy"] = scorer.scores
                    else:
                        meta.setdefault("beam_accuracy", {})
                        meta.setdefault("beam_speed", {})
                        meta["beam_accuracy"][beam_width] = scorer.scores
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
                    meta.setdefault("name", "model%d" % i)
                    meta.setdefault("version", version)
                    meta_loc = output_path / ("model%d" % i) / "meta.json"
                    srsly.write_json(meta_loc, meta)
                    util.set_env_log(verbose)

                    progress = _get_progress(
                        i,
                        losses,
                        scorer.scores,
                        beam_width=beam_width if has_beam_widths else None,
                        cpu_wps=cpu_wps,
                        gpu_wps=gpu_wps,
                    )
                    msg.row(progress, **row_settings)
    finally:
        with nlp.use_params(optimizer.averages):
            final_model_path = output_path / "model-final"
            nlp.to_disk(final_model_path)
        msg.good("Saved model to output directory", final_model_path)
        with msg.loading("Creating best model..."):
            best_model_path = _collate_best_model(meta, output_path, nlp.pipe_names)
        msg.good("Created best model", best_model_path)


@contextlib.contextmanager
def _create_progress_bar(total):
    if int(os.environ.get("LOG_FRIENDLY", 0)):
        yield
    else:
        pbar = tqdm.tqdm(total=total, leave=False)
        yield pbar


def _load_vectors(nlp, vectors):
    util.load_model(vectors, vocab=nlp.vocab)
    for lex in nlp.vocab:
        values = {}
        for attr, func in nlp.vocab.lex_attr_getters.items():
            # These attrs are expected to be set by data. Others should
            # be set by calling the language functions.
            if attr not in (CLUSTER, PROB, IS_OOV, LANG):
                values[lex.vocab.strings[attr]] = func(lex.orth_)
        lex.set_attrs(**values)
        lex.is_oov = False


def _load_pretrained_tok2vec(nlp, loc):
    """Load pre-trained weights for the 'token-to-vector' part of the component
    models, which is typically a CNN. See 'spacy pretrain'. Experimental.
    """
    with loc.open("rb") as file_:
        weights_data = file_.read()
    loaded = []
    for name, component in nlp.pipeline:
        if hasattr(component, "model") and hasattr(component.model, "tok2vec"):
            component.tok2vec.from_bytes(weights_data)
            loaded.append(name)
    return loaded


def _collate_best_model(meta, output_path, components):
    bests = {}
    for component in components:
        bests[component] = _find_best(output_path, component)
    best_dest = output_path / "model-best"
    shutil.copytree(output_path / "model-final", best_dest)
    for component, best_component_src in bests.items():
        shutil.rmtree(best_dest / component)
        shutil.copytree(best_component_src / component, best_dest / component)
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
            accuracies.append((scores, epoch_model))
    if accuracies:
        return max(accuracies)[1]
    else:
        return None


def _get_metrics(component):
    if component == "parser":
        return ("las", "uas", "token_acc")
    elif component == "tagger":
        return ("tags_acc",)
    elif component == "ner":
        return ("ents_f", "ents_p", "ents_r")
    return ("token_acc",)


def _get_progress(itn, losses, dev_scores, beam_width=None, cpu_wps=0.0, gpu_wps=0.0):
    scores = {}
    for col in [
        "dep_loss",
        "tag_loss",
        "uas",
        "tags_acc",
        "token_acc",
        "ents_p",
        "ents_r",
        "ents_f",
        "cpu_wps",
        "gpu_wps",
    ]:
        scores[col] = 0.0
    scores["dep_loss"] = losses.get("parser", 0.0)
    scores["ner_loss"] = losses.get("ner", 0.0)
    scores["tag_loss"] = losses.get("tagger", 0.0)
    scores.update(dev_scores)
    scores["cpu_wps"] = cpu_wps
    scores["gpu_wps"] = gpu_wps or 0.0
    result = [
        itn,
        "{:.3f}".format(scores["dep_loss"]),
        "{:.3f}".format(scores["ner_loss"]),
        "{:.3f}".format(scores["uas"]),
        "{:.3f}".format(scores["ents_p"]),
        "{:.3f}".format(scores["ents_r"]),
        "{:.3f}".format(scores["ents_f"]),
        "{:.3f}".format(scores["tags_acc"]),
        "{:.3f}".format(scores["token_acc"]),
        "{:.0f}".format(scores["cpu_wps"]),
        "{:.0f}".format(scores["gpu_wps"]),
    ]
    if beam_width is not None:
        result.insert(1, beam_width)
    return result
