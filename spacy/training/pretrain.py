from typing import Optional, Callable, Iterable, Union, List
from thinc.api import Config, fix_random_seed, set_gpu_allocator, Model, Optimizer
from thinc.api import set_dropout_rate, to_categorical, CosineDistance, L2Distance
from pathlib import Path
from functools import partial
from collections import Counter
import srsly
import numpy
import time
import re
from wasabi import Printer

from .example import Example
from ..tokens import Doc
from ..attrs import ID
from ..ml.models.multi_task import build_cloze_multi_task_model
from ..ml.models.multi_task import build_cloze_characters_multi_task_model
from ..schemas import ConfigSchemaTraining, ConfigSchemaPretrain
from ..errors import Errors
from ..util import registry, load_model_from_config, dot_to_object


def pretrain(
    config: Config,
    output_dir: Path,
    resume_path: Optional[Path] = None,
    epoch_resume: Optional[int] = None,
    use_gpu: int = -1,
    silent: bool = True,
):
    msg = Printer(no_print=silent)
    if config["training"]["seed"] is not None:
        fix_random_seed(config["training"]["seed"])
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    nlp = load_model_from_config(config)
    _config = nlp.config.interpolate()
    T = registry.resolve(_config["training"], schema=ConfigSchemaTraining)
    P = registry.resolve(_config["pretraining"], schema=ConfigSchemaPretrain)
    corpus = dot_to_object(T, P["corpus"])
    batcher = P["batcher"]
    model = create_pretraining_model(nlp, P)
    optimizer = P["optimizer"]
    # Load in pretrained weights to resume from
    if resume_path is not None:
        _resume_model(model, resume_path, epoch_resume, silent=silent)
    else:
        # Without '--resume-path' the '--epoch-resume' argument is ignored
        epoch_resume = 0
    # TODO: move this to logger function?
    tracker = ProgressTracker(frequency=10000)
    msg.divider(f"Pre-training tok2vec layer - starting at epoch {epoch_resume}")
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

    objective = create_objective(P["objective"])
    # TODO: I think we probably want this to look more like the
    # 'create_train_batches' function?
    for epoch in range(epoch_resume, P["max_epochs"]):
        for batch_id, batch in enumerate(batcher(corpus(nlp))):
            docs = ensure_docs(batch)
            loss = make_update(model, docs, optimizer, objective)
            progress = tracker.update(epoch, loss, docs)
            if progress:
                msg.row(progress, **row_settings)
            if P["n_save_every"] and (batch_id % P["n_save_every"] == 0):
                _save_model(epoch, is_temp=True)
        _save_model(epoch)
        tracker.epoch_loss = 0.0


def ensure_docs(examples_or_docs: Iterable[Union[Doc, Example]]) -> List[Doc]:
    docs = []
    for eg_or_doc in examples_or_docs:
        if isinstance(eg_or_doc, Doc):
            docs.append(eg_or_doc)
        else:
            docs.append(eg_or_doc.reference)
    return docs


def _resume_model(
    model: Model, resume_path: Path, epoch_resume: int, silent: bool = True
) -> None:
    msg = Printer(no_print=silent)
    msg.info(f"Resume training tok2vec from: {resume_path}")
    with resume_path.open("rb") as file_:
        weights_data = file_.read()
        model.get_ref("tok2vec").from_bytes(weights_data)
    # Parse the epoch number from the given weight file
    model_name = re.search(r"model\d+\.bin", str(resume_path))
    if model_name:
        # Default weight file name so read epoch_start from it by cutting off 'model' and '.bin'
        epoch_resume = int(model_name.group(0)[5:][:-4]) + 1
        msg.info(f"Resuming from epoch: {epoch_resume}")
    else:
        msg.info(f"Resuming from epoch: {epoch_resume}")


def make_update(
    model: Model, docs: Iterable[Doc], optimizer: Optimizer, objective_func: Callable
) -> float:
    """Perform an update over a single batch of documents.

    docs (iterable): A batch of `Doc` objects.
    optimizer (callable): An optimizer.
    RETURNS loss: A float for the loss.
    """
    predictions, backprop = model.begin_update(docs)
    loss, gradients = objective_func(model.ops, docs, predictions)
    backprop(gradients)
    model.finish_update(optimizer)
    # Don't want to return a cupy object here
    # The gradients are modified in-place by the BERT MLM,
    # so we get an accurate loss
    return float(loss)


