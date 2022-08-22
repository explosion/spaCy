from typing import Union, Dict, Optional, Any, IO, TYPE_CHECKING
from thinc.api import Config, fix_random_seed, set_gpu_allocator
from thinc.api import ConfigValidationError
from pathlib import Path
import srsly
import numpy
import tarfile
import gzip
import zipfile
import tqdm
from itertools import islice
import warnings

from .pretrain import get_tok2vec_ref
from ..lookups import Lookups
from ..vectors import Vectors
from ..errors import Errors, Warnings
from ..schemas import ConfigSchemaTraining
from ..util import registry, load_model_from_config, resolve_dot_names, logger
from ..util import load_model, ensure_path, get_sourced_components
from ..util import OOV_RANK, DEFAULT_OOV_PROB

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


def init_nlp(config: Config, *, use_gpu: int = -1) -> "Language":
    raw_config = config
    config = raw_config.interpolate()
    if "seed" not in config["training"]:
        raise ValueError(Errors.E1015.format(value="[training] seed"))
    if "gpu_allocator" not in config["training"]:
        raise ValueError(Errors.E1015.format(value="[training] gpu_allocator"))
    if config["training"]["seed"] is not None:
        fix_random_seed(config["training"]["seed"])
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    # Use original config here before it's resolved to functions
    sourced = get_sourced_components(config)
    nlp = load_model_from_config(raw_config, auto_fill=True)
    logger.info("Set up nlp object from config")
    config = nlp.config.interpolate()
    # Resolve all training-relevant sections using the filled nlp config
    T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    if not isinstance(T["train_corpus"], str):
        raise ConfigValidationError(
            desc=Errors.E897.format(
                field="training.train_corpus", type=type(T["train_corpus"])
            )
        )
    if not isinstance(T["dev_corpus"], str):
        raise ConfigValidationError(
            desc=Errors.E897.format(
                field="training.dev_corpus", type=type(T["dev_corpus"])
            )
        )
    train_corpus, dev_corpus = resolve_dot_names(config, dot_names)
    optimizer = T["optimizer"]
    # Components that shouldn't be updated during training
    frozen_components = T["frozen_components"]
    # Sourced components that require resume_training
    resume_components = [p for p in sourced if p not in frozen_components]
    logger.info(f"Pipeline: {nlp.pipe_names}")
    if resume_components:
        with nlp.select_pipes(enable=resume_components):
            logger.info(f"Resuming training for: {resume_components}")
            nlp.resume_training(sgd=optimizer)
    # Make sure that listeners are defined before initializing further
    nlp._link_components()
    with nlp.select_pipes(disable=[*frozen_components, *resume_components]):
        if T["max_epochs"] == -1:
            sample_size = 100
            logger.debug(
                f"Due to streamed train corpus, using only first {sample_size} "
                f"examples for initialization. If necessary, provide all labels "
                f"in [initialize]. More info: https://spacy.io/api/cli#init_labels"
            )
            nlp.initialize(
                lambda: islice(train_corpus(nlp), sample_size), sgd=optimizer
            )
        else:
            nlp.initialize(lambda: train_corpus(nlp), sgd=optimizer)
        logger.info(f"Initialized pipeline components: {nlp.pipe_names}")
    # Detect components with listeners that are not frozen consistently
    for name, proc in nlp.pipeline:
        for listener in getattr(
            proc, "listening_components", []
        ):  # e.g. tok2vec/transformer
            # Don't warn about components not in the pipeline
            if listener not in nlp.pipe_names:
                continue
            if listener in frozen_components and name not in frozen_components:
                logger.warning(Warnings.W087.format(name=name, listener=listener))
            # We always check this regardless, in case user freezes tok2vec
            if listener not in frozen_components and name in frozen_components:
                if name not in T["annotating_components"]:
                    logger.warning(Warnings.W086.format(name=name, listener=listener))
    return nlp


