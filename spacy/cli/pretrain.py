import random
import numpy
import time
import re
from collections import Counter
from pathlib import Path
from thinc.api import Linear, Maxout, chain, list2array, prefer_gpu
from thinc.api import CosineDistance, L2Distance
from wasabi import msg
import srsly

from ..gold import Example
from ..errors import Errors
from ..ml.models.multi_task import build_masked_language_model
from ..tokens import Doc
from ..attrs import ID, HEAD
from ..ml.models.tok2vec import build_Tok2Vec_model
from .. import util
from ..util import create_default_optimizer
from .train import _load_pretrained_tok2vec


def pretrain(
    # fmt: off
    texts_loc: ("Path to JSONL file with raw texts to learn from, with text provided as the key 'text' or tokens as the key 'tokens'", "positional", None, str),
    vectors_model: ("Name or path to spaCy model with vectors to learn from", "positional", None, str),
    output_dir: ("Directory to write models to on each epoch", "positional", None, str),
    width: ("Width of CNN layers", "option", "cw", int) = 96,
    conv_depth: ("Depth of CNN layers", "option", "cd", int) = 4,
    bilstm_depth: ("Depth of BiLSTM layers (requires PyTorch)", "option", "lstm", int) = 0,
    cnn_pieces: ("Maxout size for CNN layers. 1 for Mish", "option", "cP", int) = 3,
    sa_depth: ("Depth of self-attention layers", "option", "sa", int) = 0,
    use_chars: ("Whether to use character-based embedding", "flag", "chr", bool) = False,
    cnn_window: ("Window size for CNN layers", "option", "cW", int) = 1,
    embed_rows: ("Number of embedding rows", "option", "er", int) = 2000,
    loss_func: ("Loss function to use for the objective. Either 'L2' or 'cosine'", "option", "L", str) = "cosine",
    use_vectors: ("Whether to use the static vectors as input features", "flag", "uv") = False,
    dropout: ("Dropout rate", "option", "d", float) = 0.2,
    n_iter: ("Number of iterations to pretrain", "option", "i", int) = 1000,
    batch_size: ("Number of words per training batch", "option", "bs", int) = 3000,
    max_length: ("Max words per example. Longer examples are discarded", "option", "xw", int) = 500,
    min_length: ("Min words per example. Shorter examples are discarded", "option", "nw", int) = 5,
    seed: ("Seed for random number generators", "option", "s", int) = 0,
    n_save_every: ("Save model every X batches.", "option", "se", int) = None,
    init_tok2vec: ("Path to pretrained weights for the token-to-vector parts of the models. See 'spacy pretrain'. Experimental.", "option", "t2v", Path) = None,
    epoch_start: ("The epoch to start counting at. Only relevant when using '--init-tok2vec' and the given weight file has been renamed. Prevents unintended overwriting of existing weight files.", "option", "es", int) = None,
    # fmt: on
):
    """
    Pre-train the 'token-to-vector' (tok2vec) layer of pipeline components,
    using an approximate language-modelling objective. Specifically, we load
    pretrained vectors, and train a component like a CNN, BiLSTM, etc to predict
    vectors which match the pretrained ones. The weights are saved to a directory
    after each epoch. You can then pass a path to one of these pretrained weights
    files to the 'spacy train' command.

    This technique may be especially helpful if you have little labelled data.
    However, it's still quite experimental, so your mileage may vary.

    To load the weights back in during 'spacy train', you need to ensure
    all settings are the same between pretraining and training. The API and
    errors around this need some improvement.
    """
    config = dict(locals())
    for key in config:
        if isinstance(config[key], Path):
            config[key] = str(config[key])
    util.fix_random_seed(seed)

    has_gpu = prefer_gpu()
    if has_gpu:
        import torch

        torch.set_default_tensor_type("torch.cuda.FloatTensor")
    msg.info("Using GPU" if has_gpu else "Not using GPU")

    output_dir = Path(output_dir)
    if output_dir.exists() and [p for p in output_dir.iterdir()]:
        msg.warn(
            "Output directory is not empty",
            "It is better to use an empty directory or refer to a new output path, "
            "then the new directory will be created for you.",
        )
    if not output_dir.exists():
        output_dir.mkdir()
        msg.good(f"Created output directory: {output_dir}")
    srsly.write_json(output_dir / "config.json", config)
    msg.good("Saved settings to config.json")

    # Load texts from file or stdin
    if texts_loc != "-":  # reading from a file
        texts_loc = Path(texts_loc)
        if not texts_loc.exists():
            msg.fail("Input text file doesn't exist", texts_loc, exits=1)
        with msg.loading("Loading input texts..."):
            texts = list(srsly.read_jsonl(texts_loc))
        if not texts:
            msg.fail("Input file is empty", texts_loc, exits=1)
        msg.good("Loaded input texts")
        random.shuffle(texts)
    else:  # reading from stdin
        msg.text("Reading input text from stdin...")
        texts = srsly.read_jsonl("-")

    with msg.loading(f"Loading model '{vectors_model}'..."):
        nlp = util.load_model(vectors_model)
    msg.good(f"Loaded model '{vectors_model}'")
    pretrained_vectors = None if not use_vectors else nlp.vocab.vectors
    model = create_pretraining_model(
        nlp,
        # TODO: replace with config
        build_Tok2Vec_model(
            width,
            embed_rows,
            conv_depth=conv_depth,
            pretrained_vectors=pretrained_vectors,
            bilstm_depth=bilstm_depth,  # Requires PyTorch. Experimental.
            subword_features=not use_chars,  # Set to False for Chinese etc
            maxout_pieces=cnn_pieces,  # If set to 1, use Mish activation.
            window_size=1,
            char_embed=False,
            nM=64,
            nC=8,
        ),
    )
    # Load in pretrained weights
    if init_tok2vec is not None:
        components = _load_pretrained_tok2vec(nlp, init_tok2vec)
        msg.text(f"Loaded pretrained tok2vec for: {components}")
        # Parse the epoch number from the given weight file
        model_name = re.search(r"model\d+\.bin", str(init_tok2vec))
        if model_name:
            # Default weight file name so read epoch_start from it by cutting off 'model' and '.bin'
            epoch_start = int(model_name.group(0)[5:][:-4]) + 1
        else:
            if not epoch_start:
                msg.fail(
                    "You have to use the --epoch-start argument when using a renamed weight file for --init-tok2vec",
                    exits=True,
                )
            elif epoch_start < 0:
                msg.fail(
                    f"The argument --epoch-start has to be greater or equal to 0. {epoch_start} is invalid",
                    exits=True,
                )
    else:
        # Without '--init-tok2vec' the '--epoch-start' argument is ignored
        epoch_start = 0

    optimizer = create_default_optimizer()
    tracker = ProgressTracker(frequency=10000)
    msg.divider(f"Pre-training tok2vec layer - starting at epoch {epoch_start}")
    row_settings = {"widths": (3, 10, 10, 6, 4), "aligns": ("r", "r", "r", "r", "r")}
    msg.row(("#", "# Words", "Total Loss", "Loss", "w/s"), **row_settings)

    def _save_model(epoch, is_temp=False):
        is_temp_str = ".temp" if is_temp else ""
        with model.use_params(optimizer.averages):
            with (output_dir / f"model{epoch}{is_temp_str}.bin").open("wb") as file_:
                file_.write(model.get_ref("tok2vec").to_bytes())
            log = {
                "nr_word": tracker.nr_word,
                "loss": tracker.loss,
                "epoch_loss": tracker.epoch_loss,
                "epoch": epoch,
            }
            with (output_dir / "log.jsonl").open("a") as file_:
                file_.write(srsly.json_dumps(log) + "\n")

    skip_counter = 0
    for epoch in range(epoch_start, n_iter + epoch_start):
        for batch_id, batch in enumerate(
            util.minibatch_by_words(
                (Example(doc=text) for text in texts), size=batch_size
            )
        ):
            docs, count = make_docs(
                nlp,
                [text for (text, _) in batch],
                max_length=max_length,
                min_length=min_length,
            )
            skip_counter += count
            loss = make_update(
                model, docs, optimizer, objective=loss_func, drop=dropout
            )
            progress = tracker.update(epoch, loss, docs)
            if progress:
                msg.row(progress, **row_settings)
                if texts_loc == "-" and tracker.words_per_epoch[epoch] >= 10 ** 7:
                    break
            if n_save_every and (batch_id % n_save_every == 0):
                _save_model(epoch, is_temp=True)
        _save_model(epoch)
        tracker.epoch_loss = 0.0
        if texts_loc != "-":
            # Reshuffle the texts if texts were loaded from a file
            random.shuffle(texts)
    if skip_counter > 0:
        msg.warn(f"Skipped {skip_counter} empty values")
    msg.good("Successfully finished pretrain")