def create_objective(config: Config):
    """Create the objective for pretraining.

    We'd like to replace this with a registry function but it's tricky because
    we're also making a model choice based on this. For now we hard-code support
    for two types (characters, vectors). For characters you can specify
    n_characters, for vectors you can specify the loss.

    Bleh.
    """
    objective_type = config["type"]
    if objective_type == "characters":
        return partial(get_characters_loss, nr_char=config["n_characters"])
    elif objective_type == "vectors":
        if config["loss"] == "cosine":
            distance = CosineDistance(normalize=True, ignore_zeros=True)
            return partial(get_vectors_loss, distance=distance)
        elif config["loss"] == "L2":
            distance = L2Distance(normalize=True, ignore_zeros=True)
            return partial(get_vectors_loss, distance=distance)
        else:
            raise ValueError(Errors.E906.format(loss_type=config["loss"]))
    else:
        raise ValueError(Errors.E907.format(objective_type=objective_type))


def get_vectors_loss(ops, docs, prediction, distance):
    """Compute a loss based on a distance between the documents' vectors and
    the prediction.
    """
    # The simplest way to implement this would be to vstack the
    # token.vector values, but that's a bit inefficient, especially on GPU.
    # Instead we fetch the index into the vectors table for each of our tokens,
    # and look them up all at once. This prevents data copying.
    ids = ops.flatten([doc.to_array(ID).ravel() for doc in docs])
    target = docs[0].vocab.vectors.data[ids]
    d_target, loss = distance(prediction, target)
    return loss, d_target


def get_characters_loss(ops, docs, prediction, nr_char):
    """Compute a loss based on a number of characters predicted from the docs."""
    target_ids = numpy.vstack([doc.to_utf8_array(nr_char=nr_char) for doc in docs])
    target_ids = target_ids.reshape((-1,))
    target = ops.asarray(to_categorical(target_ids, n_classes=256), dtype="f")
    target = target.reshape((-1, 256 * nr_char))
    diff = prediction - target
    loss = (diff ** 2).sum()
    d_target = diff / float(prediction.shape[0])
    return loss, d_target


def create_pretraining_model(nlp, pretrain_config):
    """Define a network for the pretraining. We simply add an output layer onto
    the tok2vec input model. The tok2vec input model needs to be a model that
    takes a batch of Doc objects (as a list), and returns a list of arrays.
    Each array in the output needs to have one row per token in the doc.
    The actual tok2vec layer is stored as a reference, and only this bit will be
    serialized to file and read back in when calling the 'train' command.
    """
    component = nlp.get_pipe(pretrain_config["component"])
    if pretrain_config.get("layer"):
        tok2vec = component.model.get_ref(pretrain_config["layer"])
    else:
        tok2vec = component.model

    # TODO
    maxout_pieces = 3
    hidden_size = 300
    if pretrain_config["objective"]["type"] == "vectors":
        model = build_cloze_multi_task_model(
            nlp.vocab, tok2vec, hidden_size=hidden_size, maxout_pieces=maxout_pieces
        )
    elif pretrain_config["objective"]["type"] == "characters":
        model = build_cloze_characters_multi_task_model(
            nlp.vocab,
            tok2vec,
            hidden_size=hidden_size,
            maxout_pieces=maxout_pieces,
            nr_char=pretrain_config["objective"]["n_characters"],
        )
    model.initialize(X=[nlp.make_doc("Give it a doc to infer shapes")])
    set_dropout_rate(model, pretrain_config["dropout"])
    return model


class ProgressTracker:
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


def _smart_round(
    figure: Union[float, int], width: int = 10, max_decimal: int = 4
) -> str:
    """Round large numbers as integers, smaller numbers as decimals."""
    n_digits = len(str(int(figure)))
    n_decimal = width - (n_digits + 1)
    if n_decimal <= 1:
        return str(int(figure))
    else:
        n_decimal = min(n_decimal, max_decimal)
        format_str = "%." + str(n_decimal) + "f"
        return format_str % figure
