# coding: utf8
from __future__ import unicode_literals, division, print_function

import plac
from wasabi import msg
from pathlib import Path
import thinc
import thinc.rates
from thinc.api import layerize
from spacy.gold import GoldCorpus
import spacy
import spacy._ml
from spacy.pipeline.tok2vec import ControlledModel

from .. import util

registry = util.registry

CONFIG_STR = """
[training]
patience = 10
eval_frequency = 10
dropout = 0.2
init_tok2vec = null
vectors = null
max_epochs = 100
orth_variant_level = 0.0
gold_preproc = false
max_length = 0
use_gpu = 0
scores = ["ents_p",  "ents_r", "ents_f"]
score_weights = {"ents_f": 0.5, "las": 0.5}

[training.batch_size]
@schedules = "compounding.v1"
start = 100
stop = 1000
compound = 1.001

[optimizer]
@optimizers = "Adam.v1"
learn_rate = 0.001
beta1 = 0.9
beta2 = 0.999

[nlp]
lang = "en"
vectors = ${training:vectors}

[nlp.pipeline.tok2vec]
factory = "tok2vec"

[nlp.pipeline.ner]
factory = "ner"

[nlp.pipeline.ner.model]
@architectures = "transition_based_ner.v1"
nr_feature_tokens = 3
hidden_width = 64
maxout_pieces = 3

[nlp.pipeline.ner.model.tok2vec]
@architectures = "tok2vec_tensors.v1"
attributes = {"nO": 128}


[nlp.pipeline.tok2vec.model]
@architectures = "hash_embed_cnn.v1"
pretrained_vectors = ${nlp:vectors}
width = 128
depth = 4
window_size = 1
embed_size = 10000
maxout_pieces = 3
"""


# Of course, these would normally decorate the functions where they're defined.
# But for now...
registry.architectures.register("hash_embed_cnn.v1", func=spacy._ml.Tok2Vec)


@registry.architectures.register("transition_based_ner.v1")
def create_tb_ner_model(tok2vec, nr_feature_tokens, hidden_width, maxout_pieces):
    from thinc.v2v import Affine, Model
    from thinc.api import chain
    from spacy._ml import flatten
    from spacy._ml import PrecomputableAffine
    from spacy.syntax._parser_model import ParserModel

    token_vector_width = tok2vec.nO
    tok2vec = chain(tok2vec, flatten)
    tok2vec.nO = token_vector_width

    lower = PrecomputableAffine(
        hidden_width, nF=nr_feature_tokens, nI=tok2vec.nO, nP=maxout_pieces
    )
    lower.nP = maxout_pieces
    with Model.use_device("cpu"):
        upper = Affine(drop_factor=0.0)
    # Initialize weights at zero, as it's a classification layer.
    for desc in upper.descriptions.values():
        if desc.name == "W":
            desc.init = None
    return ParserModel(tok2vec, lower, upper)


@plac.annotations(
    # fmt: off
    train_path=("Location of JSON-formatted training data", "positional", None, Path),
    dev_path=("Location of JSON-formatted development data", "positional", None, Path),
    config_path=("Path to config file", "positional", None, Path),
    output_path=("Output directory to store model in", "option", "o", Path),
    meta_path=("Optional path to meta.json to use as base.", "option", "m", Path),
    raw_text=("Path to jsonl file with unlabelled text documents.", "option", "rt", Path),
    use_gpu=("Use GPU", "option", "g", int),
    # fmt: on
)
def train_from_config_cli(
    train_path,
    dev_path,
    config_path,
    output_path=None,
    meta_path=None,
    raw_text=None,
    use_gpu=False,
    debug=False,
    verbose=False,
):
    """
    Train or update a spaCy model. Requires data to be formatted in spaCy's
    JSON format. To convert data from other formats, use the `spacy convert`
    command.
    """
    # TODO: Unhack this
    with config_path.open("w") as file_:
        file_.write(CONFIG_STR)
    if not config_path or not config_path.exists():
        msg.fail("Config file not found", config_path, exits=1)
    if not train_path or not train_path.exists():
        msg.fail("Training data not found", train_path, exits=1)
    if not dev_path or not dev_path.exists():
        msg.fail("Development data not found", dev_path, exits=1)
    if meta_path is not None and not meta_path.exists():
        msg.fail("Can't find model meta.json", meta_path, exits=1)
    if output_path is not None and not output_path.exists():
        output_path.mkdir()

    try:
        train_from_config(
            config_path,
            {"train": train_path, "dev": dev_path},
            output_path=output_path,
            meta_path=meta_path,
            raw_text=raw_text,
            use_gpu=use_gpu,
        )
    except KeyboardInterrupt:
        msg.warn("Cancelled.")


