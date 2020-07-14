from typing import Optional, Any, Dict, Callable, Iterable, Union, List
from dataclasses import dataclass
import random
import itertools
import weakref
import functools
from collections import Iterable as IterableInstance
from contextlib import contextmanager
from copy import copy, deepcopy
from pathlib import Path
import warnings
import inspect

from thinc.api import get_current_ops, Config, require_gpu, Optimizer
import srsly
import multiprocessing as mp
from itertools import chain, cycle

from .tokenizer import Tokenizer
from .tokens.underscore import Underscore
from .vocab import Vocab
from .lemmatizer import Lemmatizer
from .lookups import Lookups
from .pipe_analysis import analyze_pipes, analyze_all_pipes
from .gold import Example
from .scorer import Scorer
from .util import link_vectors_to_models, create_default_optimizer, registry
from .util import SimpleFrozenDict
from .attrs import IS_STOP, LANG, NORM
from .lang.punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES
from .lang.punctuation import TOKENIZER_INFIXES
from .lang.tokenizer_exceptions import TOKEN_MATCH, URL_MATCH
from .lang.norm_exceptions import BASE_NORMS
from .lang.tag_map import TAG_MAP
from .tokens import Doc
from .lang.lex_attrs import LEX_ATTRS, is_stop
from .errors import Errors, Warnings
from . import util
from . import about


ENABLE_PIPELINE_ANALYSIS = False


class BaseDefaults:
    @classmethod
    def create_lemmatizer(cls, nlp=None, lookups=None):
        if lookups is None:
            lookups = cls.create_lookups(nlp=nlp)
        return Lemmatizer(lookups=lookups)

    @classmethod
    def create_lookups(cls, nlp=None):
        root = util.get_module_path(cls)
        filenames = {name: root / filename for name, filename in cls.resources}
        if LANG in cls.lex_attr_getters:
            lang = cls.lex_attr_getters[LANG](None)
            if lang in util.registry.lookups:
                filenames.update(util.registry.lookups.get(lang))
        lookups = Lookups()
        for name, filename in filenames.items():
            data = util.load_language_data(filename)
            lookups.add_table(name, data)
        return lookups

    @classmethod
    def create_vocab(cls, nlp=None):
        lookups = cls.create_lookups(nlp)
        lemmatizer = cls.create_lemmatizer(nlp, lookups=lookups)
        lex_attr_getters = dict(cls.lex_attr_getters)
        # This is messy, but it's the minimal working fix to Issue #639.
        lex_attr_getters[IS_STOP] = functools.partial(is_stop, stops=cls.stop_words)
        vocab = Vocab(
            lex_attr_getters=lex_attr_getters,
            tag_map=cls.tag_map,
            lemmatizer=lemmatizer,
            lookups=lookups,
        )
        vocab.lex_attr_getters[NORM] = util.add_lookups(
            vocab.lex_attr_getters.get(NORM, LEX_ATTRS[NORM]),
            BASE_NORMS,
            vocab.lookups.get_table("lexeme_norm"),
        )
        for tag_str, exc in cls.morph_rules.items():
            for orth_str, attrs in exc.items():
                vocab.morphology.add_special_case(tag_str, orth_str, attrs)
        return vocab

    @classmethod
    def create_tokenizer(cls, nlp=None):
        rules = cls.tokenizer_exceptions
        token_match = cls.token_match
        url_match = cls.url_match
        prefix_search = (
            util.compile_prefix_regex(cls.prefixes).search if cls.prefixes else None
        )
        suffix_search = (
            util.compile_suffix_regex(cls.suffixes).search if cls.suffixes else None
        )
        infix_finditer = (
            util.compile_infix_regex(cls.infixes).finditer if cls.infixes else None
        )
        vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)
        return Tokenizer(
            vocab,
            rules=rules,
            prefix_search=prefix_search,
            suffix_search=suffix_search,
            infix_finditer=infix_finditer,
            token_match=token_match,
            url_match=url_match,
        )

    pipe_names = ["tagger", "parser", "ner"]
    token_match = TOKEN_MATCH
    url_match = URL_MATCH
    prefixes = tuple(TOKENIZER_PREFIXES)
    suffixes = tuple(TOKENIZER_SUFFIXES)
    infixes = tuple(TOKENIZER_INFIXES)
    tag_map = dict(TAG_MAP)
    tokenizer_exceptions = {}
    stop_words = set()
    morph_rules = {}
    lex_attr_getters = LEX_ATTRS
    syntax_iterators = {}
    resources = {}
    writing_system = {"direction": "ltr", "has_case": True, "has_letters": True}
    single_orth_variants = []
    paired_orth_variants = []


