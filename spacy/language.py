from typing import Optional, Any, Dict, Callable, Iterable, Union, List, Pattern
from typing import Tuple
from dataclasses import dataclass
import random
import itertools
import functools
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
import warnings
from thinc.api import Model, get_current_ops, Config, Optimizer
import srsly
import multiprocessing as mp
from itertools import chain, cycle
from timeit import default_timer as timer

from .tokens.underscore import Underscore
from .vocab import Vocab, create_vocab
from .pipe_analysis import validate_attrs, analyze_pipes, print_pipe_analysis
from .training import Example, validate_examples
from .training.initialize import init_vocab, init_tok2vec
from .scorer import Scorer
from .util import registry, SimpleFrozenList, _pipe
from .util import SimpleFrozenDict, combine_score_weights, CONFIG_SECTION_ORDER
from .lang.tokenizer_exceptions import URL_MATCH, BASE_EXCEPTIONS
from .lang.punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES
from .lang.punctuation import TOKENIZER_INFIXES
from .tokens import Doc
from .tokenizer import Tokenizer
from .errors import Errors, Warnings
from .schemas import ConfigSchema, ConfigSchemaNlp, ConfigSchemaInit
from .schemas import ConfigSchemaPretrain, validate_init_settings
from .git_info import GIT_VERSION
from . import util
from . import about
from .lookups import load_lookups


# This is the base config will all settings (training etc.)
DEFAULT_CONFIG_PATH = Path(__file__).parent / "default_config.cfg"
DEFAULT_CONFIG = util.load_config(DEFAULT_CONFIG_PATH)
# This is the base config for the [pretraining] block and currently not included
# in the main config and only added via the 'init fill-config' command
DEFAULT_CONFIG_PRETRAIN_PATH = Path(__file__).parent / "default_config_pretraining.cfg"


class BaseDefaults:
    """Language data defaults, available via Language.Defaults. Can be
    overwritten by language subclasses by defining their own subclasses of
    Language.Defaults.
    """

    config: Config = Config(section_order=CONFIG_SECTION_ORDER)
    tokenizer_exceptions: Dict[str, List[dict]] = BASE_EXCEPTIONS
    prefixes: Optional[List[Union[str, Pattern]]] = TOKENIZER_PREFIXES
    suffixes: Optional[List[Union[str, Pattern]]] = TOKENIZER_SUFFIXES
    infixes: Optional[List[Union[str, Pattern]]] = TOKENIZER_INFIXES
    token_match: Optional[Pattern] = None
    url_match: Optional[Pattern] = URL_MATCH
    syntax_iterators: Dict[str, Callable] = {}
    lex_attr_getters: Dict[int, Callable[[str], Any]] = {}
    stop_words = set()
    writing_system = {"direction": "ltr", "has_case": True, "has_letters": True}


@registry.tokenizers("spacy.Tokenizer.v1")
def create_tokenizer() -> Callable[["Language"], Tokenizer]:
    """Registered function to create a tokenizer. Returns a factory that takes
    the nlp object and returns a Tokenizer instance using the language detaults.
    """

    def tokenizer_factory(nlp: "Language") -> Tokenizer:
        prefixes = nlp.Defaults.prefixes
        suffixes = nlp.Defaults.suffixes
        infixes = nlp.Defaults.infixes
        prefix_search = util.compile_prefix_regex(prefixes).search if prefixes else None
        suffix_search = util.compile_suffix_regex(suffixes).search if suffixes else None
        infix_finditer = util.compile_infix_regex(infixes).finditer if infixes else None
        return Tokenizer(
            nlp.vocab,
            rules=nlp.Defaults.tokenizer_exceptions,
            prefix_search=prefix_search,
            suffix_search=suffix_search,
            infix_finditer=infix_finditer,
            token_match=nlp.Defaults.token_match,
            url_match=nlp.Defaults.url_match,
        )

    return tokenizer_factory


@registry.misc("spacy.LookupsDataLoader.v1")
def load_lookups_data(lang, tables):
    util.logger.debug(f"Loading lookups from spacy-lookups-data: {tables}")
    lookups = load_lookups(lang=lang, tables=tables)
    return lookups