def train_from_config(
    config_path,
    data_paths,
    raw_text=None,
    meta_path=None,
    output_path=None,
    use_gpu=None,
):
    config = util.load_from_config(config_path, create_objects=True)
    nlp = create_nlp_from_config(**config["nlp"])
    optimizer = config["optimizer"]
    corpus = GoldCorpus(data_paths["train"], data_paths["dev"])
    nlp.begin_training(
        lambda: corpus.train_tuples, device=config["training"]["use_gpu"]
    )
    assert nlp.entity.model.upper.nO is not None

    train_batches = create_train_batches(nlp, corpus, config["training"])
    evaluate = create_evaluation_callback(nlp, optimizer, corpus, config["training"])

    # Create iterator, which yields out info after each optimization step.
    training_step_iterator = train_while_improving(
        nlp,
        optimizer,
        train_batches,
        evaluate,
        config["training"]["dropout"],
        config["training"]["patience"],
        config["training"]["eval_frequency"],
    )

    msg.info("Training. Initial learn rate: {}".format(optimizer.alpha))
    print_row = setup_printer(config)

    try:
        for batch, info, is_best_checkpoint in training_step_iterator:
            if is_best_checkpoint is not None:
                print_row(info)
                if is_best_checkpoint and output_path is not None:
                    nlp.to_disk(output_path)
    finally:
        if output_path is not None:
            with nlp.use_params(optimizer.averages):
                final_model_path = output_path / "model-final"
                nlp.to_disk(final_model_path)
            msg.good("Saved model to output directory", final_model_path)
        # with msg.loading("Creating best model..."):
        #     best_model_path = _collate_best_model(meta, output_path, nlp.pipe_names)
        # msg.good("Created best model", best_model_path)


def create_nlp_from_config(lang, vectors, pipeline):
    lang_class = spacy.util.get_lang_class(lang)
    nlp = lang_class()
    if vectors is not None:
        spacy.cli.train._load_vectors(nlp, vectors)
    for name, component_cfg in pipeline.items():
        factory = component_cfg.pop("factory")
        component = nlp.create_pipe(factory, config=component_cfg)
        nlp.add_pipe(component, name=name)
    return nlp


def create_train_batches(nlp, corpus, cfg):
    while True:
        train_docs = corpus.train_docs(
            nlp,
            noise_level=0.0,
            orth_variant_level=cfg["orth_variant_level"],
            gold_preproc=cfg["gold_preproc"],
            max_length=cfg["max_length"],
            ignore_misaligned=True,
        )
        for batch in util.minibatch_by_words(train_docs, size=cfg["batch_size"]):
            yield batch


def create_evaluation_callback(nlp, optimizer, corpus, cfg):
    def evaluate():
        with nlp.use_params(optimizer.averages):
            dev_docs = list(
                corpus.dev_docs(
                    nlp, gold_preproc=cfg["gold_preproc"], ignore_misaligned=True
                )
            )
            scorer = nlp.evaluate(dev_docs)
            scores = scorer.scores
            # Calculate a weighted sum based on score_weights for the main score
            weights = cfg["score_weights"]
            weighted_score = sum(scores[s] * weights.get(s, 0.0) for s in weights)
        return weighted_score, scorer.scores

    return evaluate