def make_update(model, docs, optimizer, drop=0.0, objective="L2"):
    """Perform an update over a single batch of documents.

    docs (iterable): A batch of `Doc` objects.
    drop (float): The dropout rate.
    optimizer (callable): An optimizer.
    RETURNS loss: A float for the loss.
    """
    predictions, backprop = model.begin_update(docs, drop=drop)
    loss, gradients = get_vectors_loss(model.ops, docs, predictions, objective)
    backprop(gradients, sgd=optimizer)
    # Don't want to return a cupy object here
    # The gradients are modified in-place by the BERT MLM,
    # so we get an accurate loss
    return float(loss)


def make_docs(nlp, batch, min_length, max_length):
    docs = []
    skip_count = 0
    for record in batch:
        if not isinstance(record, dict):
            raise TypeError(Errors.E137.format(type=type(record), line=record))
        if "tokens" in record:
            words = record["tokens"]
            if not words:
                skip_count += 1
                continue
            doc = Doc(nlp.vocab, words=words)
        elif "text" in record:
            text = record["text"]
            if not text:
                skip_count += 1
                continue
            doc = nlp.make_doc(text)
        else:
            raise ValueError(Errors.E138.format(text=record))
        if "heads" in record:
            heads = record["heads"]
            heads = numpy.asarray(heads, dtype="uint64")
            heads = heads.reshape((len(doc), 1))
            doc = doc.from_array([HEAD], heads)
        if len(doc) >= min_length and len(doc) < max_length:
            docs.append(doc)
    return docs, skip_count