class Language:
    """A text-processing pipeline. Usually you'll load this once per process,
    and pass the instance around your application.

    Defaults (class): Settings, data and factory methods for creating the `nlp`
        object and processing pipeline.
    lang (str): Two-letter language ID, i.e. ISO code.

    DOCS: https://spacy.io/api/language
    """

    Defaults = BaseDefaults
    lang = None

    # TODO: remove
    factories = {"tokenizer": lambda nlp: nlp.Defaults.create_tokenizer(nlp)}

    _factory_meta = {}  # meta by factory
    _pipe_meta = {}  # meta by component
    _pipe_configs = {}  # config by component

    def __init__(
        self,
        vocab: Union[Vocab, bool] = True,
        make_doc: bool = True,
        max_length: int = 10 ** 6,
        meta: Dict[str, Any] = {},
        config: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Initialise a Language object.

        vocab (Vocab): A `Vocab` object. If `True`, a vocab is created via
            `Language.Defaults.create_vocab`.
        make_doc (callable): A function that takes text and returns a `Doc`
            object. Usually a `Tokenizer`.
        meta (dict): Custom meta data for the Language class. Is written to by
            models to add model meta data.
        config (Config): Configuration data for creating the pipeline components.
        max_length (int) :
            Maximum number of characters in a single text. The current v2 models
            may run out memory on extremely long texts, due to large internal
            allocations. You should segment these texts into meaningful units,
            e.g. paragraphs, subsections etc, before passing them to spaCy.
            Default maximum length is 1,000,000 characters (1mb). As a rule of
            thumb, if all pipeline components are enabled, spaCy's default
            models currently requires roughly 1GB of temporary memory per
            100,000 characters in one text.
        RETURNS (Language): The newly constructed object.
        """
        # We're only calling this to import all factories provided via entry
        # points. The factory decorator applied to these functions takes care
        # of the rest.
        util.registry._entry_point_factories.get_all()
        self._meta = dict(meta)
        self._config = config
        if not self._config:
            self._config = Config()
        self._path = None
        if vocab is True:
            factory = self.Defaults.create_vocab
            vocab = factory(self, **meta.get("vocab", {}))
            if vocab.vectors.name is None:
                vocab.vectors.name = meta.get("vectors", {}).get("name")
        else:
            if (self.lang and vocab.lang) and (self.lang != vocab.lang):
                raise ValueError(Errors.E150.format(nlp=self.lang, vocab=vocab.lang))
        self.vocab = vocab
        if make_doc is True:
            factory = self.Defaults.create_tokenizer
            make_doc = factory(self, **meta.get("tokenizer", {}))
        self.tokenizer = make_doc
        self.pipeline = []
        self.max_length = max_length
        self._optimizer = None

    @property
    def path(self):
        return self._path

    @property
    def meta(self) -> Dict[str, Any]:
        spacy_version = util.get_model_version_range(about.__version__)
        if self.vocab.lang:
            self._meta.setdefault("lang", self.vocab.lang)
        else:
            self._meta.setdefault("lang", self.lang)
        self._meta.setdefault("name", "model")
        self._meta.setdefault("version", "0.0.0")
        self._meta.setdefault("spacy_version", spacy_version)
        self._meta.setdefault("description", "")
        self._meta.setdefault("author", "")
        self._meta.setdefault("email", "")
        self._meta.setdefault("url", "")
        self._meta.setdefault("license", "")
        self._meta["vectors"] = {
            "width": self.vocab.vectors_length,
            "vectors": len(self.vocab.vectors),
            "keys": self.vocab.vectors.n_keys,
            "name": self.vocab.vectors.name,
        }
        self._meta["pipeline"] = self.pipe_names
        self._meta["factories"] = self.pipe_factories
        self._meta["labels"] = self.pipe_labels
        return self._meta

    @meta.setter
    def meta(self, value):
        self._meta = value

    @property
    def config(self) -> Config:
        self._config.setdefault("nlp", {})
        self._config["nlp"]["lang"] = self.meta["lang"]
        # We're storing the filled config for each pipeline component and so
        # we can populate the config again later
        pipeline = {}
        for pipe_name in self.pipe_names:
            pipe_meta = self.get_pipe_meta(pipe_name)
            pipe_config = self.get_pipe_config(pipe_name)
            pipeline[pipe_name] = {"@factories": pipe_meta.factory, **pipe_config}
        self._config["nlp"]["pipeline"] = pipeline
        if not srsly.is_json_serializable(self._config):
            raise ValueError(Errors.E961.format(config=self._config))
        return self._config

    @config.setter
    def config(self, value: Config) -> None:
        self._config = value

    @property
    def pipe_names(self) -> List[str]:
        """Get names of available pipeline components.

        RETURNS (list): List of component name strings, in order.
        """
        return [pipe_name for pipe_name, _ in self.pipeline]

    @property
    def pipe_factories(self) -> Dict[str, str]:
        """Get the component factories for the available pipeline components.

        RETURNS (dict): Factory names, keyed by component names.
        """
        factories = {}
        for pipe_name, pipe in self.pipeline:
            factories[pipe_name] = self.get_pipe_meta(pipe_name).factory
        return factories

    @property
    def pipe_labels(self) -> Dict[str, List[str]]:
        """Get the labels set by the pipeline components, if available (if
        the component exposes a labels property).

        RETURNS (dict): Labels keyed by component name.
        """
        labels = {}
        for name, pipe in self.pipeline:
            if hasattr(pipe, "labels"):
                labels[name] = list(pipe.labels)
        return labels

    @classmethod
    def has_factory(cls, name: str) -> bool:
        """RETURNS (bool): Whether a factory of that name is registered."""
        return name in registry.factories

    @classmethod
    def get_factory_meta(cls, name: str) -> "FactoryMeta":
        """RETURNS (FactoryMeta): The meta for the given factory name."""
        if name not in cls._factory_meta:
            raise ValueError(Errors.E967.format(meta="factory", name=name))
        return cls._factory_meta[name]

    @classmethod
    def get_pipe_meta(cls, name: str) -> "FactoryMeta":
        """RETURNS (FactoryMeta): The meta for the given component name."""
        if name not in cls._pipe_meta:
            raise ValueError(Errors.E967.format(meta="component", name=name))
        return cls._pipe_meta[name]

    @classmethod
    def get_pipe_config(cls, name: str) -> Config:
        """RETURNS (Config): The config used to create the pipeline component."""
        if name not in cls._pipe_configs:
            raise ValueError(Errors.E960.format(name=name))
        pipe_config = dict(cls._pipe_configs[name])
        # Remove auto-populated name and nlp object
        pipe_config.pop("nlp", None)
        pipe_config.pop("name", None)
        return pipe_config

    @classmethod
    def factory(
        cls,
        name: str,
        *,
        default_config: Dict[str, Any] = SimpleFrozenDict(),
        assigns: Iterable[str] = tuple(),
        requires: Iterable[str] = tuple(),
        retokenizes: bool = False,
        func: Optional[Any] = None,
    ) -> Callable:
        """Register a new pipeline component factory. Can be used as a decorator
        on a function or classmethod, or called as a function with the factory
        provided as the func keyword argument.
        """
        if not isinstance(name, str):
            raise ValueError(Errors.E963.format(decorator="factory"))
        if not isinstance(default_config, dict):
            err = Errors.E962.format(
                style="default config", name=name, cfg_type=type(default_config)
            )
            raise ValueError(err)
        if cls.has_factory(name):
            raise ValueError(Errors.E004.format(name=name))

        def add_factory(factory_func: Callable) -> Callable:
            argspec = inspect.getfullargspec(factory_func).args
            if "nlp" not in argspec or "name" not in argspec:
                raise ValueError(Errors.E964.format(name=name))
            # Officially register the factory so we can later call
            # registry.make_from_config and refer to it in the config as
            # @factories = "spacy.Language.xyz". We use the class name here so
            # different classes can have different factories.
            registry.factories.register(name, func=factory_func)
            cls._factory_meta[name] = FactoryMeta(
                factory=name,
                default_config=default_config,
                assigns=assigns,
                requires=requires,
                retokenizes=retokenizes,
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
        assigns: Iterable[str] = tuple(),
        requires: Iterable[str] = tuple(),
        retokenizes: bool = False,
        func: Optional[Callable[[Doc], Doc]] = None,
    ) -> Callable:
        """Register a new pipeline component. Can be used for stateless function
        compponents that don't require a separate factory. Can be used as a
        decorator on a function or classmethod, or called as a function with the
        factory provided as the func keyword argument.
        """
        if name is not None and not isinstance(name, str):
            raise ValueError(Errors.E963.format(decorator="component"))
        component_name = name if name is not None else util.get_component_name(func)

        def add_component(component_func: Callable[[Doc], Doc]) -> Callable:
            if isinstance(func, type):  # function is a class
                raise ValueError(Errors.E965.format(name=component_name))

            def factory_func(nlp: cls, name: str) -> Callable[[Doc], Doc]:
                return component_func

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

    def get_pipe(self, name: str) -> Callable[[Doc], Doc]:
        """Get a pipeline component for a given component name.

        name (str): Name of pipeline component to get.
        RETURNS (callable): The pipeline component.

        DOCS: https://spacy.io/api/language#get_pipe
        """
        for pipe_name, component in self.pipeline:
            if pipe_name == name:
                return component
        raise KeyError(Errors.E001.format(name=name, opts=self.pipe_names))

    def create_pipe(
        self,
        factory_name: str,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = SimpleFrozenDict(),
        validate: bool = True,
    ) -> Callable[[Doc], Doc]:
        name = name if name is not None else factory_name
        if not isinstance(config, dict):
            err = Errors.E962.format(style="config", name=name, cfg_type=type(config))
            raise ValueError(err)
        if not srsly.is_json_serializable(config):
            raise ValueError(Errors.E961.format(config=config))
        if not self.has_factory(factory_name):
            raise ValueError(Errors.E002.format(name=factory_name))
        pipe_meta = self.get_factory_meta(factory_name)
        config = config or {}
        # This is unideal, but the alternative would mean you always need to
        # specify the full config settings, which is not really viable.
        if pipe_meta.default_config:
            config = util.deep_merge_configs(config, pipe_meta.default_config)
        # We need to create a top-level key because Thinc doesn't allow resolving
        # top-level references to registered functions. Also gives nicer errors.
        # The name allows components to know their pipe name and use it in the
        # losses etc. (even if multiple instances of the same factory are used)
        config = {"@factories": factory_name, "nlp": self, "name": name, **config}
        cfg = {factory_name: config}
        # We're calling the internal _fill here to avoid constructing the
        # registered functions twice
        # TODO: customize validation to make it more readable / relate it to
        # pipeline component and why it failed, explain default config
        filled, _, resolved = registry._fill(cfg, validate=validate)
        self._pipe_configs[name] = filled[factory_name]
        return resolved[factory_name]

    def add_pipe(
        self,
        factory_name: str,
        name: Optional[str] = None,
        *,
        before: Optional[Union[str, int]] = None,
        after: Optional[Union[str, int]] = None,
        first: Optional[bool] = None,
        last: Optional[bool] = None,
        config: Optional[Dict[str, Any]] = SimpleFrozenDict(),
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
        before (str): Name or index of the component to insert directly before.
        after (str): Name or index of component to insert directly after.
        first (bool): Insert component first / not first in the pipeline.
        last (bool): Insert component last / not last in the pipeline.

        DOCS: https://spacy.io/api/language#add_pipe
        """
        # TODO: validate other arguments (name etc.)
        if not isinstance(factory_name, str):
            bad_val = repr(factory_name)
            err = Errors.E966.format(component=bad_val, name=name, method="add_pipe")
            raise ValueError(err)
        if not self.has_factory(factory_name):
            raise ValueError(Errors.E002.format(name=factory_name))
        name = name if name is not None else factory_name
        if name in self.pipe_names:
            raise ValueError(Errors.E007.format(name=name, opts=self.pipe_names))
        pipe_component = self.create_pipe(
            factory_name, name=name, config=config, validate=validate
        )
        pipe_index = self._get_pipe_index(before, after, first, last)
        self._pipe_meta[name] = self.get_factory_meta(factory_name)
        self.pipeline.insert(pipe_index, (name, pipe_component))
        if ENABLE_PIPELINE_ANALYSIS:
            analyze_pipes(self.pipeline, name, self.get_pipe_meta, pipe_index)
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
        first (bool): Insert component first / not first in the pipeline.
        last (bool): Insert component last / not last in the pipeline.
        RETURNS (int): The index of the new pipeline component.
        """
        all_args = {"before": before, "after": after, "first": first, "last": last}
        if sum(arg is not None for arg in [before, after, first, last]) >= 2:
            raise ValueError(Errors.E006.format(args=all_args, opts=self.pipe_names))
        if last or not any(value is not None for value in [first, before, after]):
            return len(self.pipeline)
        elif first:
            return 0
        elif isinstance(before, str):
            if before not in self.pipe_names:
                raise ValueError(Errors.E001.format(name=before, opts=self.pipe_names))
            return self.pipe_names.index(before)
        elif isinstance(after, str):
            if after not in self.pipe_names:
                raise ValueError(Errors.E001.format(name=after, opts=self.pipe_names))
            return self.pipe_names.index(after) + 1
        # We're only accepting indices referring to components that exist
        # (can't just do isinstance here because bools are instance of int, too)
        elif type(before) == int:
            if before >= len(self.pipeline) or before < 0:
                err = Errors.E959.format(dir="before", idx=before, opts=self.pipe_names)
                raise ValueError(err)
            return before
        elif type(after) == int:
            if after >= len(self.pipeline) or after < 0:
                err = Errors.E959.format(dir="after", idx=after, opts=self.pipe_names)
                raise ValueError(err)
            return after + 1
        raise ValueError(Errors.E006.format(args=all_args, opts=self.pipe_names))

    def has_pipe(self, name: str) -> bool:
        """Check if a component name is present in the pipeline. Equivalent to
        `name in nlp.pipe_names`.

        name (str): Name of the component.
        RETURNS (bool): Whether a component of the name exists in the pipeline.

        DOCS: https://spacy.io/api/language#has_pipe
        """
        return name in self.pipe_names

    def replace_pipe(
        self,
        name: str,
        factory_name: str,
        config: Dict[str, Any] = SimpleFrozenDict(),
        validate: bool = True,
    ) -> None:
        """Replace a component in the pipeline.

        name (str): Name of the component to replace.
        factory_name (str): Factory name of replacement component.

        DOCS: https://spacy.io/api/language#replace_pipe
        """
        if name not in self.pipe_names:
            raise ValueError(Errors.E001.format(name=name, opts=self.pipe_names))
        if hasattr(factory_name, "__call__"):
            err = Errors.E966.format(
                component=repr(factory_name), name=name, method="replace_pipe"
            )
            raise ValueError(err)
        # We need to delegate to Language.add_pipe here instead of just writing
        # to Language.pipeline to make sure the configs are handled correctly
        pipe_index = self.pipe_names.index(name)
        self.remove_pipe(name)
        if not len(self.pipeline):  # we have no components to insert before/after
            self.add_pipe(factory_name, name=name)
        else:
            self.add_pipe(factory_name, name=name, before=pipe_index)
        if ENABLE_PIPELINE_ANALYSIS:
            analyze_all_pipes(self.pipeline, self.get_pipe_meta)

    def rename_pipe(self, old_name: str, new_name: str) -> None:
        """Rename a pipeline component.

        old_name (str): Name of the component to rename.
        new_name (str): New name of the component.

        DOCS: https://spacy.io/api/language#rename_pipe
        """
        if old_name not in self.pipe_names:
            raise ValueError(Errors.E001.format(name=old_name, opts=self.pipe_names))
        if new_name in self.pipe_names:
            raise ValueError(Errors.E007.format(name=new_name, opts=self.pipe_names))
        i = self.pipe_names.index(old_name)
        self.pipeline[i] = (new_name, self.pipeline[i][1])
        self._pipe_meta[new_name] = self._pipe_meta.pop(old_name)
        self._pipe_configs[new_name] = self._pipe_configs.pop(old_name)

    def remove_pipe(self, name: str) -> Callable[[Doc], Doc]:
        """Remove a component from the pipeline.

        name (str): Name of the component to remove.
        RETURNS (tuple): A `(name, component)` tuple of the removed component.

        DOCS: https://spacy.io/api/language#remove_pipe
        """
        if name not in self.pipe_names:
            raise ValueError(Errors.E001.format(name=name, opts=self.pipe_names))
        removed = self.pipeline.pop(self.pipe_names.index(name))
        # We're only removing the component itself from the metas/configs here
        # because factory may be used for something else
        self._pipe_meta.pop(name)
        self._pipe_configs.pop(name)
        if ENABLE_PIPELINE_ANALYSIS:
            analyze_all_pipes(self.pipeline, self.get_pipe_meta)
        return removed

    def __call__(
        self,
        text: str,
        disable: Iterable[str] = tuple(),
        component_cfg: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Doc:
        """Apply the pipeline to some text. The text can span multiple sentences,
        and can contain arbitrary whitespace. Alignment into the original string
        is preserved.

        text (str): The text to be processed.
        disable (list): Names of the pipeline components to disable.
        component_cfg (dict): An optional dictionary with extra keyword arguments
            for specific components.
        RETURNS (Doc): A container for accessing the annotations.

        DOCS: https://spacy.io/api/language#call
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
            except KeyError:
                raise ValueError(Errors.E109.format(name=name))
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
        return DisabledPipes(self, names)

    def select_pipes(
        self,
        disable: Optional[Union[str, Iterable[str]]] = None,
        enable: Optional[Union[str, Iterable[str]]] = None,
    ) -> "DisabledPipes":
        """Disable one or more pipeline components. If used as a context
        manager, the pipeline will be restored to the initial state at the end
        of the block. Otherwise, a DisabledPipes object is returned, that has
        a `.restore()` method you can use to undo your changes.

        disable (str or iterable): The name(s) of the pipes to disable
        enable (str or iterable): The name(s) of the pipes to enable - all others will be disabled

        DOCS: https://spacy.io/api/language#select_pipes
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
        return DisabledPipes(self, disable)

    def make_doc(self, text: str) -> Doc:
        return self.tokenizer(text)

    def update(
        self,
        examples: Iterable[Example],
        dummy: Optional[Any] = None,
        *,
        drop: float = 0.0,
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
        component_cfg: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """Update the models in the pipeline.

        examples (Iterable[Example]): A batch of examples
        dummy: Should not be set - serves to catch backwards-incompatible scripts.
        drop (float): The dropout rate.
        sgd (Optimizer): An optimizer.
        losses (Dict[str, float]): Dictionary to update with the loss, keyed by component.
        component_cfg (Dict[str, Dict]): Config parameters for specific pipeline
            components, keyed by component name.
        RETURNS (Dict[str, float]): The updated losses dictionary

        DOCS: https://spacy.io/api/language#update
        """
        if dummy is not None:
            raise ValueError(Errors.E989)
        if losses is None:
            losses = {}
        if len(examples) == 0:
            return losses
        if not isinstance(examples, IterableInstance):
            raise TypeError(
                Errors.E978.format(
                    name="language", method="update", types=type(examples)
                )
            )
        wrong_types = set([type(eg) for eg in examples if not isinstance(eg, Example)])
        if wrong_types:
            raise TypeError(
                Errors.E978.format(name="language", method="update", types=wrong_types)
            )

        if sgd is None:
            if self._optimizer is None:
                self._optimizer = create_default_optimizer()
            sgd = self._optimizer

        if component_cfg is None:
            component_cfg = {}
        for i, (name, proc) in enumerate(self.pipeline):
            component_cfg.setdefault(name, {})
            component_cfg[name].setdefault("drop", drop)
            component_cfg[name].setdefault("set_annotations", False)
        for name, proc in self.pipeline:
            if not hasattr(proc, "update"):
                continue
            proc.update(examples, sgd=None, losses=losses, **component_cfg[name])
        if sgd not in (None, False):
            for name, proc in self.pipeline:
                if hasattr(proc, "model"):
                    proc.model.finish_update(sgd)
        return losses

    def rehearse(
        self,
        examples: Iterable[Example],
        sgd: Optional[Optimizer] = None,
        losses: Optional[Dict[str, float]] = None,
        component_cfg: Optional[Dict[str, Dict[str, Any]]] = None,
    ):
        """Make a "rehearsal" update to the models in the pipeline, to prevent
        forgetting. Rehearsal updates run an initial copy of the model over some
        data, and update the model so its current predictions are more like the
        initial ones. This is useful for keeping a pretrained model on-track,
        even if you're updating it with a smaller set of examples.

        examples (iterable): A batch of `Example` objects.
        drop (float): The dropout rate.
        sgd (callable): An optimizer.
        RETURNS (dict): Results from the update.

        EXAMPLE:
            >>> raw_text_batches = minibatch(raw_texts)
            >>> for labelled_batch in minibatch(examples):
            >>>     nlp.update(labelled_batch)
            >>>     raw_batch = [Example.from_dict(nlp.make_doc(text), {}) for text in next(raw_text_batches)]
            >>>     nlp.rehearse(raw_batch)
        """
        # TODO: document
        if len(examples) == 0:
            return
        if not isinstance(examples, IterableInstance):
            raise TypeError(
                Errors.E978.format(
                    name="language", method="rehearse", types=type(examples)
                )
            )
        wrong_types = set([type(eg) for eg in examples if not isinstance(eg, Example)])
        if wrong_types:
            raise TypeError(
                Errors.E978.format(
                    name="language", method="rehearse", types=wrong_types
                )
            )
        if sgd is None:
            if self._optimizer is None:
                self._optimizer = create_default_optimizer()
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
            if not hasattr(proc, "rehearse"):
                continue
            grads = {}
            proc.rehearse(
                examples, sgd=get_grads, losses=losses, **component_cfg.get(name, {})
            )
        for key, (W, dW) in grads.items():
            sgd(W, dW, key=key)
        return losses

    def begin_training(self, get_examples=None, sgd=None, component_cfg=None, **cfg):
        """Allocate models, pre-process training data and acquire a trainer and
        optimizer. Used as a contextmanager.

        get_examples (function): Function returning example training data (TODO: document format change since 3.0)
        component_cfg (dict): Config parameters for specific components.
        **cfg: Config parameters.
        RETURNS: An optimizer.

        DOCS: https://spacy.io/api/language#begin_training
        """
        # TODO: throw warning when get_gold_tuples is provided instead of get_examples
        if get_examples is None:
            get_examples = lambda: []
        # Populate vocab
        else:
            for example in get_examples():
                for word in [t.text for t in example.reference]:
                    _ = self.vocab[word]  # noqa: F841

        if cfg.get("device", -1) >= 0:
            require_gpu(cfg["device"])
            if self.vocab.vectors.data.shape[1] >= 1:
                ops = get_current_ops()
                self.vocab.vectors.data = ops.asarray(self.vocab.vectors.data)
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = create_default_optimizer()
        self._optimizer = sgd
        if component_cfg is None:
            component_cfg = {}
        for name, proc in self.pipeline:
            if hasattr(proc, "begin_training"):
                proc.begin_training(
                    get_examples, pipeline=self.pipeline, sgd=self._optimizer
                )
        self._link_components()
        return self._optimizer

    def resume_training(self, sgd=None, **cfg):
        """Continue training a pretrained model.

        Create and return an optimizer, and initialize "rehearsal" for any pipeline
        component that has a .rehearse() method. Rehearsal is used to prevent
        models from "forgetting" their initialised "knowledge". To perform
        rehearsal, collect samples of text you want the models to retain performance
        on, and call nlp.rehearse() with a batch of Example objects.
        """
        if cfg.get("device", -1) >= 0:
            require_gpu(cfg["device"])
            ops = get_current_ops()
            if self.vocab.vectors.data.shape[1] >= 1:
                self.vocab.vectors.data = ops.asarray(self.vocab.vectors.data)
        link_vectors_to_models(self.vocab)
        if sgd is None:
            sgd = create_default_optimizer()
        self._optimizer = sgd
        for name, proc in self.pipeline:
            if hasattr(proc, "_rehearsal_model"):
                proc._rehearsal_model = deepcopy(proc.model)
        return self._optimizer

    def evaluate(
        self, examples, verbose=False, batch_size=256, scorer=None, component_cfg=None
    ):
        """Evaluate a model's pipeline components.

        examples (iterable): `Example` objects.
        verbose (bool): Print debugging information.
        batch_size (int): Batch size to use.
        scorer (Scorer): Optional `Scorer` to use. If not passed in, a new one
            will be created.
        component_cfg (dict): An optional dictionary with extra keyword
            arguments for specific components.
        RETURNS (Scorer): The scorer containing the evaluation results.

        DOCS: https://spacy.io/api/language#evaluate
        """
        if not isinstance(examples, IterableInstance):
            raise TypeError(
                Errors.E978.format(
                    name="language", method="evaluate", types=type(examples)
                )
            )
        wrong_types = set([type(eg) for eg in examples if not isinstance(eg, Example)])
        if wrong_types:
            raise TypeError(
                Errors.E978.format(
                    name="language", method="evaluate", types=wrong_types
                )
            )
        if scorer is None:
            scorer = Scorer(pipeline=self.pipeline)
        if component_cfg is None:
            component_cfg = {}
        docs = list(eg.predicted for eg in examples)
        for name, pipe in self.pipeline:
            kwargs = component_cfg.get(name, {})
            kwargs.setdefault("batch_size", batch_size)
            if not hasattr(pipe, "pipe"):
                docs = _pipe(docs, pipe, kwargs)
            else:
                docs = pipe.pipe(docs, **kwargs)
        for i, (doc, eg) in enumerate(zip(docs, examples)):
            if verbose:
                print(doc)
            eg.predicted = doc
            kwargs = component_cfg.get("scorer", {})
            kwargs.setdefault("verbose", verbose)
            scorer.score(eg, **kwargs)
        return scorer

    @contextmanager
    def use_params(self, params, **cfg):
        """Replace weights of models in the pipeline with those provided in the
        params dictionary. Can be used as a contextmanager, in which case,
        models go back to their original weights after the block.

        params (dict): A dictionary of parameters keyed by model ID.
        **cfg: Config parameters.

        EXAMPLE:
            >>> with nlp.use_params(optimizer.averages):
            >>>     nlp.to_disk('/tmp/checkpoint')
        """
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
        as_tuples: bool = False,
        batch_size: str = 1000,
        disable: Iterable[str] = tuple(),
        cleanup: bool = False,
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
        cleanup (bool): If True, unneeded strings are freed to control memory
            use. Experimental.
        component_cfg (Dict[str, Dict]): An optional dictionary with extra keyword
            arguments for specific components.
        n_process (int): Number of processors to process texts. If -1, set `multiprocessing.cpu_count()`.
        YIELDS (Doc): Documents in the order of the original text.

        DOCS: https://spacy.io/api/language#pipe
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
            if hasattr(proc, "pipe"):
                f = functools.partial(proc.pipe, **kwargs)
            else:
                # Apply the function, but yield the doc
                f = functools.partial(_pipe, proc=proc, kwargs=kwargs)
            pipes.append(f)

        if n_process != 1:
            docs = self._multiprocessing_pipe(texts, pipes, n_process, batch_size)
        else:
            # if n_process == 1, no processes are forked.
            docs = (self.make_doc(text) for text in texts)
            for pipe in pipes:
                docs = pipe(docs)

        # Track weakrefs of "recent" documents, so that we can see when they
        # expire from memory. When they do, we know we don't need old strings.
        # This way, we avoid maintaining an unbounded growth in string entries
        # in the string store.
        recent_refs = weakref.WeakSet()
        old_refs = weakref.WeakSet()
        # Keep track of the original string data, so that if we flush old strings,
        # we can recover the original ones. However, we only want to do this if we're
        # really adding strings, to save up-front costs.
        original_strings_data = None
        nr_seen = 0
        for doc in docs:
            yield doc
            if cleanup:
                recent_refs.add(doc)
                if nr_seen < 10000:
                    old_refs.add(doc)
                    nr_seen += 1
                elif len(old_refs) == 0:
                    old_refs, recent_refs = recent_refs, old_refs
                    if original_strings_data is None:
                        original_strings_data = list(self.vocab.strings)
                    else:
                        keys, strings = self.vocab.strings._cleanup_stale_strings(
                            original_strings_data
                        )
                        self.vocab._reset_cache(keys, strings)
                        self.tokenizer._reset_cache(keys)
                    nr_seen = 0

    def _multiprocessing_pipe(self, texts, pipes, n_process, batch_size):
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

    def _link_components(self):
        """Register 'listeners' within pipeline components, to allow them to
        effectively share weights.
        """
        for i, (name1, proc1) in enumerate(self.pipeline):
            if hasattr(proc1, "find_listeners"):
                for name2, proc2 in self.pipeline[i:]:
                    if hasattr(proc2, "model"):
                        proc1.find_listeners(proc2.model)

    def to_disk(self, path: Union[str, Path], exclude: Iterable[str] = tuple()) -> None:
        """Save the current state to a directory.  If a model is loaded, this
        will include the model.

        path (str / Path): Path to a directory, which will be created if
            it doesn't exist.
        exclude (list): Names of components or serialization fields to exclude.

        DOCS: https://spacy.io/api/language#to_disk
        """
        path = util.ensure_path(path)
        serializers = {}
        serializers["tokenizer"] = lambda p: self.tokenizer.to_disk(
            p, exclude=["vocab"]
        )
        serializers["meta.json"] = lambda p: srsly.write_json(p, self.meta)
        serializers["config.cfg"] = lambda p: self.config.to_disk(p)
        for name, proc in self.pipeline:
            if not hasattr(proc, "name"):
                continue
            if name in exclude:
                continue
            if not hasattr(proc, "to_disk"):
                continue
            serializers[name] = lambda p, proc=proc: proc.to_disk(p, exclude=["vocab"])
        serializers["vocab"] = lambda p: self.vocab.to_disk(p)
        util.to_disk(path, serializers, exclude)

    def from_disk(
        self, path: Union[str, Path], exclude: Iterable[str] = tuple()
    ) -> "Language":
        """Loads state from a directory. Modifies the object in place and
        returns it. If the saved `Language` object contains a model, the
        model will be loaded.

        path (str / Path): A path to a directory.
        exclude (list): Names of components or serialization fields to exclude.
        RETURNS (Language): The modified `Language` object.

        DOCS: https://spacy.io/api/language#from_disk
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
            _fix_pretrained_vectors_name(self)

        path = util.ensure_path(path)

        deserializers = {}
        if Path(path / "config.cfg").exists():
            deserializers["config.cfg"] = lambda p: self.config.from_disk(p)
        deserializers["meta.json"] = deserialize_meta
        deserializers["vocab"] = deserialize_vocab
        deserializers["tokenizer"] = lambda p: self.tokenizer.from_disk(
            p, exclude=["vocab"]
        )
        for name, proc in self.pipeline:
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

    def to_bytes(self, exclude: Iterable[str] = tuple()) -> bytes:
        """Serialize the current state to a binary string.

        exclude (list): Names of components or serialization fields to exclude.
        RETURNS (bytes): The serialized form of the `Language` object.

        DOCS: https://spacy.io/api/language#to_bytes
        """
        serializers = {}
        serializers["vocab"] = lambda: self.vocab.to_bytes()
        serializers["tokenizer"] = lambda: self.tokenizer.to_bytes(exclude=["vocab"])
        serializers["meta.json"] = lambda: srsly.json_dumps(self.meta)
        serializers["config.cfg"] = lambda: self.config.to_bytes()
        for name, proc in self.pipeline:
            if name in exclude:
                continue
            if not hasattr(proc, "to_bytes"):
                continue
            serializers[name] = lambda proc=proc: proc.to_bytes(exclude=["vocab"])
        return util.to_bytes(serializers, exclude)

    def from_bytes(
        self, bytes_data: bytes, exclude: Iterable[str] = tuple()
    ) -> "Language":
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        exclude (list): Names of components or serialization fields to exclude.
        RETURNS (Language): The `Language` object.

        DOCS: https://spacy.io/api/language#from_bytes
        """

        def deserialize_meta(b):
            data = srsly.json_loads(b)
            self.meta.update(data)
            # self.meta always overrides meta["vectors"] with the metadata
            # from self.vocab.vectors, so set the name directly
            self.vocab.vectors.name = data.get("vectors", {}).get("name")

        def deserialize_vocab(b):
            self.vocab.from_bytes(b)
            _fix_pretrained_vectors_name(self)

        deserializers = {}
        deserializers["config.cfg"] = lambda b: self.config.from_bytes(b)
        deserializers["meta.json"] = deserialize_meta
        deserializers["vocab"] = deserialize_vocab
        deserializers["tokenizer"] = lambda b: self.tokenizer.from_bytes(
            b, exclude=["vocab"]
        )
        for name, proc in self.pipeline:
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
    factory: str
    default_config: Optional[Dict[str, Any]] = None  # noqa: E704
    assigns: Iterable[str] = tuple()
    requires: Iterable[str] = tuple()
    retokenizes: bool = False


def _fix_pretrained_vectors_name(nlp: Language) -> None:
    # TODO: Replace this once we handle vectors consistently as static
    # data
    if "vectors" in nlp.meta and "name" in nlp.meta["vectors"]:
        nlp.vocab.vectors.name = nlp.meta["vectors"]["name"]
    elif not nlp.vocab.vectors.size:
        nlp.vocab.vectors.name = None
    elif "name" in nlp.meta and "lang" in nlp.meta:
        vectors_name = f"{nlp.meta['lang']}_{nlp.meta['name']}.vectors"
        nlp.vocab.vectors.name = vectors_name
    else:
        raise ValueError(Errors.E092)
    if nlp.vocab.vectors.size != 0:
        link_vectors_to_models(nlp.vocab)
    for name, proc in nlp.pipeline:
        if not hasattr(proc, "cfg"):
            continue
        proc.cfg.setdefault("deprecation_fixes", {})
        proc.cfg["deprecation_fixes"]["vectors_name"] = nlp.vocab.vectors.name


class DisabledPipes(list):
    """Manager for temporary pipeline disabling."""

    def __init__(self, nlp: Language, names: List[str]):
        self.nlp = nlp
        self.names = names
        # Important! Not deep copy -- we just want the container (but we also
        # want to support people providing arbitrarily typed nlp.pipeline
        # objects.)
        self.original_pipeline = copy(nlp.pipeline)
        self.metas = {name: nlp.get_pipe_meta(name) for name in names}
        self.configs = {name: nlp.get_pipe_config(name) for name in names}
        list.__init__(self)
        self.extend(nlp.remove_pipe(name) for name in names)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.restore()

    def restore(self):
        """Restore the pipeline to its state when DisabledPipes was created."""
        current, self.nlp.pipeline = self.nlp.pipeline, self.original_pipeline
        unexpected = [name for name, pipe in current if not self.nlp.has_pipe(name)]
        if unexpected:
            # Don't change the pipeline if we're raising an error.
            self.nlp.pipeline = current
            raise ValueError(Errors.E008.format(names=unexpected))
        self.nlp._pipe_meta.update(self.metas)
        self.nlp._pipe_configs.update(self.configs)
        self[:] = []


def _pipe(examples, proc, kwargs):
    # We added some args for pipe that __call__ doesn't expect.
    kwargs = dict(kwargs)
    for arg in ["batch_size"]:
        if arg in kwargs:
            kwargs.pop(arg)
    for eg in examples:
        eg = proc(eg, **kwargs)
        yield eg


def _apply_pipes(make_doc, pipes, receiver, sender, underscore_state):
    """Worker for Language.pipe

    receiver (multiprocessing.Connection): Pipe to receive text. Usually
        created by `multiprocessing.Pipe()`
    sender (multiprocessing.Connection): Pipe to send doc. Usually created by
        `multiprocessing.Pipe()`
    underscore_state (tuple): The data in the Underscore class of the parent
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

    def __init__(self, data, queues, chunk_size):
        self.data = iter(data)
        self.queues = iter(cycle(queues))
        self.chunk_size = chunk_size
        self.count = 0

    def send(self):
        """Send chunk_size items from self.data to channels."""
        for item, q in itertools.islice(
            zip(self.data, cycle(self.queues)), self.chunk_size
        ):
            # cycle channels so that distribute the texts evenly
            q.put(item)

    def step(self):
        """Tell sender that comsumed one item.

        Data is sent to the workers after every chunk_size calls."""
        self.count += 1
        if self.count >= self.chunk_size:
            self.count = 0
            self.send()