def init_vocab(
    nlp: "Language",
    *,
    data: Optional[Path] = None,
    lookups: Optional[Lookups] = None,
    vectors: Optional[str] = None,
) -> None:
    if lookups:
        nlp.vocab.lookups = lookups
        logger.info(f"Added vocab lookups: {', '.join(lookups.tables)}")
    data_path = ensure_path(data)
    if data_path is not None:
        lex_attrs = srsly.read_jsonl(data_path)
        for lexeme in nlp.vocab:
            lexeme.rank = OOV_RANK
        for attrs in lex_attrs:
            if "settings" in attrs:
                continue
            lexeme = nlp.vocab[attrs["orth"]]
            lexeme.set_attrs(**attrs)
        if len(nlp.vocab):
            oov_prob = min(lex.prob for lex in nlp.vocab) - 1
        else:
            oov_prob = DEFAULT_OOV_PROB
        nlp.vocab.cfg.update({"oov_prob": oov_prob})
        logger.info(f"Added {len(nlp.vocab)} lexical entries to the vocab")
    logger.info("Created vocabulary")
    if vectors is not None:
        load_vectors_into_model(nlp, vectors)
        logger.info(f"Added vectors: {vectors}")
    # warn if source model vectors are not identical
    sourced_vectors_hashes = nlp.meta.pop("_sourced_vectors_hashes", {})
    vectors_hash = hash(nlp.vocab.vectors.to_bytes())
    for sourced_component, sourced_vectors_hash in sourced_vectors_hashes.items():
        if vectors_hash != sourced_vectors_hash:
            warnings.warn(Warnings.W113.format(name=sourced_component))
    logger.info("Finished initializing nlp object")


def load_vectors_into_model(
    nlp: "Language", name: Union[str, Path], *, add_strings: bool = True
) -> None:
    """Load word vectors from an installed model or path into a model instance."""
    try:
        # Load with the same vocab, which automatically adds the vectors to
        # the current nlp object. Exclude lookups so they are not modified.
        exclude = ["lookups"]
        if not add_strings:
            exclude.append("strings")
        vectors_nlp = load_model(name, vocab=nlp.vocab, exclude=exclude)
    except ConfigValidationError as e:
        title = f"Config validation error for vectors {name}"
        desc = (
            "This typically means that there's a problem in the config.cfg included "
            "with the packaged vectors. Make sure that the vectors package you're "
            "loading is compatible with the current version of spaCy."
        )
        err = ConfigValidationError.from_error(e, title=title, desc=desc)
        raise err from None

    if len(vectors_nlp.vocab.vectors.keys()) == 0:
        logger.warning(Warnings.W112.format(name=name))

    for lex in nlp.vocab:
        lex.rank = nlp.vocab.vectors.key2row.get(lex.orth, OOV_RANK)  # type: ignore[attr-defined]


def init_tok2vec(
    nlp: "Language", pretrain_config: Dict[str, Any], init_config: Dict[str, Any]
) -> bool:
    # Load pretrained tok2vec weights - cf. CLI command 'pretrain'
    P = pretrain_config
    I = init_config
    weights_data = None
    init_tok2vec = ensure_path(I["init_tok2vec"])
    if init_tok2vec is not None:
        if not init_tok2vec.exists():
            err = f"can't find pretrained tok2vec: {init_tok2vec}"
            errors = [{"loc": ["initialize", "init_tok2vec"], "msg": err}]
            raise ConfigValidationError(config=nlp.config, errors=errors)
        with init_tok2vec.open("rb") as file_:
            weights_data = file_.read()
    if weights_data is not None:
        layer = get_tok2vec_ref(nlp, P)
        layer.from_bytes(weights_data)
        logger.info(f"Loaded pretrained weights from {init_tok2vec}")
        return True
    return False