def get_vectors_loss(ops, docs, prediction, objective="L2"):
    """Compute a mean-squared error loss between the documents' vectors and
    the prediction.

    Note that this is ripe for customization! We could compute the vectors
    in some other word, e.g. with an LSTM language model, or use some other
    type of objective.
    """
    # The simplest way to implement this would be to vstack the
    # token.vector values, but that's a bit inefficient, especially on GPU.
    # Instead we fetch the index into the vectors table for each of our tokens,
    # and look them up all at once. This prevents data copying.
    ids = ops.flatten([doc.to_array(ID).ravel() for doc in docs])
    target = docs[0].vocab.vectors.data[ids]
    # TODO: this code originally didn't normalize, but shouldn't normalize=True ?
    if objective == "L2":
        distance = L2Distance(normalize=False)
    elif objective == "cosine":
        distance = CosineDistance(normalize=False)
    else:
        raise ValueError(Errors.E142.format(loss_func=objective))
    d_target, loss = distance(prediction, target)
    return loss, d_target


def create_pretraining_model(nlp, tok2vec):
    """Define a network for the pretraining. We simply add an output layer onto
    the tok2vec input model. The tok2vec input model needs to be a model that
    takes a batch of Doc objects (as a list), and returns a list of arrays.
    Each array in the output needs to have one row per token in the doc.
    """
    output_size = nlp.vocab.vectors.data.shape[1]
    output_layer = chain(
        Maxout(300, pieces=3, normalize=True, dropout=0.0), Linear(output_size)
    )
    # This is annoying, but the parser etc have the flatten step after
    # the tok2vec. To load the weights in cleanly, we need to match
    # the shape of the models' components exactly. So what we cann
    # "tok2vec" has to be the same set of processes as what the components do.
    tok2vec = chain(tok2vec, list2array())
    model = chain(tok2vec, output_layer)
    model = build_masked_language_model(nlp.vocab, model)
    model.set_ref("tok2vec", tok2vec)
    model.set_ref("output_layer", output_layer)
    model.initialize(X=[nlp.make_doc("Give it a doc to infer shapes")])
    return model


class ProgressTracker(object):
    def __init__(self, frequency=1000000):
        self.loss = 0.0
        self.prev_loss = 0.0
        self.nr_word = 0
        self.words_per_epoch = Counter()
        self.frequency = frequency
        self.last_time = time.time()
        self.last_update = 0
        self.epoch_loss = 0.0

    def update(self, epoch, loss, docs):
        self.loss += loss
        self.epoch_loss += loss
        words_in_batch = sum(len(doc) for doc in docs)
        self.words_per_epoch[epoch] += words_in_batch
        self.nr_word += words_in_batch
        words_since_update = self.nr_word - self.last_update
        if words_since_update >= self.frequency:
            wps = words_since_update / (time.time() - self.last_time)
            self.last_update = self.nr_word
            self.last_time = time.time()
            loss_per_word = self.loss - self.prev_loss
            status = (
                epoch,
                self.nr_word,
                _smart_round(self.loss, width=10),
                _smart_round(loss_per_word, width=6),
                int(wps),
            )
            self.prev_loss = float(self.loss)
            return status
        else:
            return None


def _smart_round(figure, width=10, max_decimal=4):
    """Round large numbers as integers, smaller numbers as decimals."""
    n_digits = len(str(int(figure)))
    n_decimal = width - (n_digits + 1)
    if n_decimal <= 1:
        return str(int(figure))
    else:
        n_decimal = min(n_decimal, max_decimal)
        format_str = "%." + str(n_decimal) + "f"
        return format_str % figure