class Language:
    """A text-processing pipeline. Usually you'll load this once per process,
    and pass the instance around your application.

    Defaults (class): Settings, data and factory methods for creating the `nlp`
        object and processing pipeline.
    lang (str): Two-letter language ID, i.e. ISO code.

    DOCS: https://nightly.spacy.io/api/language
    """

    Defaults = BaseDefaults
    lang: str = None
    default_config = DEFAULT_CONFIG

    factories = SimpleFrozenDict(error=Errors.E957)
    _factory_meta: Dict[str, "FactoryMeta"] = {}  # meta by factory

    def __init__(
        self,
        vocab: Union[Vocab, bool] = True,
        *,
        max_length: int = 10 ** 6,
        meta: Dict[str, Any] = {},
        create_tokenizer: Optional[Callable[["Language"], Callable[[str], Doc]]] = None,
        **kwargs,
    ) -> None:
        """Initialise a Language object.

        vocab (Vocab): A `Vocab` object. If `True`, a vocab is created.
        meta (dict): Custom meta data for the Language class. Is written to by
            models to add model meta data.
        max_length (int): Maximum number of characters in a single text. The
            current models may run out memory on extremely long texts, due to
            large internal allocations. You should segment these texts into
            meaningful units, e.g. paragraphs, subsections etc, before passing
            them to spaCy. Default maximum length is 1,000,000 charas (1mb). As
            a rule of thumb, if all pipeline components are enabled, spaCy's
            default models currently requires roughly 1GB of temporary memory per
            100,000 characters in one text.
        create_tokenizer (Callable): Function that takes the nlp object and
            returns a tokenizer.

        DOCS: https://nightly.spacy.io/api/language#init
        """
        # We're only calling this to import all factories provided via entry
        # points. The factory decorator applied to these functions takes care
        # of the rest.
        util.registry._entry_point_factories.get_all()

        self._config = DEFAULT_CONFIG.merge(self.default_config)
        self._meta = dict(meta)
        self._path = None
        self._optimizer = None
        # Component meta and configs are only needed on the instance
        self._pipe_meta: Dict[str, "FactoryMeta"] = {}  # meta by component
        self._pipe_configs: Dict[str, Config] = {}  # config by component

        if not isinstance(vocab, Vocab) and vocab is not True:
            raise ValueError(Errors.E918.format(vocab=vocab, vocab_type=type(Vocab)))
        if vocab is True:
            vectors_name = meta.get("vectors", {}).get("name")
            vocab = create_vocab(self.lang, self.Defaults, vectors_name=vectors_name)
        else:
            if (self.lang and vocab.lang) and (self.lang != vocab.lang):
                raise ValueError(Errors.E150.format(nlp=self.lang, vocab=vocab.lang))
        self.vocab: Vocab = vocab
        if self.lang is None:
            self.lang = self.vocab.lang
        self._components = []
        self._disabled = set()
        self.max_length = max_length
        # Create the default tokenizer from the default config
        if not create_tokenizer:
            tokenizer_cfg = {"tokenizer": self._config["nlp"]["tokenizer"]}
            create_tokenizer = registry.resolve(tokenizer_cfg)["tokenizer"]
        self.tokenizer = create_tokenizer(self)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.default_config = DEFAULT_CONFIG.merge(cls.Defaults.config)
        cls.default_config["nlp"]["lang"] = cls.lang

    @property
    def path(self):
        return self._path

    @property
    def meta(self) -> Dict[str, Any]:
        """Custom meta data of the language class. If a model is loaded, this
        includes details from the model's meta.json.

        RETURNS (Dict[str, Any]): The meta.

        DOCS: https://nightly.spacy.io/api/language#meta
        """
        spacy_version = util.get_model_version_range(about.__version__)
        if self.vocab.lang:
            self._meta.setdefault("lang", self.vocab.lang)
        else:
            self._meta.setdefault("lang", self.lang)
        self._meta.setdefault("name", "pipeline")
        self._meta.setdefault("version", "0.0.0")
        self._meta.setdefault("spacy_version", spacy_version)
        self._meta.setdefault("description", "")
        self._meta.setdefault("author", "")
        self._meta.setdefault("email", "")
        self._meta.setdefault("url", "")
        self._meta.setdefault("license", "")
        self._meta.setdefault("spacy_git_version", GIT_VERSION)
        self._meta["vectors"] = {
            "width": self.vocab.vectors_length,
            "vectors": len(self.vocab.vectors),
            "keys": self.vocab.vectors.n_keys,
            "name": self.vocab.vectors.name,
        }
        self._meta["labels"] = dict(self.pipe_labels)
        # TODO: Adding this back to prevent breaking people's code etc., but
        # we should consider removing it
        self._meta["pipeline"] = list(self.pipe_names)
        self._meta["components"] = list(self.component_names)
        self._meta["disabled"] = list(self.disabled)
        return self._meta

    @meta.setter
    def meta(self, value: Dict[str, Any]) -> None:
        self._meta = value

    @property
    def config(self) -> Config:
        """Trainable config for the current language instance. Includes the
        current pipeline components, as well as default training config.

        RETURNS (thinc.api.Config): The config.

        DOCS: https://nightly.spacy.io/api/language#config
        """
        self._config.setdefault("nlp", {})
        self._config.setdefault("training", {})
        self._config["nlp"]["lang"] = self.lang
        # We're storing the filled config for each pipeline component and so
        # we can populate the config again later
        pipeline = {}
        score_weights = []
        for pipe_name in self.component_names:
            pipe_meta = self.get_pipe_meta(pipe_name)
            pipe_config = self.get_pipe_config(pipe_name)
            pipeline[pipe_name] = {"factory": pipe_meta.factory, **pipe_config}
            if pipe_meta.default_score_weights:
                score_weights.append(pipe_meta.default_score_weights)
        self._config["nlp"]["pipeline"] = list(self.component_names)
        self._config["nlp"]["disabled"] = list(self.disabled)
        self._config["components"] = pipeline
        # We're merging the existing score weights back into the combined
        # weights to make sure we're preserving custom settings in the config
        # but also reflect updates (e.g. new components added)
        prev_weights = self._config["training"].get("score_weights", {})
        combined_score_weights = combine_score_weights(score_weights, prev_weights)
        self._config["training"]["score_weights"] = combined_score_weights
        if not srsly.is_json_serializable(self._config):
            raise ValueError(Errors.E961.format(config=self._config))
        return self._config

    @config.setter
    def config(self, value: Config) -> None:
        self._config = value

    @property
    def disabled(self) -> List[str]:
        """Get the names of all disabled components.

        RETURNS (List[str]): The disabled components.
        """
        # Make sure the disabled components are returned in the order they
        # appear in the pipeline (which isn't guaranteed by the set)
        names = [name for name, _ in self._components if name in self._disabled]
        return SimpleFrozenList(names, error=Errors.E926.format(attr="disabled"))

    @property
    def factory_names(self) -> List[str]:
        """Get names of all available factories.

        RETURNS (List[str]): The factory names.
        """
        names = list(self.factories.keys())
        return SimpleFrozenList(names)

    @property
    def components(self) -> List[Tuple[str, Callable[[Doc], Doc]]]:
        """Get all (name, component) tuples in the pipeline, including the
        currently disabled components.
        """
        return SimpleFrozenList(
            self._components, error=Errors.E926.format(attr="components")
        )

    @property
    def component_names(self) -> List[str]:
        """Get the names of the available pipeline components. Includes all
        active and inactive pipeline components.

        RETURNS (List[str]): List of component name strings, in order.
        """
        names = [pipe_name for pipe_name, _ in self._components]
        return SimpleFrozenList(names, error=Errors.E926.format(attr="component_names"))

    @property
    def pipeline(self) -> List[Tuple[str, Callable[[Doc], Doc]]]:
        """The processing pipeline consisting of (name, component) tuples. The
        components are called on the Doc in order as it passes through the
        pipeline.

        RETURNS (List[Tuple[str, Callable[[Doc], Doc]]]): The pipeline.
        """
        pipes = [(n, p) for n, p in self._components if n not in self._disabled]
        return SimpleFrozenList(pipes, error=Errors.E926.format(attr="pipeline"))

    @property
    def pipe_names(self) -> List[str]:
        """Get names of available active pipeline components.

        RETURNS (List[str]): List of component name strings, in order.
        """
        names = [pipe_name for pipe_name, _ in self.pipeline]
        return SimpleFrozenList(names, error=Errors.E926.format(attr="pipe_names"))

    @property
    def pipe_factories(self) -> Dict[str, str]:
        """Get the component factories for the available pipeline components.

        RETURNS (Dict[str, str]): Factory names, keyed by component names.
        """
        factories = {}
        for pipe_name, pipe in self._components:
            factories[pipe_name] = self.get_pipe_meta(pipe_name).factory
        return SimpleFrozenDict(factories)

    @property
    def pipe_labels(self) -> Dict[str, List[str]]:
        """Get the labels set by the pipeline components, if available (if
        the component exposes a labels property).

        RETURNS (Dict[str, List[str]]): Labels keyed by component name.
        """
        labels = {}
        for name, pipe in self._components:
            if hasattr(pipe, "labels"):
                labels[name] = list(pipe.labels)
        return SimpleFrozenDict(labels)

    @classmethod
    def has_factory(cls, name: str) -> bool:
        """RETURNS (bool): Whether a factory of that name is registered."""
        internal_name = cls.get_factory_name(name)
        return name in registry.factories or internal_name in registry.factories

    @classmethod
    def get_factory_name(cls, name: str) -> str:
        """Get the internal factory name based on the language subclass.

        name (str): The factory name.
        RETURNS (str): The internal factory name.
        """
        if cls.lang is None:
            return name
        return f"{cls.lang}.{name}"

    @classmethod
    def get_factory_meta(cls, name: str) -> "FactoryMeta":
        """Get the meta information for a given factory name.

        name (str): The component factory name.
        RETURNS (FactoryMeta): The meta for the given factory name.
        """
        internal_name = cls.get_factory_name(name)
        if internal_name in cls._factory_meta:
            return cls._factory_meta[internal_name]
        if name in cls._factory_meta:
            return cls._factory_meta[name]
        raise ValueError(Errors.E967.format(meta="factory", name=name))

    @classmethod
    def set_factory_meta(cls, name: str, value: "FactoryMeta") -> None:
        """Set the meta information for a given factory name.

        name (str): The component factory name.
        value (FactoryMeta): The meta to set.
        """
        cls._factory_meta[cls.get_factory_name(name)] = value

    def get_pipe_meta(self, name: str) -> "FactoryMeta":
        """Get the meta information for a given component name.

        name (str): The component name.
        RETURNS (FactoryMeta): The meta for the given component name.
        """
        if name not in self._pipe_meta:
            raise ValueError(Errors.E967.format(meta="component", name=name))
        return self._pipe_meta[name]

    def get_pipe_config(self, name: str) -> Config:
        """Get the config used to create a pipeline component.

        name (str): The component name.
        RETURNS (Config): The config used to create the pipeline component.
        """
        if name not in self._pipe_configs:
            raise ValueError(Errors.E960.format(name=name))
        pipe_config = self._pipe_configs[name]
        return pipe_config

    @classmethod
    def factory(
        cls,
        name: str,
        *,
        default_config: Dict[str, Any] = SimpleFrozenDict(),
        assigns: Iterable[str] = SimpleFrozenList(),
        requires: Iterable[str] = SimpleFrozenList(),
        retokenizes: bool = False,
        default_score_weights: Dict[str, float] = SimpleFrozenDict(),
        func: Optional[Callable] = None,
    ) -> Callable:
        """Register a new pipeline component factory. Can be used as a decorator
        on a function or classmethod, or called as a function with the factory
        provided as the func keyword argument. To create a component and add
        it to the pipeline, you can use nlp.add_pipe(name).

        name (str): The name of the component factory.
        default_config (Dict[str, Any]): Default configuration, describing the
            default values of the factory arguments.
        assigns (Iterable[str]): Doc/Token attributes assigned by this component,
            e.g. "token.ent_id". Used for pipeline analyis.
        requires (Iterable[str]): Doc/Token attributes required by this component,
            e.g. "token.ent_id". Used for pipeline analyis.
        retokenizes (bool): Whether the component changes the tokenization.
            Used for pipeline analysis.
        default_score_weights (Dict[str, float]): The scores to report during
            training, and their default weight towards the final score used to
            select the best model. Weights should sum to 1.0 per component and
            will be combined and normalized for the whole pipeline. If None,
            the score won't be shown in the logs or be weighted.
        func (Optional[Callable]): Factory function if not used as a decorator.

        DOCS: https://nightly.spacy.io/api/language#factory
        """
        if not isinstance(name, str):
            raise ValueError(Errors.E963.format(decorator="factory"))
        if not isinstance(default_config, dict):
            err = Errors.E962.format(
                style="default config", name=name, cfg_type=type(default_config)
            )
            raise ValueError(err)

        def add_factory(factory_func: Callable) -> Callable:
            internal_name = cls.get_factory_name(name)
            if internal_name in registry.factories:
                # We only check for the internal name here – it's okay if it's a
                # subclass and the base class has a factory of the same name. We
                # also only raise if the function is different to prevent raising
                # if module is reloaded.
                existing_func = registry.factories.get(internal_name)
                if not util.is_same_func(factory_func, existing_func):
                    err = Errors.E004.format(
                        name=name, func=existing_func, new_func=factory_func
                    )
                    raise ValueError(err)

            arg_names = util.get_arg_names(factory_func)
            if "nlp" not in arg_names or "name" not in arg_names:
                raise ValueError(Errors.E964.format(name=name))
            # Officially register the factory so we can later call
            # registry.resolve and refer to it in the config as
            # @factories = "spacy.Language.xyz". We use the class name here so
            # different classes can have different factories.
            registry.factories.register(internal_name, func=factory_func)
            factory_meta = FactoryMeta(
                factory=name,
                default_config=default_config,
                assigns=validate_attrs(assigns),
                requires=validate_attrs(requires),
                scores=list(default_score_weights.keys()),
                default_score_weights=default_score_weights,
                retokenizes=retokenizes,
            )
            cls.set_factory_meta(name, factory_meta)
            # We're overwriting the class attr with a frozen dict to handle
            # backwards-compat (writing to Language.factories directly). This
            # wouldn't work with an instance property and just produce a
            # confusing error – here we can show a custom error
            cls.factories = SimpleFrozenDict(
                registry.factories.get_all(), error=Errors.E957
            )
            return factory_func

        if func is not None:  # Support non-decorator use cases
            return add_factory(func)
        return add_factory

    @classmethod
    def component(
        cls,
        name: Optional[str] = None,
        *,
        assigns: Iterable[str] = SimpleFrozenList(),
        requires: Iterable[str] = SimpleFrozenList(),
        retokenizes: bool = False,
        func: Optional[Callable[[Doc], Doc]] = None,
    ) -> Callable:
        """Register a new pipeline component. Can be used for stateless function
        components that don't require a separate factory. Can be used as a
        decorator on a function or classmethod, or called as a function with the
        factory provided as the func keyword argument. To create a component and
        add it to the pipeline, you can use nlp.add_pipe(name).

        name (str): The name of the component factory.
        assigns (Iterable[str]): Doc/Token attributes assigned by this component,
            e.g. "token.ent_id". Used for pipeline analyis.
        requires (Iterable[str]): Doc/Token attributes required by this component,
            e.g. "token.ent_id". Used for pipeline analyis.
        retokenizes (bool): Whether the component changes the tokenization.
            Used for pipeline analysis.
        func (Optional[Callable]): Factory function if not used as a decorator.

        DOCS: https://nightly.spacy.io/api/language#component
        """
        if name is not None and not isinstance(name, str):
            raise ValueError(Errors.E963.format(decorator="component"))
        component_name = name if name is not None else util.get_object_name(func)

        def add_component(component_func: Callable[[Doc], Doc]) -> Callable:
            if isinstance(func, type):  # function is a class
                raise ValueError(Errors.E965.format(name=component_name))

            def factory_func(nlp: cls, name: str) -> Callable[[Doc], Doc]:
                return component_func

            internal_name = cls.get_factory_name(name)
            if internal_name in registry.factories:
                # We only check for the internal name here – it's okay if it's a
                # subclass and the base class has a factory of the same name. We
                # also only raise if the function is different to prevent raising
                # if module is reloaded. It's hacky, but we need to check the
                # existing functure for a closure and whether that's identical
                # to the component function (because factory_func created above
                # will always be different, even for the same function)
                existing_func = registry.factories.get(internal_name)
                closure = existing_func.__closure__
                wrapped = [c.cell_contents for c in closure][0] if closure else None
                if util.is_same_func(wrapped, component_func):
                    factory_func = existing_func  # noqa: F811

            cls.factory(
                component_name,
                assigns=assigns,
                requires=requires,
                retokenizes=retokenizes,
                func=factory_func,
            )
            return component_func

        if func is not None:  # Support non-decorator use cases
            return add_component(func)
        return add_component

    def analyze_pipes(
        self,
        *,
        keys: List[str] = ["assigns", "requires", "scores", "retokenizes"],
        pretty: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Analyze the current pipeline components, print a summary of what
        they assign or require and check that all requirements are met.

        keys (List[str]): The meta values to display in the table. Corresponds
            to values in FactoryMeta, defined by @Language.factory decorator.
        pretty (bool): Pretty-print the results.
        RETURNS (dict): The data.
        """
        analysis = analyze_pipes(self, keys=keys)
        if pretty:
            print_pipe_analysis(analysis, keys=keys)
        return analysis

    def get_pipe(self, name: str) -> Callable[[Doc], Doc]:
        """Get a pipeline component for a given component name.

        name (str): Name of pipeline component to get.
        RETURNS (callable): The pipeline component.

        DOCS: https://nightly.spacy.io/api/language#get_pipe
        """
        for pipe_name, component in self._components:
            if pipe_name == name:
                return component
        raise KeyError(Errors.E001.format(name=name, opts=self.component_names))

    def create_pipe(
        self,
        factory_name: str,
        name: Optional[str] = None,
        *,
        config: Optional[Dict[str, Any]] = SimpleFrozenDict(),
        raw_config: Optional[Config] = None,
        validate: bool = True,
    ) -> Callable[[Doc], Doc]:
        """Create a pipeline component. Mostly used internally. To create and
        add a component to the pipeline, you can use nlp.add_pipe.

        factory_name (str): Name of component factory.
        name (Optional[str]): Optional name to assign to component instance.
            Defaults to factory name if not set.
        config (Optional[Dict[str, Any]]): Config parameters to use for this
            component. Will be merged with default config, if available.
        raw_config (Optional[Config]): Internals: the non-interpolated config.
        validate (bool): Whether to validate the component config against the
            arguments and types expected by the factory.
        RETURNS (Callable[[Doc], Doc]): The pipeline component.

        DOCS: https://nightly.spacy.io/api/language#create_pipe
        """
        name = name if name is not None else factory_name
        if not isinstance(config, dict):
            err = Errors.E962.format(style="config", name=name, cfg_type=type(config))
            raise ValueError(err)
        if not srsly.is_json_serializable(config):
            raise ValueError(Errors.E961.format(config=config))
        if not self.has_factory(factory_name):
            err = Errors.E002.format(
                name=factory_name,
                opts=", ".join(self.factory_names),
                method="create_pipe",
                lang=util.get_object_name(self),
                lang_code=self.lang,
            )
            raise ValueError(err)
        pipe_meta = self.get_factory_meta(factory_name)
        config = config or {}
        # This is unideal, but the alternative would mean you always need to
        # specify the full config settings, which is not really viable.
        if pipe_meta.default_config:
            config = Config(pipe_meta.default_config).merge(config)
        # We need to create a top-level key because Thinc doesn't allow resolving
        # top-level references to registered functions. Also gives nicer errors.
        # The name allows components to know their pipe name and use it in the
        # losses etc. (even if multiple instances of the same factory are used)
        internal_name = self.get_factory_name(factory_name)
        # If the language-specific factory doesn't exist, try again with the
        # not-specific name
        if internal_name not in registry.factories:
            internal_name = factory_name
        config = {"nlp": self, "name": name, **config, "@factories": internal_name}
        cfg = {factory_name: config}
        # We're calling the internal _fill here to avoid constructing the
        # registered functions twice
        resolved = registry.resolve(cfg, validate=validate)
        filled = registry.fill({"cfg": cfg[factory_name]}, validate=validate)["cfg"]
        filled = Config(filled)
        filled["factory"] = factory_name
        filled.pop("@factories", None)
        # Remove the extra values we added because we don't want to keep passing
        # them around, copying them etc.
        filled.pop("nlp", None)
        filled.pop("name", None)
        # Merge the final filled config with the raw config (including non-
        # interpolated variables)
        if raw_config:
            filled = filled.merge(raw_config)
        self._pipe_configs[name] = filled
        return resolved[factory_name]

    def create_pipe_from_source(
        self, source_name: str, source: "Language", *, name: str
    ) -> Tuple[Callable[[Doc], Doc], str]:
        """Create a pipeline component by copying it from an existing model.

        source_name (str): Name of the component in the source pipeline.
        source (Language): The source nlp object to copy from.
        name (str): Optional alternative name to use in current pipeline.
        RETURNS (Tuple[Callable, str]): The component and its factory name.
        """
        # TODO: handle errors and mismatches (vectors etc.)
        if not isinstance(source, self.__class__):
            raise ValueError(Errors.E945.format(name=source_name, source=type(source)))
        if not source.has_pipe(source_name):
            raise KeyError(
                Errors.E944.format(
                    name=source_name,
                    model=f"{source.meta['lang']}_{source.meta['name']}",
                    opts=", ".join(source.pipe_names),
                )
            )
        pipe = source.get_pipe(source_name)
        # Make sure the source config is interpolated so we don't end up with
        # orphaned variables in our final config
        source_config = source.config.interpolate()
        pipe_config = util.copy_config(source_config["components"][source_name])
        self._pipe_configs[name] = pipe_config
        return pipe, pipe_config["factory"]

    def add_pipe(
        self,
        factory_name: str,
        name: Optional[str] = None,
        *,
        before: Optional[Union[str, int]] = None,
        after: Optional[Union[str, int]] = None,
        first: Optional[bool] = None,
        last: Optional[bool] = None,
        source: Optional["Language"] = None,
        config: Optional[Dict[str, Any]] = SimpleFrozenDict(),
        raw_config: Optional[Config] = None,
        validate: bool = True,
    ) -> Callable[[Doc], Doc]:
        """Add a component to the processing pipeline. Valid components are
        callables that take a `Doc` object, modify it and return it. Only one
        of before/after/first/last can be set. Default behaviour is "last".

        factory_name (str): Name of the component factory.
        name (str): Name of pipeline component. Overwrites existing
            component.name attribute if available. If no name is set and
            the component exposes no name attribute, component.__name__ is
            used. An error is raised if a name already exists in the pipeline.
        before (Union[str, int]): Name or index of the component to insert new
            component directly before.
        after (Union[str, int]): Name or index of the component to insert new
            component directly after.
        first (bool): If True, insert component first in the pipeline.
        last (bool): If True, insert component last in the pipeline.
        source (Language): Optional loaded nlp object to copy the pipeline
            component from.
        config (Optional[Dict[str, Any]]): Config parameters to use for this
            component. Will be merged with default config, if available.
        raw_config (Optional[Config]): Internals: the non-interpolated config.
        validate (bool): Whether to validate the component config against the
            arguments and types expected by the factory.
        RETURNS (Callable[[Doc], Doc]): The pipeline component.

        DOCS: https://nightly.spacy.io/api/language#add_pipe
        """
        if not isinstance(factory_name, str):
            bad_val = repr(factory_name)
            err = Errors.E966.format(component=bad_val, name=name)
            raise ValueError(err)
        name = name if name is not None else factory_name
        if name in self.component_names:
            raise ValueError(Errors.E007.format(name=name, opts=self.component_names))
        if source is not None:
            # We're loading the component from a model. After loading the
            # component, we know its real factory name
            pipe_component, factory_name = self.create_pipe_from_source(
                factory_name, source, name=name
            )
        else:
            if not self.has_factory(factory_name):
                err = Errors.E002.format(
                    name=factory_name,
                    opts=", ".join(self.factory_names),
                    method="add_pipe",
                    lang=util.get_object_name(self),
                    lang_code=self.lang,
                )
            pipe_component = self.create_pipe(
                factory_name,
                name=name,
                config=config,
                raw_config=raw_config,
                validate=validate,
            )
        pipe_index = self._get_pipe_index(before, after, first, last)
        self._pipe_meta[name] = self.get_factory_meta(factory_name)
        self._components.insert(pipe_index, (name, pipe_component))
        return pipe_component

    def _get_pipe_index(
        self,
        before: Optional[Union[str, int]] = None,
        after: Optional[Union[str, int]] = None,
        first: Optional[bool] = None,
        last: Optional[bool] = None,
    ) -> int:
        """Determine where to insert a pipeline component based on the before/
        after/first/last values.

        before (str): Name or index of the component to insert directly before.
        after (str): Name or index of component to insert directly after.
        first (bool): If True, insert component first in the pipeline.
        last (bool): If True, insert component last in the pipeline.
        RETURNS (int): The index of the new pipeline component.
        """
        all_args = {"before": before, "after": after, "first": first, "last": last}
        if sum(arg is not None for arg in [before, after, first, last]) >= 2:
            raise ValueError(
                Errors.E006.format(args=all_args, opts=self.component_names)
            )
        if last or not any(value is not None for value in [first, before, after]):
            return len(self._components)
        elif first:
            return 0
        elif isinstance(before, str):
            if before not in self.component_names:
                raise ValueError(
                    Errors.E001.format(name=before, opts=self.component_names)
                )
            return self.component_names.index(before)
        elif isinstance(after, str):
            if after not in self.component_names:
                raise ValueError(
                    Errors.E001.format(name=after, opts=self.component_names)
                )
            return self.component_names.index(after) + 1
        # We're only accepting indices referring to components that exist
        # (can't just do isinstance here because bools are instance of int, too)
        elif type(before) == int:
            if before >= len(self._components) or before < 0:
                err = Errors.E959.format(
                    dir="before", idx=before, opts=self.component_names
                )
                raise ValueError(err)
            return before
        elif type(after) == int:
            if after >= len(self._components) or after < 0:
                err = Errors.E959.format(
                    dir="after", idx=after, opts=self.component_names
                )
                raise ValueError(err)
            return after + 1
        raise ValueError(Errors.E006.format(args=all_args, opts=self.component_names))

    def has_pipe(self, name: str) -> bool:
        """Check if a component name is present in the pipeline. Equivalent to
        `name in nlp.pipe_names`.

        name (str): Name of the component.
        RETURNS (bool): Whether a component of the name exists in the pipeline.

        DOCS: https://nightly.spacy.io/api/language#has_pipe
        """
        return name in self.pipe_names

    def replace_pipe(
        self,
        name: str,
        factory_name: str,
        *,
        config: Dict[str, Any] = SimpleFrozenDict(),
        validate: bool = True,
    ) -> Callable[[Doc], Doc]:
        """Replace a component in the pipeline.

        name (str): Name of the component to replace.
        factory_name (str): Factory name of replacement component.
        config (Optional[Dict[str, Any]]): Config parameters to use for this
            component. Will be merged with default config, if available.
        validate (bool): Whether to validate the component config against the
            arguments and types expected by the factory.
        RETURNS (Callable[[Doc], Doc]): The new pipeline component.

        DOCS: https://nightly.spacy.io/api/language#replace_pipe
        """
        if name not in self.pipe_names:
            raise ValueError(Errors.E001.format(name=name, opts=self.pipe_names))
        if hasattr(factory_name, "__call__"):
            err = Errors.E968.format(component=repr(factory_name), name=name)
            raise ValueError(err)
        # We need to delegate to Language.add_pipe here instead of just writing
        # to Language.pipeline to make sure the configs are handled correctly
        pipe_index = self.pipe_names.index(name)
        self.remove_pipe(name)
        if not len(self._components) or pipe_index == len(self._components):
            # we have no components to insert before/after, or we're replacing the last component
            return self.add_pipe(
                factory_name, name=name, config=config, validate=validate
            )
        else:
            return self.add_pipe(
                factory_name,
                name=name,
                before=pipe_index,
                config=config,
                validate=validate,
            )

    def rename_pipe(self, old_name: str, new_name: str) -> None:
        """Rename a pipeline component.

        old_name (str): Name of the component to rename.
        new_name (str): New name of the component.

        DOCS: https://nightly.spacy.io/api/language#rename_pipe
        """
        if old_name not in self.component_names:
            raise ValueError(
                Errors.E001.format(name=old_name, opts=self.component_names)
            )
        if new_name in self.component_names:
            raise ValueError(
                Errors.E007.format(name=new_name, opts=self.component_names)
            )
        i = self.component_names.index(old_name)
        self._components[i] = (new_name, self._components[i][1])
        self._pipe_meta[new_name] = self._pipe_meta.pop(old_name)
        self._pipe_configs[new_name] = self._pipe_configs.pop(old_name)
        # Make sure [initialize] config is adjusted
        if old_name in self._config["initialize"]["components"]:
            init_cfg = self._config["initialize"]["components"].pop(old_name)
            self._config["initialize"]["components"][new_name] = init_cfg

    def remove_pipe(self, name: str) -> Tuple[str, Callable[[Doc], Doc]]:
        """Remove a component from the pipeline.

        name (str): Name of the component to remove.
        RETURNS (tuple): A `(name, component)` tuple of the removed component.

        DOCS: https://nightly.spacy.io/api/language#remove_pipe
        """
        if name not in self.component_names:
            raise ValueError(Errors.E001.format(name=name, opts=self.component_names))
        removed = self._components.pop(self.component_names.index(name))
        # We're only removing the component itself from the metas/configs here
        # because factory may be used for something else
        self._pipe_meta.pop(name)
        self._pipe_configs.pop(name)
        # Make sure name is removed from the [initialize] config
        if name in self._config["initialize"]["components"]:
            self._config["initialize"]["components"].pop(name)
        # Make sure the name is also removed from the set of disabled components
        if name in self.disabled:
            self._disabled.remove(name)
        return removed

    def disable_pipe(self, name: str) -> None:
        """Disable a pipeline component. The component will still exist on
        the nlp object, but it won't be run as part of the pipeline. Does
        nothing if the component is already disabled.

        name (str): The name of the component to disable.
        """
        if name not in self.component_names:
            raise ValueError(Errors.E001.format(name=name, opts=self.component_names))
        self._disabled.add(name)

    def enable_pipe(self, name: str) -> None:
        """Enable a previously disabled pipeline component so it's run as part
        of the pipeline. Does nothing if the component is already enabled.

        name (str): The name of the component to enable.
        """
        if name not in self.component_names:
            raise ValueError(Errors.E001.format(name=name, opts=self.component_names))
        if name in self.disabled:
            self._disabled.remove(name)

    def __call__(
        self,
        text: str,
        *,
        disable: Iterable[str] = SimpleFrozenList(),
        component_cfg: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Doc:
        """Apply the pipeline to some text. The text can span multiple sentences,
        and can contain arbitrary whitespace. Alignment into the original string
        is preserved.

        text (str): The text to be processed.
        disable (list): Names of the pipeline components to disable.
        component_cfg (Dict[str, dict]): An optional dictionary with extra
            keyword arguments for specific components.
        RETURNS (Doc): A container for accessing the annotations.

        DOCS: https://nightly.spacy.io/api/language#call
        """
        if len(text) > self.max_length:
            raise ValueError(
                Errors.E088.format(length=len(text), max_length=self.max_length)
            )
        doc = self.make_doc(text)
        if component_cfg is None:
            component_cfg = {}
        for name, proc in self.pipeline:
            if name in disable:
                continue
            if not hasattr(proc, "__call__"):
                raise ValueError(Errors.E003.format(component=type(proc), name=name))
            try:
                doc = proc(doc, **component_cfg.get(name, {}))
            except KeyError as e:
                # This typically happens if a component is not initialized
                raise ValueError(Errors.E109.format(name=name)) from e
            if doc is None:
                raise ValueError(Errors.E005.format(name=name))
        return doc

    def disable_pipes(self, *names) -> "DisabledPipes":
        """Disable one or more pipeline components. If used as a context
        manager, the pipeline will be restored to the initial state at the end
        of the block. Otherwise, a DisabledPipes object is returned, that has
        a `.restore()` method you can use to undo your changes.

        This method has been deprecated since 3.0
        """
        warnings.warn(Warnings.W096, DeprecationWarning)
        if len(names) == 1 and isinstance(names[0], (list, tuple)):
            names = names[0]  # support list of names instead of spread
        return self.select_pipes(disable=names)

    def select_pipes(
        self,
        *,
        disable: Optional[Union[str, Iterable[str]]] = None,
        enable: Optional[Union[str, Iterable[str]]] = None,
    ) -> "DisabledPipes":
        """Disable one or more pipeline components. If used as a context
        manager, the pipeline will be restored to the initial state at the end
        of the block. Otherwise, a DisabledPipes object is returned, that has
        a `.restore()` method you can use to undo your changes.

        disable (str or iterable): The name(s) of the pipes to disable
        enable (str or iterable): The name(s) of the pipes to enable - all others will be disabled

        DOCS: https://nightly.spacy.io/api/language#select_pipes
        """
        if enable is None and disable is None:
            raise ValueError(Errors.E991)
        if disable is not None and isinstance(disable, str):
            disable = [disable]
        if enable is not None:
            if isinstance(enable, str):
                enable = [enable]
            to_disable = [pipe for pipe in self.pipe_names if pipe not in enable]
            # raise an error if the enable and disable keywords are not consistent
            if disable is not None and disable != to_disable:
                raise ValueError(
                    Errors.E992.format(
                        enable=enable, disable=disable, names=self.pipe_names
                    )
                )
            disable = to_disable
        # DisabledPipes will restore the pipes in 'disable' when it's done, so we need to exclude
        # those pipes that were already disabled.
        disable = [d for d in disable if d not in self._disabled]
        return DisabledPipes(self, disable)

    def make_doc(self, text: str) -> Doc:
        """Turn a text into a Doc object.

        text (str): The text to process.
        RETURNS (Doc): The processed doc.
        """
        return self.tokenizer(text)

    def update(
        self,
        examples: Iterable[Example],
        _: Optional[Any] = None,
        *,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
        component_cfg: Optional[Dict[str, Dict[str, Any]]] = None,
        exclude: Iterable[str] = SimpleFrozenList(),
    ):
        """Update the models in the pipeline.

        examples (Iterable[Example]): A batch of examples
        _: Should not be set - serves to catch backwards-incompatible scripts.
        drop (float): The dropout rate.
        sgd (Optimizer): An optimizer.
        losses (Dict[str, float]): Dictionary to update with the loss, keyed by component.
        component_cfg (Dict[str, Dict]): Config parameters for specific pipeline
            components, keyed by component name.
        exclude (Iterable[str]): Names of components that shouldn't be updated.
        RETURNS (Dict[str, float]): The updated losses dictionary

        DOCS: https://nightly.spacy.io/api/language#update
        """
        if _ is not None:
            raise ValueError(Errors.E989)
        if losses is None:
            losses = {}
        if len(examples) == 0:
            return losses
        validate_examples(examples, "Language.update")
        if sgd is None:
            if self._optimizer is None:
                self._optimizer = self.create_optimizer()
            sgd = self._optimizer
        if component_cfg is None:
            component_cfg = {}
        for i, (name, proc) in enumerate(self.pipeline):
            component_cfg.setdefault(name, {})
            component_cfg[name].setdefault("drop", drop)
            component_cfg[name].setdefault("set_annotations", False)
        for name, proc in self.pipeline:
            if name in exclude or not hasattr(proc, "update"):
                continue
            proc.update(examples, sgd=None, losses=losses, **component_cfg[name])
        if sgd not in (None, False):
            for name, proc in self.pipeline:
                if (
                    name not in exclude
                    and hasattr(proc, "is_trainable")
                    and proc.is_trainable
                    and proc.model not in (True, False, None)
                ):
                    proc.finish_update(sgd)
        return losses

    def rehearse(
        self,
        examples: Iterable[Example],
        *,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
        component_cfg: Optional[Dict[str, Dict[str, Any]]] = None,
        exclude: Iterable[str] = SimpleFrozenList(),
    ) -> Dict[str, float]:
        """Make a "rehearsal" update to the models in the pipeline, to prevent
        forgetting. Rehearsal updates run an initial copy of the model over some
        data, and update the model so its current predictions are more like the
        initial ones. This is useful for keeping a pretrained model on-track,
        even if you're updating it with a smaller set of examples.

        examples (Iterable[Example]): A batch of `Example` objects.
        sgd (Optional[Optimizer]): An optimizer.
        component_cfg (Dict[str, Dict]): Config parameters for specific pipeline
            components, keyed by component name.
        exclude (Iterable[str]): Names of components that shouldn't be updated.
        RETURNS (dict): Results from the update.

        EXAMPLE:
            >>> raw_text_batches = minibatch(raw_texts)
            >>> for labelled_batch in minibatch(examples):
            >>>     nlp.update(labelled_batch)
            >>>     raw_batch = [Example.from_dict(nlp.make_doc(text), {}) for text in next(raw_text_batches)]
            >>>     nlp.rehearse(raw_batch)

        DOCS: https://nightly.spacy.io/api/language#rehearse
        """
        if len(examples) == 0:
            return
        validate_examples(examples, "Language.rehearse")
        if sgd is None:
            if self._optimizer is None:
                self._optimizer = self.create_optimizer()
            sgd = self._optimizer
        pipes = list(self.pipeline)
        random.shuffle(pipes)
        if component_cfg is None:
            component_cfg = {}
        grads = {}

        def get_grads(W, dW, key=None):
            grads[key] = (W, dW)

        get_grads.learn_rate = sgd.learn_rate
        get_grads.b1 = sgd.b1
        get_grads.b2 = sgd.b2
        for name, proc in pipes:
            if name in exclude or not hasattr(proc, "rehearse"):
                continue
            grads = {}
            proc.rehearse(
                examples, sgd=get_grads, losses=losses, **component_cfg.get(name, {})
            )
        for key, (W, dW) in grads.items():
            sgd(W, dW, key=key)
        return losses

    def begin_training(
        self,
        get_examples: Optional[Callable[[], Iterable[Example]]] = None,
        *,
        sgd: Optional[Optimizer] = None,
    ) -> Optimizer:
        warnings.warn(Warnings.W089, DeprecationWarning)
        return self.initialize(get_examples, sgd=sgd)

    def initialize(
        self,
        get_examples: Optional[Callable[[], Iterable[Example]]] = None,
        *,
        sgd: Optional[Optimizer] = None,
    ) -> Optimizer:
        """Initialize the pipe for training, using data examples if available.

        get_examples (Callable[[], Iterable[Example]]): Optional function that
            returns gold-standard Example objects.
        sgd (Optional[Optimizer]): An optimizer to use for updates. If not
            provided, will be created using the .create_optimizer() method.
        RETURNS (thinc.api.Optimizer): The optimizer.

        DOCS: https://nightly.spacy.io/api/language#initialize
        """
        if get_examples is None:
            util.logger.debug(
                "No 'get_examples' callback provided to 'Language.initialize', creating dummy examples"
            )
            doc = Doc(self.vocab, words=["x", "y", "z"])
            get_examples = lambda: [Example.from_dict(doc, {})]
        if not hasattr(get_examples, "__call__"):
            err = Errors.E930.format(
                method="Language.initialize", obj=type(get_examples)
            )
            raise TypeError(err)
        # Make sure the config is interpolated so we can resolve subsections
        config = self.config.interpolate()
        # These are the settings provided in the [initialize] block in the config
        I = registry.resolve(config["initialize"], schema=ConfigSchemaInit)
        init_vocab(
            self, data=I["vocab_data"], lookups=I["lookups"], vectors=I["vectors"]
        )
        pretrain_cfg = config.get("pretraining")
        if pretrain_cfg:
            P = registry.resolve(pretrain_cfg, schema=ConfigSchemaPretrain)
            init_tok2vec(self, P, I)
        if self.vocab.vectors.data.shape[1] >= 1:
            ops = get_current_ops()
            self.vocab.vectors.data = ops.asarray(self.vocab.vectors.data)
        if hasattr(self.tokenizer, "initialize"):
            tok_settings = validate_init_settings(
                self.tokenizer.initialize,
                I["tokenizer"],
                section="tokenizer",
                name="tokenizer",
            )
            self.tokenizer.initialize(get_examples, nlp=self, **tok_settings)
        for name, proc in self.pipeline:
            if hasattr(proc, "initialize"):
                p_settings = I["components"].get(name, {})
                p_settings = validate_init_settings(
                    proc.initialize, p_settings, section="components", name=name
                )
                proc.initialize(get_examples, nlp=self, **p_settings)
        self._link_components()
        self._optimizer = sgd
        if sgd is not None:
            self._optimizer = sgd
        elif self._optimizer is None:
            self._optimizer = self.create_optimizer()
        return self._optimizer

    def resume_training(self, *, sgd: Optional[Optimizer] = None) -> Optimizer:
        """Continue training a pretrained model.

        Create and return an optimizer, and initialize "rehearsal" for any pipeline
        component that has a .rehearse() method. Rehearsal is used to prevent
        models from "forgetting" their initialized "knowledge". To perform
        rehearsal, collect samples of text you want the models to retain performance
        on, and call nlp.rehearse() with a batch of Example objects.

        RETURNS (Optimizer): The optimizer.

        DOCS: https://nightly.spacy.io/api/language#resume_training
        """
        ops = get_current_ops()
        if self.vocab.vectors.data.shape[1] >= 1:
            self.vocab.vectors.data = ops.asarray(self.vocab.vectors.data)
        for name, proc in self.pipeline:
            if hasattr(proc, "_rehearsal_model"):
                proc._rehearsal_model = deepcopy(proc.model)
        if sgd is not None:
            self._optimizer = sgd
        elif self._optimizer is None:
            self._optimizer = self.create_optimizer()
        return self._optimizer

    def evaluate(
        self,
        examples: Iterable[Example],
        *,
        batch_size: int = 256,
        scorer: Optional[Scorer] = None,
        component_cfg: Optional[Dict[str, Dict[str, Any]]] = None,
        scorer_cfg: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Union[float, dict]]:
        """Evaluate a model's pipeline components.

        examples (Iterable[Example]): `Example` objects.
        batch_size (int): Batch size to use.
        scorer (Optional[Scorer]): Scorer to use. If not passed in, a new one
            will be created.
        component_cfg (dict): An optional dictionary with extra keyword
            arguments for specific components.
        scorer_cfg (dict): An optional dictionary with extra keyword arguments
            for the scorer.
        RETURNS (Scorer): The scorer containing the evaluation results.

        DOCS: https://nightly.spacy.io/api/language#evaluate
        """
        validate_examples(examples, "Language.evaluate")
        if component_cfg is None:
            component_cfg = {}
        if scorer_cfg is None:
            scorer_cfg = {}
        if scorer is None:
            kwargs = dict(scorer_cfg)
            kwargs.setdefault("nlp", self)
            scorer = Scorer(**kwargs)
        texts = [eg.reference.text for eg in examples]
        docs = [eg.predicted for eg in examples]
        start_time = timer()
        # tokenize the texts only for timing purposes
        if not hasattr(self.tokenizer, "pipe"):
            _ = [self.tokenizer(text) for text in texts]  # noqa: F841
        else:
            _ = list(self.tokenizer.pipe(texts))  # noqa: F841
        for name, pipe in self.pipeline:
            kwargs = component_cfg.get(name, {})
            kwargs.setdefault("batch_size", batch_size)
            docs = _pipe(docs, pipe, kwargs)
        # iterate over the final generator
        if len(self.pipeline):
            docs = list(docs)
        end_time = timer()
        for i, (doc, eg) in enumerate(zip(docs, examples)):
            util.logger.debug(doc)
            eg.predicted = doc
        results = scorer.score(examples)
        n_words = sum(len(doc) for doc in docs)
        results["speed"] = n_words / (end_time - start_time)
        return results

    def create_optimizer(self):
        """Create an optimizer, usually using the [training.optimizer] config."""
        subconfig = {"optimizer": self.config["training"]["optimizer"]}
        return registry.resolve(subconfig)["optimizer"]

    @contextmanager
    def use_params(self, params: Optional[dict]):
        """Replace weights of models in the pipeline with those provided in the
        params dictionary. Can be used as a contextmanager, in which case,
        models go back to their original weights after the block.

        params (dict): A dictionary of parameters keyed by model ID.

        EXAMPLE:
            >>> with nlp.use_params(optimizer.averages):
            >>>     nlp.to_disk("/tmp/checkpoint")

        DOCS: https://nightly.spacy.io/api/language#use_params
        """
        if not params:
            yield
        else:
            contexts = [
                pipe.use_params(params)
                for name, pipe in self.pipeline
                if hasattr(pipe, "use_params") and hasattr(pipe, "model")
            ]
            # TODO: Having trouble with contextlib
            # Workaround: these aren't actually context managers atm.
            for context in contexts:
                try:
                    next(context)
                except StopIteration:
                    pass
            yield
            for context in contexts:
                try:
                    next(context)
                except StopIteration:
                    pass

    def pipe(
        self,
        texts: Iterable[str],
        *,
        as_tuples: bool = False,
        batch_size: int = 1000,
        disable: Iterable[str] = SimpleFrozenList(),
        component_cfg: Optional[Dict[str, Dict[str, Any]]] = None,
        n_process: int = 1,
    ):
        """Process texts as a stream, and yield `Doc` objects in order.

        texts (Iterable[str]): A sequence of texts to process.
        as_tuples (bool): If set to True, inputs should be a sequence of
            (text, context) tuples. Output will then be a sequence of
            (doc, context) tuples. Defaults to False.
        batch_size (int): The number of texts to buffer.
        disable (List[str]): Names of the pipeline components to disable.
        component_cfg (Dict[str, Dict]): An optional dictionary with extra keyword
            arguments for specific components.
        n_process (int): Number of processors to process texts. If -1, set `multiprocessing.cpu_count()`.
        YIELDS (Doc): Documents in the order of the original text.

        DOCS: https://nightly.spacy.io/api/language#pipe
        """
        if n_process == -1:
            n_process = mp.cpu_count()
        if as_tuples:
            text_context1, text_context2 = itertools.tee(texts)
            texts = (tc[0] for tc in text_context1)
            contexts = (tc[1] for tc in text_context2)
            docs = self.pipe(
                texts,
                batch_size=batch_size,
                disable=disable,
                n_process=n_process,
                component_cfg=component_cfg,
            )
            for doc, context in zip(docs, contexts):
                yield (doc, context)
            return
        if component_cfg is None:
            component_cfg = {}

        pipes = (
            []
        )  # contains functools.partial objects to easily create multiprocess worker.
        for name, proc in self.pipeline:
            if name in disable:
                continue
            kwargs = component_cfg.get(name, {})
            # Allow component_cfg to overwrite the top-level kwargs.
            kwargs.setdefault("batch_size", batch_size)
            f = functools.partial(_pipe, proc=proc, kwargs=kwargs)
            pipes.append(f)

        if n_process != 1:
            docs = self._multiprocessing_pipe(texts, pipes, n_process, batch_size)
        else:
            # if n_process == 1, no processes are forked.
            docs = (self.make_doc(text) for text in texts)
            for pipe in pipes:
                docs = pipe(docs)
        for doc in docs:
            yield doc

    def _multiprocessing_pipe(
        self,
        texts: Iterable[str],
        pipes: Iterable[Callable[[Doc], Doc]],
        n_process: int,
        batch_size: int,
    ) -> None:
        # raw_texts is used later to stop iteration.
        texts, raw_texts = itertools.tee(texts)
        # for sending texts to worker
        texts_q = [mp.Queue() for _ in range(n_process)]
        # for receiving byte-encoded docs from worker
        bytedocs_recv_ch, bytedocs_send_ch = zip(
            *[mp.Pipe(False) for _ in range(n_process)]
        )

        batch_texts = util.minibatch(texts, batch_size)
        # Sender sends texts to the workers.
        # This is necessary to properly handle infinite length of texts.
        # (In this case, all data cannot be sent to the workers at once)
        sender = _Sender(batch_texts, texts_q, chunk_size=n_process)
        # send twice to make process busy
        sender.send()
        sender.send()

        procs = [
            mp.Process(
                target=_apply_pipes,
                args=(self.make_doc, pipes, rch, sch, Underscore.get_state()),
            )
            for rch, sch in zip(texts_q, bytedocs_send_ch)
        ]
        for proc in procs:
            proc.start()

        # Cycle channels not to break the order of docs.
        # The received object is a batch of byte-encoded docs, so flatten them with chain.from_iterable.
        byte_docs = chain.from_iterable(recv.recv() for recv in cycle(bytedocs_recv_ch))
        docs = (Doc(self.vocab).from_bytes(byte_doc) for byte_doc in byte_docs)
        try:
            for i, (_, doc) in enumerate(zip(raw_texts, docs), 1):
                yield doc
                if i % batch_size == 0:
                    # tell `sender` that one batch was consumed.
                    sender.step()
        finally:
            for proc in procs:
                proc.terminate()

    def _link_components(self) -> None:
        """Register 'listeners' within pipeline components, to allow them to
        effectively share weights.
        """
        # I had though, "Why do we do this inside the Language object? Shouldn't
        # it be the tok2vec/transformer/etc's job?
        # The problem is we need to do it during deserialization...And the
        # components don't receive the pipeline then. So this does have to be
        # here :(
        for i, (name1, proc1) in enumerate(self.pipeline):
            if hasattr(proc1, "find_listeners"):
                for name2, proc2 in self.pipeline[i + 1 :]:
                    if isinstance(getattr(proc2, "model", None), Model):
                        proc1.find_listeners(proc2.model)

    @classmethod
    def from_config(
        cls,
        config: Union[Dict[str, Any], Config] = {},
        *,
        vocab: Union[Vocab, bool] = True,
        disable: Iterable[str] = SimpleFrozenList(),
        exclude: Iterable[str] = SimpleFrozenList(),
        meta: Dict[str, Any] = SimpleFrozenDict(),
        auto_fill: bool = True,
        validate: bool = True,
    ) -> "Language":
        """Create the nlp object from a loaded config. Will set up the tokenizer
        and language data, add pipeline components etc. If no config is provided,
        the default config of the given language is used.

        config (Dict[str, Any] / Config): The loaded config.
        vocab (Vocab): A Vocab object. If True, a vocab is created.
        disable (Iterable[str]): Names of pipeline components to disable.
            Disabled pipes will be loaded but they won't be run unless you
            explicitly enable them by calling nlp.enable_pipe.
        exclude (Iterable[str]): Names of pipeline components to exclude.
            Excluded components won't be loaded.
        meta (Dict[str, Any]): Meta overrides for nlp.meta.
        auto_fill (bool): Automatically fill in missing values in config based
            on defaults and function argument annotations.
        validate (bool): Validate the component config and arguments against
            the types expected by the factory.
        RETURNS (Language): The initialized Language class.

        DOCS: https://nightly.spacy.io/api/language#from_config
        """
        if auto_fill:
            config = Config(
                cls.default_config, section_order=CONFIG_SECTION_ORDER
            ).merge(config)
        if "nlp" not in config:
            raise ValueError(Errors.E985.format(config=config))
        config_lang = config["nlp"].get("lang")
        if config_lang is not None and config_lang != cls.lang:
            raise ValueError(
                Errors.E958.format(
                    bad_lang_code=config["nlp"]["lang"],
                    lang_code=cls.lang,
                    lang=util.get_object_name(cls),
                )
            )
        config["nlp"]["lang"] = cls.lang
        # This isn't very elegant, but we remove the [components] block here to prevent
        # it from getting resolved (causes problems because we expect to pass in
        # the nlp and name args for each component). If we're auto-filling, we're
        # using the nlp.config with all defaults.
        config = util.copy_config(config)
        orig_pipeline = config.pop("components", {})
        config["components"] = {}
        if auto_fill:
            filled = registry.fill(config, validate=validate, schema=ConfigSchema)
        else:
            filled = config
        filled["components"] = orig_pipeline
        config["components"] = orig_pipeline
        resolved_nlp = registry.resolve(
            filled["nlp"], validate=validate, schema=ConfigSchemaNlp
        )
        create_tokenizer = resolved_nlp["tokenizer"]
        before_creation = resolved_nlp["before_creation"]
        after_creation = resolved_nlp["after_creation"]
        after_pipeline_creation = resolved_nlp["after_pipeline_creation"]
        lang_cls = cls
        if before_creation is not None:
            lang_cls = before_creation(cls)
            if (
                not isinstance(lang_cls, type)
                or not issubclass(lang_cls, cls)
                or lang_cls is not cls
            ):
                raise ValueError(Errors.E943.format(value=type(lang_cls)))
        # Note that we don't load vectors here, instead they get loaded explicitly
        # inside stuff like the spacy train function. If we loaded them here,
        # then we would load them twice at runtime: once when we make from config,
        # and then again when we load from disk.
        nlp = lang_cls(vocab=vocab, create_tokenizer=create_tokenizer, meta=meta)
        if after_creation is not None:
            nlp = after_creation(nlp)
            if not isinstance(nlp, cls):
                raise ValueError(Errors.E942.format(name="creation", value=type(nlp)))
        # To create the components we need to use the final interpolated config
        # so all values are available (if component configs use variables).
        # Later we replace the component config with the raw config again.
        interpolated = filled.interpolate() if not filled.is_interpolated else filled
        pipeline = interpolated.get("components", {})
        # If components are loaded from a source (existing models), we cache
        # them here so they're only loaded once
        source_nlps = {}
        for pipe_name in config["nlp"]["pipeline"]:
            if pipe_name not in pipeline:
                opts = ", ".join(pipeline.keys())
                raise ValueError(Errors.E956.format(name=pipe_name, opts=opts))
            pipe_cfg = util.copy_config(pipeline[pipe_name])
            raw_config = Config(filled["components"][pipe_name])
            if pipe_name not in exclude:
                if "factory" not in pipe_cfg and "source" not in pipe_cfg:
                    err = Errors.E984.format(name=pipe_name, config=pipe_cfg)
                    raise ValueError(err)
                if "factory" in pipe_cfg:
                    factory = pipe_cfg.pop("factory")
                    # The pipe name (key in the config) here is the unique name
                    # of the component, not necessarily the factory
                    nlp.add_pipe(
                        factory,
                        name=pipe_name,
                        config=pipe_cfg,
                        validate=validate,
                        raw_config=raw_config,
                    )
                else:
                    model = pipe_cfg["source"]
                    if model not in source_nlps:
                        # We only need the components here and we need to init
                        # model with the same vocab as the current nlp object
                        source_nlps[model] = util.load_model(
                            model, vocab=nlp.vocab, disable=["vocab", "tokenizer"]
                        )
                    source_name = pipe_cfg.get("component", pipe_name)
                    nlp.add_pipe(source_name, source=source_nlps[model], name=pipe_name)
        disabled_pipes = [*config["nlp"]["disabled"], *disable]
        nlp._disabled = set(p for p in disabled_pipes if p not in exclude)
        nlp.config = filled if auto_fill else config
        if after_pipeline_creation is not None:
            nlp = after_pipeline_creation(nlp)
            if not isinstance(nlp, cls):
                raise ValueError(
                    Errors.E942.format(name="pipeline_creation", value=type(nlp))
                )
        return nlp

    def to_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> None:
        """Save the current state to a directory.  If a model is loaded, this
        will include the model.

        path (str / Path): Path to a directory, which will be created if
            it doesn't exist.
        exclude (list): Names of components or serialization fields to exclude.

        DOCS: https://nightly.spacy.io/api/language#to_disk
        """
        path = util.ensure_path(path)
        serializers = {}
        serializers["tokenizer"] = lambda p: self.tokenizer.to_disk(
            p, exclude=["vocab"]
        )
        serializers["meta.json"] = lambda p: srsly.write_json(p, self.meta)
        serializers["config.cfg"] = lambda p: self.config.to_disk(p)
        for name, proc in self._components:
            if name in exclude:
                continue
            if not hasattr(proc, "to_disk"):
                continue
            serializers[name] = lambda p, proc=proc: proc.to_disk(p, exclude=["vocab"])
        serializers["vocab"] = lambda p: self.vocab.to_disk(p)
        util.to_disk(path, serializers, exclude)

    def from_disk(
        self, path: Union[str, Path], *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "Language":
        """Loads state from a directory. Modifies the object in place and
        returns it. If the saved `Language` object contains a model, the
        model will be loaded.

        path (str / Path): A path to a directory.
        exclude (list): Names of components or serialization fields to exclude.
        RETURNS (Language): The modified `Language` object.

        DOCS: https://nightly.spacy.io/api/language#from_disk
        """

        def deserialize_meta(path: Path) -> None:
            if path.exists():
                data = srsly.read_json(path)
                self.meta.update(data)
                # self.meta always overrides meta["vectors"] with the metadata
                # from self.vocab.vectors, so set the name directly
                self.vocab.vectors.name = data.get("vectors", {}).get("name")

        def deserialize_vocab(path: Path) -> None:
            if path.exists():
                self.vocab.from_disk(path)

        path = util.ensure_path(path)
        deserializers = {}
        if Path(path / "config.cfg").exists():
            deserializers["config.cfg"] = lambda p: self.config.from_disk(
                p, interpolate=False
            )
        deserializers["meta.json"] = deserialize_meta
        deserializers["vocab"] = deserialize_vocab
        deserializers["tokenizer"] = lambda p: self.tokenizer.from_disk(
            p, exclude=["vocab"]
        )
        for name, proc in self._components:
            if name in exclude:
                continue
            if not hasattr(proc, "from_disk"):
                continue
            deserializers[name] = lambda p, proc=proc: proc.from_disk(
                p, exclude=["vocab"]
            )
        if not (path / "vocab").exists() and "vocab" not in exclude:
            # Convert to list here in case exclude is (default) tuple
            exclude = list(exclude) + ["vocab"]
        util.from_disk(path, deserializers, exclude)
        self._path = path
        self._link_components()
        return self

    def to_bytes(self, *, exclude: Iterable[str] = SimpleFrozenList()) -> bytes:
        """Serialize the current state to a binary string.

        exclude (list): Names of components or serialization fields to exclude.
        RETURNS (bytes): The serialized form of the `Language` object.

        DOCS: https://nightly.spacy.io/api/language#to_bytes
        """
        serializers = {}
        serializers["vocab"] = lambda: self.vocab.to_bytes()
        serializers["tokenizer"] = lambda: self.tokenizer.to_bytes(exclude=["vocab"])
        serializers["meta.json"] = lambda: srsly.json_dumps(self.meta)
        serializers["config.cfg"] = lambda: self.config.to_bytes()
        for name, proc in self._components:
            if name in exclude:
                continue
            if not hasattr(proc, "to_bytes"):
                continue
            serializers[name] = lambda proc=proc: proc.to_bytes(exclude=["vocab"])
        return util.to_bytes(serializers, exclude)

    def from_bytes(
        self, bytes_data: bytes, *, exclude: Iterable[str] = SimpleFrozenList()
    ) -> "Language":
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        exclude (list): Names of components or serialization fields to exclude.
        RETURNS (Language): The `Language` object.

        DOCS: https://nightly.spacy.io/api/language#from_bytes
        """

        def deserialize_meta(b):
            data = srsly.json_loads(b)
            self.meta.update(data)
            # self.meta always overrides meta["vectors"] with the metadata
            # from self.vocab.vectors, so set the name directly
            self.vocab.vectors.name = data.get("vectors", {}).get("name")

        deserializers = {}
        deserializers["config.cfg"] = lambda b: self.config.from_bytes(
            b, interpolate=False
        )
        deserializers["meta.json"] = deserialize_meta
        deserializers["vocab"] = self.vocab.from_bytes
        deserializers["tokenizer"] = lambda b: self.tokenizer.from_bytes(
            b, exclude=["vocab"]
        )
        for name, proc in self._components:
            if name in exclude:
                continue
            if not hasattr(proc, "from_bytes"):
                continue
            deserializers[name] = lambda b, proc=proc: proc.from_bytes(
                b, exclude=["vocab"]
            )
        util.from_bytes(bytes_data, deserializers, exclude)
        self._link_components()
        return self


@dataclass
class FactoryMeta:
    """Dataclass containing information about a component and its defaults
    provided by the @Language.component or @Language.factory decorator. It's
    created whenever a component is defined and stored on the Language class for
    each component instance and factory instance.
    """

    factory: str
    default_config: Optional[Dict[str, Any]] = None  # noqa: E704
    assigns: Iterable[str] = tuple()
    requires: Iterable[str] = tuple()
    retokenizes: bool = False
    scores: Iterable[str] = tuple()
    default_score_weights: Optional[Dict[str, float]] = None  # noqa: E704


class DisabledPipes(list):
    """Manager for temporary pipeline disabling."""

    def __init__(self, nlp: Language, names: List[str]) -> None:
        self.nlp = nlp
        self.names = names
        for name in self.names:
            self.nlp.disable_pipe(name)
        list.__init__(self)
        self.extend(self.names)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.restore()

    def restore(self) -> None:
        """Restore the pipeline to its state when DisabledPipes was created."""
        for name in self.names:
            if name not in self.nlp.component_names:
                raise ValueError(Errors.E008.format(name=name))
            self.nlp.enable_pipe(name)
        self[:] = []


def _apply_pipes(
    make_doc: Callable[[str], Doc],
    pipes: Iterable[Callable[[Doc], Doc]],
    receiver,
    sender,
    underscore_state: Tuple[dict, dict, dict],
) -> None:
    """Worker for Language.pipe

    make_doc (Callable[[str,] Doc]): Function to create Doc from text.
    pipes (Iterable[Callable[[Doc], Doc]]): The components to apply.
    receiver (multiprocessing.Connection): Pipe to receive text. Usually
        created by `multiprocessing.Pipe()`
    sender (multiprocessing.Connection): Pipe to send doc. Usually created by
        `multiprocessing.Pipe()`
    underscore_state (Tuple[dict, dict, dict]): The data in the Underscore class
        of the parent.
    """
    Underscore.load_state(underscore_state)
    while True:
        texts = receiver.get()
        docs = (make_doc(text) for text in texts)
        for pipe in pipes:
            docs = pipe(docs)
        # Connection does not accept unpickable objects, so send list.
        sender.send([doc.to_bytes() for doc in docs])


class _Sender:
    """Util for sending data to multiprocessing workers in Language.pipe"""

    def __init__(
        self, data: Iterable[Any], queues: List[mp.Queue], chunk_size: int
    ) -> None:
        self.data = iter(data)
        self.queues = iter(cycle(queues))
        self.chunk_size = chunk_size
        self.count = 0

    def send(self) -> None:
        """Send chunk_size items from self.data to channels."""
        for item, q in itertools.islice(
            zip(self.data, cycle(self.queues)), self.chunk_size
        ):
            # cycle channels so that distribute the texts evenly
            q.put(item)

    def step(self) -> None:
        """Tell sender that comsumed one item. Data is sent to the workers after
        every chunk_size calls.
        """
        self.count += 1
        if self.count >= self.chunk_size:
            self.count = 0
            self.send()
