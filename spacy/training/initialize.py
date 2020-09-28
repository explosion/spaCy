from typing import Union, Dict, Optional, Any, List, Callable
from thinc.api import Config, fix_random_seed, set_gpu_allocator
from thinc.api import ConfigValidationError
from pathlib import Path
import srsly

from .loop import create_before_to_disk_callback
from ..language import Language
from ..lookups import Lookups
from ..errors import Errors
from ..schemas import ConfigSchemaTraining, ConfigSchemaInit, ConfigSchemaPretrain
from ..util import registry, load_model_from_config, resolve_dot_names
from ..util import load_model, ensure_path, logger, OOV_RANK, DEFAULT_OOV_PROB


def init_nlp(
    config: Config,
    *,
    use_gpu: int = -1,
    logger: Callable[[Any], Any] = logger,
    on_success: Callable[[str], None] = lambda x: None,
) -> Language:
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
    on_success("Set up nlp object from config")
    config = nlp.config.interpolate()
    # Resolve all training-relevant sections using the filled nlp config
    T = registry.resolve(config["training"], schema=ConfigSchemaTraining)
    dot_names = [T["train_corpus"], T["dev_corpus"]]
    train_corpus, dev_corpus = resolve_dot_names(config, dot_names)
    I = registry.resolve(config["initialize"], schema=ConfigSchemaInit)
    V = I["vocab"]
    init_vocab(nlp, data=V["data"], lookups=V["lookups"], vectors=V["vectors"])
    optimizer = T["optimizer"]
    before_to_disk = create_before_to_disk_callback(T["before_to_disk"])
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
        nlp.begin_training(lambda: train_corpus(nlp), sgd=optimizer)
        on_success(f"Initialized pipeline components")
    # Verify the config after calling 'begin_training' to ensure labels
    # are properly initialized
    verify_config(nlp)
    if "pretraining" in config and config["pretraining"]:
        P = registry.resolve(config["pretraining"], schema=ConfigSchemaPretrain)
        loaded = add_tok2vec_weights(nlp, P, I)
        if loaded and P["component"]:
            on_success(f"Loaded pretrained weights into component '{P['component']}'")
    nlp = before_to_disk(nlp)
    return nlp


def must_reinitialize(train_config: Config, init_config: Config) -> bool:
    # TODO: do this better and more fine-grained
    return train_config.interpolate().to_str() == init_config.interpolate().to_str()


def init_vocab(
    nlp: Language,
    *,
    data: Optional[Path] = None,
    lookups: Optional[Lookups] = None,
    vectors: Optional[str] = None,
    on_success: Callable[[str], None] = lambda x: None,
) -> Language:
    if lookups:
        nlp.vocab.lookups = lookups
        on_success(f"Added vocab lookups: {', '.join(lookups.tables)}")
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
        on_success(f"Added {len(nlp.vocab)} lexical entries to the vocab")
    on_success("Created vocabulary")
    if vectors is not None:
        load_vectors_into_model(nlp, vectors)
        on_success(f"Added vectors: {vectors}")


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
        err = ConfigValidationError.from_error(config=None, title=title, desc=desc)
        raise err from None
    nlp.vocab.vectors = vectors_nlp.vocab.vectors
    if add_strings:
        # I guess we should add the strings from the vectors_nlp model?
        # E.g. if someone does a similarity query, they might expect the strings.
        for key in nlp.vocab.vectors.key2row:
            if key in vectors_nlp.vocab.strings:
                nlp.vocab.strings.add(vectors_nlp.vocab.strings[key])


def add_tok2vec_weights(
    nlp: Language, pretrain_config: Dict[str, Any], vocab_config: Dict[str, Any]
) -> bool:
    # Load pretrained tok2vec weights - cf. CLI command 'pretrain'
    P = pretrain_config
    V = vocab_config
    weights_data = None
    init_tok2vec = ensure_path(V["init_tok2vec"])
    if init_tok2vec is not None:
        if P["objective"].get("type") == "vectors" and not V["vectors"]:
            err = 'need initialize.vectors if pretraining.objective.type is "vectors"'
            errors = [{"loc": ["initialize", "vectors"], "msg": err}]
            raise ConfigValidationError(config=nlp.config, errors=errors)
        if not init_tok2vec.exists():
            err = f"can't find pretrained tok2vec: {init_tok2vec}"
            errors = [{"loc": ["initialize", "vectors", "init_tok2vec"], "msg": err}]
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


def verify_config(nlp: Language) -> None:
    """Perform additional checks based on the config, loaded nlp object and training data."""
    # TODO: maybe we should validate based on the actual components, the list
    # in config["nlp"]["pipeline"] instead?
    for pipe_config in nlp.config["components"].values():
        # We can't assume that the component name == the factory
        factory = pipe_config["factory"]
        if factory == "textcat":
            verify_textcat_config(nlp, pipe_config)


def verify_textcat_config(nlp: Language, pipe_config: Dict[str, Any]) -> None:
    # if 'positive_label' is provided: double check whether it's in the data and
    # the task is binary
    if pipe_config.get("positive_label"):
        textcat_labels = nlp.get_pipe("textcat").labels
        pos_label = pipe_config.get("positive_label")
        if pos_label not in textcat_labels:
            raise ValueError(
                Errors.E920.format(pos_label=pos_label, labels=textcat_labels)
            )
        if len(list(textcat_labels)) != 2:
            raise ValueError(
                Errors.E919.format(pos_label=pos_label, labels=textcat_labels)
            )


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