def convert_vectors(
    nlp: "Language",
    vectors_loc: Optional[Path],
    *,
    truncate: int,
    prune: int,
    name: Optional[str] = None,
) -> None:
    vectors_loc = ensure_path(vectors_loc)
    if vectors_loc and vectors_loc.parts[-1].endswith(".npz"):
        nlp.vocab.vectors = Vectors(data=numpy.load(vectors_loc.open("rb")))
        for lex in nlp.vocab:
            if lex.rank and lex.rank != OOV_RANK:
                nlp.vocab.vectors.add(lex.orth, row=lex.rank)  # type: ignore[attr-defined]
    else:
        if vectors_loc:
            logger.info(f"Reading vectors from {vectors_loc}")
            vectors_data, vector_keys = read_vectors(vectors_loc, truncate)
            logger.info(f"Loaded vectors from {vectors_loc}")
        else:
            vectors_data, vector_keys = (None, None)
        if vector_keys is not None:
            for word in vector_keys:
                if word not in nlp.vocab:
                    nlp.vocab[word]
        if vectors_data is not None:
            nlp.vocab.vectors = Vectors(data=vectors_data, keys=vector_keys)
    if name is None:
        # TODO: Is this correct? Does this matter?
        nlp.vocab.vectors.name = f"{nlp.meta['lang']}_{nlp.meta['name']}.vectors"
    else:
        nlp.vocab.vectors.name = name
    nlp.meta["vectors"]["name"] = nlp.vocab.vectors.name
    if prune >= 1:
        nlp.vocab.prune_vectors(prune)


def read_vectors(vectors_loc: Path, truncate_vectors: int):
    f = ensure_shape(vectors_loc)
    shape = tuple(int(size) for size in next(f).split())
    if truncate_vectors >= 1:
        shape = (truncate_vectors, shape[1])
    vectors_data = numpy.zeros(shape=shape, dtype="f")
    vectors_keys = []
    for i, line in enumerate(tqdm.tqdm(f)):
        line = line.rstrip()
        pieces = line.rsplit(" ", vectors_data.shape[1])
        word = pieces.pop(0)
        if len(pieces) != vectors_data.shape[1]:
            raise ValueError(Errors.E094.format(line_num=i, loc=vectors_loc))
        vectors_data[i] = numpy.asarray(pieces, dtype="f")
        vectors_keys.append(word)
        if i == truncate_vectors - 1:
            break
    return vectors_data, vectors_keys


def open_file(loc: Union[str, Path]) -> IO:
    """Handle .gz, .tar.gz or unzipped files"""
    loc = ensure_path(loc)
    if tarfile.is_tarfile(str(loc)):
        return tarfile.open(str(loc), "r:gz")  # type: ignore[return-value]
    elif loc.parts[-1].endswith("gz"):
        return (line.decode("utf8") for line in gzip.open(str(loc), "r"))  # type: ignore[return-value]
    elif loc.parts[-1].endswith("zip"):
        zip_file = zipfile.ZipFile(str(loc))
        names = zip_file.namelist()
        file_ = zip_file.open(names[0])
        return (line.decode("utf8") for line in file_)  # type: ignore[return-value]
    else:
        return loc.open("r", encoding="utf8")


def ensure_shape(vectors_loc):
    """Ensure that the first line of the data is the vectors shape.
    If it's not, we read in the data and output the shape as the first result,
    so that the reader doesn't have to deal with the problem.
    """
    lines = open_file(vectors_loc)
    first_line = next(lines)
    try:
        shape = tuple(int(size) for size in first_line.split())
    except ValueError:
        shape = None
    if shape is not None:
        # All good, give the data
        yield first_line
        yield from lines
    else:
        # Figure out the shape, make it the first value, and then give the
        # rest of the data.
        width = len(first_line.split()) - 1
        length = 1
        for _ in lines:
            length += 1
        yield f"{length} {width}"
        # Reading the lines in again from file. This to avoid having to
        # store all the results in a list in memory
        lines2 = open_file(vectors_loc)
        yield from lines2
        lines2.close()
    lines.close()
