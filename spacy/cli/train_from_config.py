# coding: utf8
from __future__ import unicode_literals, division, print_function

import plac
from wasabi import msg
from pathlib import Path
import random
import thinc

from .. import util


@plac.annotations(
    # fmt: off
    output_path=("Output directory to store model in", "positional", None, Path),
    train_path=("Location of JSON-formatted training data", "positional", None, Path),
    dev_path=("Location of JSON-formatted development data", "positional", None, Path),
    config_path=("Path to config file", "option", "cfg", Path),
    meta_path=("Optional path to meta.json to use as base.", "option", "m", Path),
    raw_text=("Path to jsonl file with unlabelled text documents.", "option", "rt", Path),
    use_gpu=("Use GPU", "option", "g", int),
    # fmt: on
)
def train_from_config_cli(
    output_path,
    train_path,
    dev_path,
    config_path,
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
    if not config_path or not config_path.exists():
        msg.fail("Config file not found", config_path, exits=1)
    if not train_path or not train_path.exists():
        msg.fail("Training data not found", train_path, exits=1)
    if not dev_path or not dev_path.exists():
        msg.fail("Development data not found", dev_path, exits=1)
    if meta_path is not None and not meta_path.exists():
        msg.fail("Can't find model meta.json", meta_path, exits=1)
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

    train_from_config(
        config_path,
        {"train": train_path, "dev": dev_path},
        output_path=output_path,
        meta_path=meta_path,
        raw_text=raw_text,
        use_gpu=use_gpu,
    )


def train_from_config(
    config_path, data_paths, raw_text=None, meta_path=None, output_path=None
):
    config = util.load_from_config(config_path, data_paths, create_objects=True)
    # Unpack the config, and create the corpus, data batches and evaluator
    nlp = config["nlp"]
    optimizer = config["optimizer"]
    corpus = config["corpus"]

    train_batches = create_train_batches(nlp, corpus, config["training"])
    evaluate = create_evaluation_callback(nlp, corpus, config["training"])

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

    # Set up printing
    table_widths = [2, 4, 4]
    msg.info("Training. Initial learn rate: {}".format(optimizer.alpha))
    msg.row(["#", "Loss", "Score"], widths=table_widths)
    msg.row(["-" * width for width in table_widths])

    try:
        for batch, info, is_best_checkpoint in training_step_iterator:
            if is_best_checkpoint is not None:
                step, loss, score = get_stats(info)
                msg.row([step, f"{loss:.2f}", score], widths=table_widths)
                if is_best_checkpoint:
                    nlp.to_disk(output_path)
    finally:
        with nlp.use_params(optimizer.averages):
            final_model_path = output_path / "model-final"
            nlp.to_disk(final_model_path)
        msg.good("Saved model to output directory", final_model_path)
        # with msg.loading("Creating best model..."):
        #     best_model_path = _collate_best_model(meta, output_path, nlp.pipe_names)
        # msg.good("Created best model", best_model_path)


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
        random.shuffle(train_docs)
        for batch in util.minibatch_by_words(train_docs, size=cfg["batch_size"]):
            yield batch


def create_evaluation_callback(nlp, corpus, cfg):
    pass


def get_stats(info):
    return (0, 0, 0)


def train_while_improving(
    nlp, optimizer, train_data, evaluate, dropout, patience, eval_frequency,
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

    The following hyper-parameters (passed as keyword arguments) may need to be
    adjusted for your problem:

        learning_rate (float): Central learning rate to cycle around. 1e-5 is
            often good, but it can depend on the batch size.
        batch_size (int): The number of examples per iteration. Try 32 and 128.
            Larger batch size makes the gradient estimation more accurate, but
            means fewer updates to the model are made per pass over the data.
            With more passes over the data, the updates are less noisy, which
            can lead to inferior generalisation and longer training times.
            The batch size is expressed in number of examples, so the best
            value will depend on the number of words per example in your data.
            If your documents are long, you can use a lower batch size (because
            you're using more information to estimate the gradients). With a
            large dataset and short examples, try a batch size of 128, possibly
            setting a higher value for `steps_per_batch` if you run out of memory
            (see below). Also try a smaller batch size like 32.

    The following hyper-parameters can affect accuracy, but generalize fairly
    well and probably don't need to be tuned:

        weight_decay (float): The weight decay for the AdamW optimizer. 0.005
            is a good value.
        classifier_lr (float): The learning rate for the classifier parameters,
            which must be trained from scatch on each new problem. A value of
            0.001 is good -- it's best for the classifier to learn much faster
            than the rest of the network, which is initialised from the language
            model.
        lr_range (int): The range to vary the learning rate over during training.
            The learning rate will cycle between learning_rate / lr_range and
            learning_rate * lr_range. 2 is good.
        lr_period (int): How many epochs per min-to-max period in the cycle.
            2 is good. Definitely don't set patience < lr_period * 2 --- you
            want at least one full cycle before you give up.

    The following hyper-parameters impact compute budgets.

        patience (int): How many evaluations to allow without improvement
            before giving up. e.g. if patience is 5 and the best evaluation
            was the tenth one, the loop may halt from evaluation 15 onward.
            The loop only halts after a full epoch though, so depending on the
            evaluation frequency, more than `patience` checkpoints may occur
            after the best one. 10 is good.
        eval_every (int): How often to evaluate, in number of iterations.
            max(100, (len(train_data) // batch_size) // 10) is good -- i.e.
            either 100, or about every 10% of a full epoch. For small training
        steps_per_batch (int): Accumulate gradients over a number of steps for
            each batch. This allows you to use a higher batch size with less memory,
            at the expense of potentially slower compute costs. If you don't need
            it, just set it to 1.

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
        gradients, accumulate_gradients = start_batch_gradients()
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
            "loss": losses,
            "checkpoints": results,
        }
        yield batch, info, is_best_checkpoint
        # Stop if no improvement in `patience` checkpoints
        best_score, best_step, best_epoch = max(results)
        if ((step - best_step) // eval_frequency) >= patience:
            break


def start_batch_gradients():
    gradients = {}

    def accumulate_gradients(W, dW, key=None):
        if key in gradients:
            gradients[key][1] += dW
        else:
            gradients[key] = [W, dW]

    return gradients, accumulate_gradients


def subdivide_batch(batch):
    return [batch]