def train_while_improving(
    nlp, optimizer, train_data, evaluate, dropout, patience, eval_frequency
):
    """Train until an evaluation stops improving. Works as a generator,
    with each iteration yielding a tuple `(batch, info, is_best_checkpoint)`,
    where info is a dict, and is_best_checkpoint is in [True, False, None] --
    None indicating that the iteration was not evaluated as a checkpoint.
    The evaluation is conducted by calling the evaluate callback, which should

    Positional arguments:
        nlp: The spaCy pipeline to evaluate.
        train_data (Iterable[Batch]): A generator of batches, with the training
            data. Each batch should be a Sized[Tuple[Input, Annot]]. The training
            data iterable needs to take care of iterating over the epochs and
            shuffling.
        evaluate (Callable[[], Tuple[float, Any]]): A callback to perform evaluation.
            The callback should take no arguments and return a tuple
            `(main_score, other_scores)`. The main_score should be a float where
            higher is better. other_scores can be any object.

    Every iteration, the function yields out a tuple with:

    * batch: A zipped sequence of Tuple[Doc, GoldParse] pairs.
    * info: A dict with various information about the last update (see below).
    * is_best_checkpoint: A value in None, False, True, indicating whether this
        was the best evaluation so far. You should use this to save the model
        checkpoints during training. If None, evaluation was not conducted on
        that iteration. False means evaluation was conducted, but a previous
        evaluation was better.

    The info dict provides the following information:

        epoch (int): How many passes over the data have been completed.
        step (int): How many steps have been completed.
        score (float): The main score form the last evaluation.
        other_scores: : The other scores from the last evaluation.
        loss: The accumulated losses throughout training.
        checkpoints: A list of previous results, where each result is a
            (score, step, epoch) tuple.
    """
    if isinstance(dropout, float):
        dropouts = thinc.rates.constant(dropout)
    else:
        dropouts = dropout
    results = []
    for step, batch in enumerate(train_data):
        dropout = next(dropouts)
        losses = {}
        gradients, accumulate_gradients = start_batch_gradients(optimizer)
        for subbatch in subdivide_batch(batch):
            docs, golds = zip(*subbatch)
            nlp.update(
                docs, golds, drop=dropout, losses=losses, sgd=accumulate_gradients
            )
        for key, (W, dW) in gradients.items():
            optimizer(W, dW, key=key)
        if not (step % eval_frequency):
            with nlp.use_params(optimizer.averages):
                score, other_scores = evaluate()
            results.append((score, step))
            is_best_checkpoint = score == max(results)[0]
        else:
            score, other_scores = (None, None)
            is_best_checkpoint = None
        info = {
            "step": step,
            "score": score,
            "other_scores": other_scores,
            "losses": losses,
            "checkpoints": results,
        }
        yield batch, info, is_best_checkpoint
        # Stop if no improvement in `patience` checkpoints
        best_score, best_step = max(results)
        if ((step - best_step) // eval_frequency) >= patience:
            break


def start_batch_gradients(optimizer):
    gradients = {}

    def accumulate_gradients(W, dW, key=None):
        if key in gradients:
            gradients[key][1] += dW
        else:
            gradients[key] = [W, dW]

    # TODO: Undo this hack
    accumulate_gradients.alpha = optimizer.alpha
    accumulate_gradients.b1 = optimizer.b1
    accumulate_gradients.b2 = optimizer.b2
    return gradients, accumulate_gradients


def subdivide_batch(batch):
    return [batch]


def setup_printer(config):
    score_cols = config["training"]["scores"]
    score_widths = [max(len(col), 6) for col in score_cols]
    loss_cols = ["Loss {}".format(pipe) for pipe in config["nlp"]["pipeline"]]
    loss_widths = [max(len(col), 8) for col in loss_cols]
    table_header = ["#"] + loss_cols + score_cols + ["Score"]
    table_header = [col.upper() for col in table_header]
    table_widths = [2] + loss_widths + score_widths + [6]
    table_aligns = ["r" for _ in table_widths]

    msg.row(table_header, widths=table_widths)
    msg.row(["-" * width for width in table_widths])

    def print_row(info):
        losses = [
            "{0:.2f}".format(info["losses"].get(col, 0.0))
            for col in config["nlp"]["pipeline"]
        ]
        scores = [
            "{0:.2f}".format(info["other_scores"].get(col, 0.0))
            for col in config["training"]["scores"]
        ]
        data = [info["step"]] + losses + scores + ["{0:.2f}".format(info["score"])]
        msg.row(data, widths=table_widths, aligns=table_aligns)

    return print_row


@registry.architectures.register("tok2vec_tensors.v1")
def tok2vec_tensors_v1(attributes):
    return ControlledModel("tok2vec", attributes=attributes)
