from typing import Union, Dict, Optional, Any, List, IO, TYPE_CHECKING
from thinc.api import Config, fix_random_seed, set_gpu_allocator
from thinc.api import ConfigValidationError
from pathlib import Path
import srsly
import numpy
import tarfile
import gzip
import zipfile
import tqdm

from ..lookups import Lookups
from ..vectors import Vectors
from ..errors import Errors
from ..schemas import ConfigSchemaTraining
from ..util import registry, load_model_from_config, resolve_dot_names, logger
from ..util import load_model, ensure_path, OOV_RANK, DEFAULT_OOV_PROB

if TYPE_CHECKING:
    from ..language import Language  # noqa: F401


def init_nlp(config: Config, *, use_gpu: int = -1) -> "Language":
    raw_config = config
    config = raw_config.interpolate()
    if config["training"]["seed"] is not None:
        fix_random_seed(config["training"]["seed"])
    allocator = config["training"]["gpu_allocator"]
    if use_gpu >= 0 and allocator:
        set_gpu_allocator(allocator)
    # Use original config here before it's resolved to functions
    sourced_components = get_sourced_components(config)
    nlp = load_model_from_config(raw_config, auto_fill=True)
    logger.info("Set up nlp object from config")
    config = nlp.config.interpolate()
    # Resolve all training-relevant sections using the filled nlp config
    T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    train_corpus, dev_corpus = resolve_dot_names(config, dot_names)
    optimizer = T["optimizer"]
    # Components that shouldn't be updated during training
    frozen_components = T["frozen_components"]
    # Sourced components that require resume_training
    resume_components = [p for p in sourced_components if p not in frozen_components]
    logger.info(f"Pipeline: {nlp.pipe_names}")
    if resume_components:
        with nlp.select_pipes(enable=resume_components):
            logger.info(f"Resuming training for: {resume_components}")
            nlp.resume_training(sgd=optimizer)
    with nlp.select_pipes(disable=[*frozen_components, *resume_components]):
        nlp.initialize(lambda: train_corpus(nlp), sgd=optimizer)
        logger.info(f"Initialized pipeline components: {nlp.pipe_names}")
    return nlp


def init_vocab(
    nlp: "Language",
    *,
    data: Optional[Path] = None,
    lookups: Optional[Lookups] = None,
    vectors: Optional[str] = None,
) -> "Language":
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
    logger.info("Finished initializing nlp object")


def load_vectors_into_model(
    nlp: "Language", name: Union[str, Path], *, add_strings: bool = True
) -> None:
    """Load word vectors from an installed model or path into a model instance."""
    try:
        vectors_nlp = load_model(name)
    except ConfigValidationError as e:
        title = f"Config validation error for vectors {name}"
        desc = (
            "This typically means that there's a problem in the config.cfg included "
            "with the packaged vectors. Make sure that the vectors package you're "
            "loading is compatible with the current version of spaCy."
        )
        err = ConfigValidationError.from_error(e, config=None, title=title, desc=desc)
        raise err from None
    nlp.vocab.vectors = vectors_nlp.vocab.vectors
    if add_strings:
        # I guess we should add the strings from the vectors_nlp model?
        # E.g. if someone does a similarity query, they might expect the strings.
        for key in nlp.vocab.vectors.key2row:
            if key in vectors_nlp.vocab.strings:
                nlp.vocab.strings.add(vectors_nlp.vocab.strings[key])


def init_tok2vec(
    nlp: "Language", pretrain_config: Dict[str, Any], init_config: Dict[str, Any]
) -> bool:
    # Load pretrained tok2vec weights - cf. CLI command 'pretrain'
    P = pretrain_config
    I = init_config
    weights_data = None
    init_tok2vec = ensure_path(I["init_tok2vec"])
    if init_tok2vec is not None:
        if P["objective"].get("type") == "vectors" and not I["vectors"]:
            err = 'need initialize.vectors if pretraining.objective.type is "vectors"'
            errors = [{"loc": ["initialize"], "msg": err}]
            raise ConfigValidationError(config=nlp.config, errors=errors)
        if not init_tok2vec.exists():
            err = f"can't find pretrained tok2vec: {init_tok2vec}"
            errors = [{"loc": ["initialize", "init_tok2vec"], "msg": err}]
            raise ConfigValidationError(config=nlp.config, errors=errors)
        with init_tok2vec.open("rb") as file_:
            weights_data = file_.read()
    if weights_data is not None:
        tok2vec_component = P["component"]
        if tok2vec_component is None:
            desc = (
                f"To use pretrained tok2vec weights, [pretraining.component] "
                f"needs to specify the component that should load them."
            )
            err = "component can't be null"
            errors = [{"loc": ["pretraining", "component"], "msg": err}]
            raise ConfigValidationError(
                config=nlp.config["pretraining"], errors=errors, desc=desc
            )
        layer = nlp.get_pipe(tok2vec_component).model
        if P["layer"]:
            layer = layer.get_ref(P["layer"])
        layer.from_bytes(weights_data)
        return True
    return False


def get_sourced_components(config: Union[Dict[str, Any], Config]) -> List[str]:
    """RETURNS (List[str]): All sourced components in the original config,
    e.g. {"source": "en_core_web_sm"}. If the config contains a key
    "factory", we assume it refers to a component factory.
    """
    return [
        name
        for name, cfg in config.get("components", {}).items()
        if "factory" not in cfg and "source" in cfg
    ]


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
                nlp.vocab.vectors.add(lex.orth, row=lex.rank)
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
    f = open_file(vectors_loc)
    f = ensure_shape(f)
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
        return tarfile.open(str(loc), "r:gz")
    elif loc.parts[-1].endswith("gz"):
        return (line.decode("utf8") for line in gzip.open(str(loc), "r"))
    elif loc.parts[-1].endswith("zip"):
        zip_file = zipfile.ZipFile(str(loc))
        names = zip_file.namelist()
        file_ = zip_file.open(names[0])
        return (line.decode("utf8") for line in file_)
    else:
        return loc.open("r", encoding="utf8")


def ensure_shape(lines):
    """Ensure that the first line of the data is the vectors shape.
    If it's not, we read in the data and output the shape as the first result,
    so that the reader doesn't have to deal with the problem.
    """
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
        captured = [first_line] + list(lines)
        length = len(captured)
        yield f"{length} {width}"
        yield from captured
