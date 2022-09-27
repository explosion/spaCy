from typing import List, Mapping, NoReturn, Union, Dict, Any, Set, cast
from typing import Optional, Iterable, Callable, Tuple, Type
from typing import Iterator, Pattern, Generator, TYPE_CHECKING
from types import ModuleType
import os
import importlib
import importlib.util
import re
from pathlib import Path
import thinc
from thinc.api import NumpyOps, get_current_ops, Adam, Config, Optimizer
from thinc.api import ConfigValidationError, Model
import functools
import itertools
import numpy
import srsly
import catalogue
from catalogue import RegistryError, Registry
import langcodes
import sys
import warnings
from packaging.specifiers import SpecifierSet, InvalidSpecifier
from packaging.version import Version, InvalidVersion
from packaging.requirements import Requirement
import subprocess
from contextlib import contextmanager
from collections import defaultdict
import tempfile
import shutil
import shlex
import inspect
import pkgutil
import logging

try:
    import cupy.random
except ImportError:
    cupy = None

# These are functions that were previously (v2.x) available from spacy.util
# and have since moved to Thinc. We're importing them here so people's code
# doesn't break, but they should always be imported from Thinc from now on,
# not from spacy.util.
from thinc.api import fix_random_seed, compounding, decaying  # noqa: F401


from .symbols import ORTH
from .compat import cupy, CudaStream, is_windows, importlib_metadata
from .errors import Errors, Warnings, OLD_MODEL_SHORTCUTS
from . import about

if TYPE_CHECKING:
    # This lets us add type hints for mypy etc. without causing circular imports
    from .language import Language  # noqa: F401
    from .pipeline import Pipe  # noqa: F401
    from .tokens import Doc, Span  # noqa: F401
    from .vocab import Vocab  # noqa: F401


# fmt: off
OOV_RANK = numpy.iinfo(numpy.uint64).max
DEFAULT_OOV_PROB = -20
LEXEME_NORM_LANGS = ["cs", "da", "de", "el", "en", "id", "lb", "mk", "pt", "ru", "sr", "ta", "th"]

# Default order of sections in the config file. Not all sections needs to exist,
# and additional sections are added at the end, in alphabetical order.
CONFIG_SECTION_ORDER = ["paths", "variables", "system", "nlp", "components", "corpora", "training", "pretraining", "initialize"]
# fmt: on

logger = logging.getLogger("spacy")
logger_stream_handler = logging.StreamHandler()
logger_stream_handler.setFormatter(
    logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
)
logger.addHandler(logger_stream_handler)


class ENV_VARS:
    CONFIG_OVERRIDES = "SPACY_CONFIG_OVERRIDES"
    PROJECT_USE_GIT_VERSION = "SPACY_PROJECT_USE_GIT_VERSION"


class registry(thinc.registry):
    languages = catalogue.create("spacy", "languages", entry_points=True)
    architectures = catalogue.create("spacy", "architectures", entry_points=True)
    tokenizers = catalogue.create("spacy", "tokenizers", entry_points=True)
    lemmatizers = catalogue.create("spacy", "lemmatizers", entry_points=True)
    lookups = catalogue.create("spacy", "lookups", entry_points=True)
    displacy_colors = catalogue.create("spacy", "displacy_colors", entry_points=True)
    misc = catalogue.create("spacy", "misc", entry_points=True)
    # Callback functions used to manipulate nlp object etc.
    callbacks = catalogue.create("spacy", "callbacks", entry_points=True)
    batchers = catalogue.create("spacy", "batchers", entry_points=True)
    readers = catalogue.create("spacy", "readers", entry_points=True)
    augmenters = catalogue.create("spacy", "augmenters", entry_points=True)
    loggers = catalogue.create("spacy", "loggers", entry_points=True)
    scorers = catalogue.create("spacy", "scorers", entry_points=True)
    # These are factories registered via third-party packages and the
    # spacy_factories entry point. This registry only exists so we can easily
    # load them via the entry points. The "true" factories are added via the
    # Language.factory decorator (in the spaCy code base and user code) and those
    # are the factories used to initialize components via registry.resolve.
    _entry_point_factories = catalogue.create("spacy", "factories", entry_points=True)
    factories = catalogue.create("spacy", "internal_factories")
    # This is mostly used to get a list of all installed models in the current
    # environment. spaCy models packaged with `spacy package` will "advertise"
    # themselves via entry points.
    models = catalogue.create("spacy", "models", entry_points=True)
    cli = catalogue.create("spacy", "cli", entry_points=True)

    @classmethod
    def get_registry_names(cls) -> List[str]:
        """List all available registries."""
        names = []
        for name, value in inspect.getmembers(cls):
            if not name.startswith("_") and isinstance(value, Registry):
                names.append(name)
        return sorted(names)

    @classmethod
    def get(cls, registry_name: str, func_name: str) -> Callable:
        """Get a registered function from the registry."""
        # We're overwriting this classmethod so we're able to provide more
        # specific error messages and implement a fallback to spacy-legacy.
        if not hasattr(cls, registry_name):
            names = ", ".join(cls.get_registry_names()) or "none"
            raise RegistryError(Errors.E892.format(name=registry_name, available=names))
        reg = getattr(cls, registry_name)
        try:
            func = reg.get(func_name)
        except RegistryError:
            if func_name.startswith("spacy."):
                legacy_name = func_name.replace("spacy.", "spacy-legacy.")
                try:
                    return reg.get(legacy_name)
                except catalogue.RegistryError:
                    pass
            available = ", ".join(sorted(reg.get_all().keys())) or "none"
            raise RegistryError(
                Errors.E893.format(
                    name=func_name, reg_name=registry_name, available=available
                )
            ) from None
        return func

    @classmethod
    def find(cls, registry_name: str, func_name: str) -> Callable:
        """Get info about a registered function from the registry."""
        # We're overwriting this classmethod so we're able to provide more
        # specific error messages and implement a fallback to spacy-legacy.
        if not hasattr(cls, registry_name):
            names = ", ".join(cls.get_registry_names()) or "none"
            raise RegistryError(Errors.E892.format(name=registry_name, available=names))
        reg = getattr(cls, registry_name)
        try:
            func_info = reg.find(func_name)
        except RegistryError:
            if func_name.startswith("spacy."):
                legacy_name = func_name.replace("spacy.", "spacy-legacy.")
                try:
                    return reg.find(legacy_name)
                except catalogue.RegistryError:
                    pass
            available = ", ".join(sorted(reg.get_all().keys())) or "none"
            raise RegistryError(
                Errors.E893.format(
                    name=func_name, reg_name=registry_name, available=available
                )
            ) from None
        return func_info

    @classmethod
    def has(cls, registry_name: str, func_name: str) -> bool:
        """Check whether a function is available in a registry."""
        if not hasattr(cls, registry_name):
            return False
        reg = getattr(cls, registry_name)
        if func_name.startswith("spacy."):
            legacy_name = func_name.replace("spacy.", "spacy-legacy.")
            return func_name in reg or legacy_name in reg
        return func_name in reg


class SimpleFrozenDict(dict):
    """Simplified implementation of a frozen dict, mainly used as default
    function or method argument (for arguments that should default to empty
    dictionary). Will raise an error if user or spaCy attempts to add to dict.
    """

    def __init__(self, *args, error: str = Errors.E095, **kwargs) -> None:
        """Initialize the frozen dict. Can be initialized with pre-defined
        values.

        error (str): The error message when user tries to assign to dict.
        """
        super().__init__(*args, **kwargs)
        self.error = error

    def __setitem__(self, key, value):
        raise NotImplementedError(self.error)

    def pop(self, key, default=None):
        raise NotImplementedError(self.error)

    def update(self, other):
        raise NotImplementedError(self.error)


class SimpleFrozenList(list):
    """Wrapper class around a list that lets us raise custom errors if certain
    attributes/methods are accessed. Mostly used for properties like
    Language.pipeline that return an immutable list (and that we don't want to
    convert to a tuple to not break too much backwards compatibility). If a user
    accidentally calls nlp.pipeline.append(), we can raise a more helpful error.
    """

    def __init__(self, *args, error: str = Errors.E927) -> None:
        """Initialize the frozen list.

        error (str): The error message when user tries to mutate the list.
        """
        self.error = error
        super().__init__(*args)

    def append(self, *args, **kwargs):
        raise NotImplementedError(self.error)

    def clear(self, *args, **kwargs):
        raise NotImplementedError(self.error)

    def extend(self, *args, **kwargs):
        raise NotImplementedError(self.error)

    def insert(self, *args, **kwargs):
        raise NotImplementedError(self.error)

    def pop(self, *args, **kwargs):
        raise NotImplementedError(self.error)

    def remove(self, *args, **kwargs):
        raise NotImplementedError(self.error)

    def reverse(self, *args, **kwargs):
        raise NotImplementedError(self.error)

    def sort(self, *args, **kwargs):
        raise NotImplementedError(self.error)


def lang_class_is_loaded(lang: str) -> bool:
    """Check whether a Language class is already loaded. Language classes are
    loaded lazily, to avoid expensive setup code associated with the language
    data.

    lang (str): Two-letter language code, e.g. 'en'.
    RETURNS (bool): Whether a Language class has been loaded.
    """
    return lang in registry.languages


def find_matching_language(lang: str) -> Optional[str]:
    """
    Given an IETF language code, find a supported spaCy language that is a
    close match for it (according to Unicode CLDR language-matching rules).
    This allows for language aliases, ISO 639-2 codes, more detailed language
    tags, and close matches.

    Returns the language code if a matching language is available, or None
    if there is no matching language.

    >>> find_matching_language('en')
    'en'
    >>> find_matching_language('pt-BR')  # Brazilian Portuguese
    'pt'
    >>> find_matching_language('fra')  # an ISO 639-2 code for French
    'fr'
    >>> find_matching_language('iw')  # obsolete alias for Hebrew
    'he'
    >>> find_matching_language('no')  # Norwegian
    'nb'
    >>> find_matching_language('mo')  # old code for ro-MD
    'ro'
    >>> find_matching_language('zh-Hans')  # Simplified Chinese
    'zh'
    >>> find_matching_language('zxx')
    None
    """
    import spacy.lang  # noqa: F401

    if lang == "xx":
        return "xx"

    # Find out which language modules we have
    possible_languages = []
    for modinfo in pkgutil.iter_modules(spacy.lang.__path__):  # type: ignore[attr-defined]
        code = modinfo.name
        if code == "xx":
            # Temporarily make 'xx' into a valid language code
            possible_languages.append("mul")
        elif langcodes.tag_is_valid(code):
            possible_languages.append(code)

    # Distances from 1-9 allow near misses like Bosnian -> Croatian and
    # Norwegian -> Norwegian Bokmål. A distance of 10 would include several
    # more possibilities, like variants of Chinese like 'wuu', but text that
    # is labeled that way is probably trying to be distinct from 'zh' and
    # shouldn't automatically match.
    match = langcodes.closest_supported_match(lang, possible_languages, max_distance=9)
    if match == "mul":
        # Convert 'mul' back to spaCy's 'xx'
        return "xx"
    else:
        return match


def get_lang_class(lang: str) -> Type["Language"]:
    """Import and load a Language class.

    lang (str): IETF language code, such as 'en'.
    RETURNS (Language): Language class.
    """
    # Check if language is registered / entry point is available
    if lang in registry.languages:
        return registry.languages.get(lang)
    else:
        # Find the language in the spacy.lang subpackage
        try:
            module = importlib.import_module(f".lang.{lang}", "spacy")
        except ImportError as err:
            # Find a matching language. For example, if the language 'no' is
            # requested, we can use language-matching to load `spacy.lang.nb`.
            try:
                match = find_matching_language(lang)
            except langcodes.tag_parser.LanguageTagError:
                # proceed to raising an import error
                match = None

            if match:
                lang = match
                module = importlib.import_module(f".lang.{lang}", "spacy")
            else:
                raise ImportError(Errors.E048.format(lang=lang, err=err)) from err
        set_lang_class(lang, getattr(module, module.__all__[0]))  # type: ignore[attr-defined]
    return registry.languages.get(lang)


def set_lang_class(name: str, cls: Type["Language"]) -> None:
    """Set a custom Language class name that can be loaded via get_lang_class.

    name (str): Name of Language class.
    cls (Language): Language class.
    """
    registry.languages.register(name, func=cls)


def ensure_path(path: Any) -> Any:
    """Ensure string is converted to a Path.

    path (Any): Anything. If string, it's converted to Path.
    RETURNS: Path or original argument.
    """
    if isinstance(path, str):
        return Path(path)
    else:
        return path


def load_language_data(path: Union[str, Path]) -> Union[dict, list]:
    """Load JSON language data using the given path as a base. If the provided
    path isn't present, will attempt to load a gzipped version before giving up.

    path (str / Path): The data to load.
    RETURNS: The loaded data.
    """
    path = ensure_path(path)
    if path.exists():
        return srsly.read_json(path)
    path = path.with_suffix(path.suffix + ".gz")
    if path.exists():
        return srsly.read_gzip_json(path)
    raise ValueError(Errors.E160.format(path=path))


def get_module_path(module: ModuleType) -> Path:
    """Get the path of a Python module.

    module (ModuleType): The Python module.
    RETURNS (Path): The path.
    """
    if not hasattr(module, "__module__"):
        raise ValueError(Errors.E169.format(module=repr(module)))
    file_path = Path(cast(os.PathLike, sys.modules[module.__module__].__file__))
    return file_path.parent


# Default value for passed enable/disable values.
_DEFAULT_EMPTY_PIPES = SimpleFrozenList()


def load_model(
    name: Union[str, Path],
    *,
    vocab: Union["Vocab", bool] = True,
    disable: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    enable: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    exclude: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    config: Union[Dict[str, Any], Config] = SimpleFrozenDict(),
) -> "Language":
    """Load a model from a package or data path.

    name (str): Package name or model path.
    vocab (Vocab / True): Optional vocab to pass in on initialization. If True,
        a new Vocab object will be created.
    disable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to disable.
    enable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to enable. All others will be disabled.
    exclude (Union[str, Iterable[str]]):  Name(s) of pipeline component(s) to exclude.
    config (Dict[str, Any] / Config): Config overrides as nested dict or dict
        keyed by section values in dot notation.
    RETURNS (Language): The loaded nlp object.
    """
    kwargs = {
        "vocab": vocab,
        "disable": disable,
        "enable": enable,
        "exclude": exclude,
        "config": config,
    }
    if isinstance(name, str):  # name or string path
        if name.startswith("blank:"):  # shortcut for blank model
            return get_lang_class(name.replace("blank:", ""))()
        if is_package(name):  # installed as package
            return load_model_from_package(name, **kwargs)  # type: ignore[arg-type]
        if Path(name).exists():  # path to model data directory
            return load_model_from_path(Path(name), **kwargs)  # type: ignore[arg-type]
    elif hasattr(name, "exists"):  # Path or Path-like to model data
        return load_model_from_path(name, **kwargs)  # type: ignore[arg-type]
    if name in OLD_MODEL_SHORTCUTS:
        raise IOError(Errors.E941.format(name=name, full=OLD_MODEL_SHORTCUTS[name]))  # type: ignore[index]
    raise IOError(Errors.E050.format(name=name))


def load_model_from_package(
    name: str,
    *,
    vocab: Union["Vocab", bool] = True,
    disable: Union[str, Iterable[str]] = SimpleFrozenList(),
    enable: Union[str, Iterable[str]] = SimpleFrozenList(),
    exclude: Union[str, Iterable[str]] = SimpleFrozenList(),
    config: Union[Dict[str, Any], Config] = SimpleFrozenDict(),
) -> "Language":
    """Load a model from an installed package.

    name (str): The package name.
    vocab (Vocab / True): Optional vocab to pass in on initialization. If True,
        a new Vocab object will be created.
    disable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to disable. Disabled
        pipes will be loaded but they won't be run unless you explicitly
        enable them by calling nlp.enable_pipe.
    enable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to enable. All other
        pipes will be disabled (and can be enabled using `nlp.enable_pipe`).
    exclude (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to exclude. Excluded
        components won't be loaded.
    config (Dict[str, Any] / Config): Config overrides as nested dict or dict
        keyed by section values in dot notation.
    RETURNS (Language): The loaded nlp object.
    """
    cls = importlib.import_module(name)
    return cls.load(vocab=vocab, disable=disable, enable=enable, exclude=exclude, config=config)  # type: ignore[attr-defined]


def load_model_from_path(
    model_path: Path,
    *,
    meta: Optional[Dict[str, Any]] = None,
    vocab: Union["Vocab", bool] = True,
    disable: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    enable: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    exclude: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    config: Union[Dict[str, Any], Config] = SimpleFrozenDict(),
) -> "Language":
    """Load a model from a data directory path. Creates Language class with
    pipeline from config.cfg and then calls from_disk() with path.

    model_path (Path): Model path.
    meta (Dict[str, Any]): Optional model meta.
    vocab (Vocab / True): Optional vocab to pass in on initialization. If True,
        a new Vocab object will be created.
    disable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to disable. Disabled
        pipes will be loaded but they won't be run unless you explicitly
        enable them by calling nlp.enable_pipe.
    enable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to enable. All other
        pipes will be disabled (and can be enabled using `nlp.enable_pipe`).
    exclude (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to exclude. Excluded
        components won't be loaded.
    config (Dict[str, Any] / Config): Config overrides as nested dict or dict
        keyed by section values in dot notation.
    RETURNS (Language): The loaded nlp object.
    """
    if not model_path.exists():
        raise IOError(Errors.E052.format(path=model_path))
    if not meta:
        meta = get_model_meta(model_path)
    config_path = model_path / "config.cfg"
    overrides = dict_to_dot(config)
    config = load_config(config_path, overrides=overrides)
    nlp = load_model_from_config(
        config,
        vocab=vocab,
        disable=disable,
        enable=enable,
        exclude=exclude,
        meta=meta,
    )
    return nlp.from_disk(model_path, exclude=exclude, overrides=overrides)


def load_model_from_config(
    config: Union[Dict[str, Any], Config],
    *,
    meta: Dict[str, Any] = SimpleFrozenDict(),
    vocab: Union["Vocab", bool] = True,
    disable: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    enable: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    exclude: Union[str, Iterable[str]] = _DEFAULT_EMPTY_PIPES,
    auto_fill: bool = False,
    validate: bool = True,
) -> "Language":
    """Create an nlp object from a config. Expects the full config file including
    a section "nlp" containing the settings for the nlp object.

    name (str): Package name or model path.
    meta (Dict[str, Any]): Optional model meta.
    vocab (Vocab / True): Optional vocab to pass in on initialization. If True,
        a new Vocab object will be created.
    disable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to disable. Disabled
        pipes will be loaded but they won't be run unless you explicitly
        enable them by calling nlp.enable_pipe.
    enable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to enable. All other
        pipes will be disabled (and can be enabled using `nlp.enable_pipe`).
    exclude (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to exclude. Excluded
        components won't be loaded.
    auto_fill (bool): Whether to auto-fill config with missing defaults.
    validate (bool): Whether to show config validation errors.
    RETURNS (Language): The loaded nlp object.
    """
    if "nlp" not in config:
        raise ValueError(Errors.E985.format(config=config))
    nlp_config = config["nlp"]
    if "lang" not in nlp_config or nlp_config["lang"] is None:
        raise ValueError(Errors.E993.format(config=nlp_config))
    # This will automatically handle all codes registered via the languages
    # registry, including custom subclasses provided via entry points
    lang_cls = get_lang_class(nlp_config["lang"])
    nlp = lang_cls.from_config(
        config,
        vocab=vocab,
        disable=disable,
        enable=enable,
        exclude=exclude,
        auto_fill=auto_fill,
        validate=validate,
        meta=meta,
    )
    return nlp


def get_sourced_components(
    config: Union[Dict[str, Any], Config]
) -> Dict[str, Dict[str, Any]]:
    """RETURNS (List[str]): All sourced components in the original config,
    e.g. {"source": "en_core_web_sm"}. If the config contains a key
    "factory", we assume it refers to a component factory.
    """
    return {
        name: cfg
        for name, cfg in config.get("components", {}).items()
        if "factory" not in cfg and "source" in cfg
    }


def resolve_dot_names(
    config: Config, dot_names: List[Optional[str]]
) -> Tuple[Any, ...]:
    """Resolve one or more "dot notation" names, e.g. corpora.train.
    The paths could point anywhere into the config, so we don't know which
    top-level section we'll be looking within.

    We resolve the whole top-level section, although we could resolve less --
    we could find the lowest part of the tree.
    """
    # TODO: include schema?
    resolved = {}
    output: List[Any] = []
    errors = []
    for name in dot_names:
        if name is None:
            output.append(name)
        else:
            section = name.split(".")[0]
            # We want to avoid resolving the same thing twice
            if section not in resolved:
                if registry.is_promise(config[section]):
                    # Otherwise we can't resolve [corpus] if it's a promise
                    result = registry.resolve({"config": config[section]})["config"]
                else:
                    result = registry.resolve(config[section])
                resolved[section] = result
            try:
                output.append(dot_to_object(resolved, name))  # type: ignore[arg-type]
            except KeyError:
                msg = f"not a valid section reference: {name}"
                errors.append({"loc": name.split("."), "msg": msg})
    if errors:
        raise ConfigValidationError(config=config, errors=errors)
    return tuple(output)


def load_model_from_init_py(
    init_file: Union[Path, str],
    *,
    vocab: Union["Vocab", bool] = True,
    disable: Union[str, Iterable[str]] = SimpleFrozenList(),
    enable: Union[str, Iterable[str]] = SimpleFrozenList(),
    exclude: Union[str, Iterable[str]] = SimpleFrozenList(),
    config: Union[Dict[str, Any], Config] = SimpleFrozenDict(),
) -> "Language":
    """Helper function to use in the `load()` method of a model package's
    __init__.py.

    vocab (Vocab / True): Optional vocab to pass in on initialization. If True,
        a new Vocab object will be created.
    disable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to disable. Disabled
        pipes will be loaded but they won't be run unless you explicitly
        enable them by calling nlp.enable_pipe.
    enable (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to enable. All other
        pipes will be disabled (and can be enabled using `nlp.enable_pipe`).
    exclude (Union[str, Iterable[str]]): Name(s) of pipeline component(s) to exclude. Excluded
        components won't be loaded.
    config (Dict[str, Any] / Config): Config overrides as nested dict or dict
        keyed by section values in dot notation.
    RETURNS (Language): The loaded nlp object.
    """
    model_path = Path(init_file).parent
    meta = get_model_meta(model_path)
    data_dir = f"{meta['lang']}_{meta['name']}-{meta['version']}"
    data_path = model_path / data_dir
    if not model_path.exists():
        raise IOError(Errors.E052.format(path=data_path))
    return load_model_from_path(
        data_path,
        vocab=vocab,
        meta=meta,
        disable=disable,
        enable=enable,
        exclude=exclude,
        config=config,
    )


def load_config(
    path: Union[str, Path],
    overrides: Dict[str, Any] = SimpleFrozenDict(),
    interpolate: bool = False,
) -> Config:
    """Load a config file. Takes care of path validation and section order.

    path (Union[str, Path]): Path to the config file or "-" to read from stdin.
    overrides: (Dict[str, Any]): Config overrides as nested dict or
        dict keyed by section values in dot notation.
    interpolate (bool): Whether to interpolate and resolve variables.
    RETURNS (Config): The loaded config.
    """
    config_path = ensure_path(path)
    config = Config(section_order=CONFIG_SECTION_ORDER)
    if str(config_path) == "-":  # read from standard input
        return config.from_str(
            sys.stdin.read(), overrides=overrides, interpolate=interpolate
        )
    else:
        if not config_path or not config_path.is_file():
            raise IOError(Errors.E053.format(path=config_path, name="config file"))
        return config.from_disk(
            config_path, overrides=overrides, interpolate=interpolate
        )


def load_config_from_str(
    text: str, overrides: Dict[str, Any] = SimpleFrozenDict(), interpolate: bool = False
):
    """Load a full config from a string. Wrapper around Thinc's Config.from_str.

    text (str): The string config to load.
    interpolate (bool): Whether to interpolate and resolve variables.
    RETURNS (Config): The loaded config.
    """
    return Config(section_order=CONFIG_SECTION_ORDER).from_str(
        text, overrides=overrides, interpolate=interpolate
    )


def get_installed_models() -> List[str]:
    """List all model packages currently installed in the environment.

    RETURNS (List[str]): The string names of the models.
    """
    return list(registry.models.get_all().keys())


def get_package_version(name: str) -> Optional[str]:
    """Get the version of an installed package. Typically used to get model
    package versions.

    name (str): The name of the installed Python package.
    RETURNS (str / None): The version or None if package not installed.
    """
    try:
        return importlib_metadata.version(name)  # type: ignore[attr-defined]
    except importlib_metadata.PackageNotFoundError:  # type: ignore[attr-defined]
        return None


def is_compatible_version(
    version: str, constraint: str, prereleases: bool = True
) -> Optional[bool]:
    """Check if a version (e.g. "2.0.0") is compatible given a version
    constraint (e.g. ">=1.9.0,<2.2.1"). If the constraint is a specific version,
    it's interpreted as =={version}.

    version (str): The version to check.
    constraint (str): The constraint string.
    prereleases (bool): Whether to allow prereleases. If set to False,
        prerelease versions will be considered incompatible.
    RETURNS (bool / None): Whether the version is compatible, or None if the
        version or constraint are invalid.
    """
    # Handle cases where exact version is provided as constraint
    if constraint[0].isdigit():
        constraint = f"=={constraint}"
    try:
        spec = SpecifierSet(constraint)
        version = Version(version)  # type: ignore[assignment]
    except (InvalidSpecifier, InvalidVersion):
        return None
    spec.prereleases = prereleases
    return version in spec


def is_unconstrained_version(
    constraint: str, prereleases: bool = True
) -> Optional[bool]:
    # We have an exact version, this is the ultimate constrained version
    if constraint[0].isdigit():
        return False
    try:
        spec = SpecifierSet(constraint)
    except InvalidSpecifier:
        return None
    spec.prereleases = prereleases
    specs = [sp for sp in spec]
    # We only have one version spec and it defines > or >=
    if len(specs) == 1 and specs[0].operator in (">", ">="):
        return True
    # One specifier is exact version
    if any(sp.operator in ("==") for sp in specs):
        return False
    has_upper = any(sp.operator in ("<", "<=") for sp in specs)
    has_lower = any(sp.operator in (">", ">=") for sp in specs)
    # We have a version spec that defines an upper and lower bound
    if has_upper and has_lower:
        return False
    # Everything else, like only an upper version, only a lower version etc.
    return True


def split_requirement(requirement: str) -> Tuple[str, str]:
    """Split a requirement like spacy>=1.2.3 into ("spacy", ">=1.2.3")."""
    req = Requirement(requirement)
    return (req.name, str(req.specifier))


def get_minor_version_range(version: str) -> str:
    """Generate a version range like >=1.2.3,<1.3.0 based on a given version
    (e.g. of spaCy).
    """
    release = Version(version).release
    return f">={version},<{release[0]}.{release[1] + 1}.0"


def get_model_lower_version(constraint: str) -> Optional[str]:
    """From a version range like >=1.2.3,<1.3.0 return the lower pin."""
    try:
        specset = SpecifierSet(constraint)
        for spec in specset:
            if spec.operator in (">=", "==", "~="):
                return spec.version
    except Exception:
        pass
    return None


def is_prerelease_version(version: str) -> bool:
    """Check whether a version is a prerelease version.

    version (str): The version, e.g. "3.0.0.dev1".
    RETURNS (bool): Whether the version is a prerelease version.
    """
    return Version(version).is_prerelease


def get_base_version(version: str) -> str:
    """Generate the base version without any prerelease identifiers.

    version (str): The version, e.g. "3.0.0.dev1".
    RETURNS (str): The base version, e.g. "3.0.0".
    """
    return Version(version).base_version


def get_minor_version(version: str) -> Optional[str]:
    """Get the major + minor version (without patch or prerelease identifiers).

    version (str): The version.
    RETURNS (str): The major + minor version or None if version is invalid.
    """
    try:
        v = Version(version)
    except (TypeError, InvalidVersion):
        return None
    return f"{v.major}.{v.minor}"


def is_minor_version_match(version_a: str, version_b: str) -> bool:
    """Compare two versions and check if they match in major and minor, without
    patch or prerelease identifiers. Used internally for compatibility checks
    that should be insensitive to patch releases.

    version_a (str): The first version
    version_b (str): The second version.
    RETURNS (bool): Whether the versions match.
    """
    a = get_minor_version(version_a)
    b = get_minor_version(version_b)
    return a is not None and b is not None and a == b


def load_meta(path: Union[str, Path]) -> Dict[str, Any]:
    """Load a model meta.json from a path and validate its contents.

    path (Union[str, Path]): Path to meta.json.
    RETURNS (Dict[str, Any]): The loaded meta.
    """
    path = ensure_path(path)
    if not path.parent.exists():
        raise IOError(Errors.E052.format(path=path.parent))
    if not path.exists() or not path.is_file():
        raise IOError(Errors.E053.format(path=path.parent, name="meta.json"))
    meta = srsly.read_json(path)
    for setting in ["lang", "name", "version"]:
        if setting not in meta or not meta[setting]:
            raise ValueError(Errors.E054.format(setting=setting))
    if "spacy_version" in meta:
        if not is_compatible_version(about.__version__, meta["spacy_version"]):
            lower_version = get_model_lower_version(meta["spacy_version"])
            lower_version = get_minor_version(lower_version)  # type: ignore[arg-type]
            if lower_version is not None:
                lower_version = "v" + lower_version
            elif "spacy_git_version" in meta:
                lower_version = "git commit " + meta["spacy_git_version"]
            else:
                lower_version = "version unknown"
            warn_msg = Warnings.W095.format(
                model=f"{meta['lang']}_{meta['name']}",
                model_version=meta["version"],
                version=lower_version,
                current=about.__version__,
            )
            warnings.warn(warn_msg)
        if is_unconstrained_version(meta["spacy_version"]):
            warn_msg = Warnings.W094.format(
                model=f"{meta['lang']}_{meta['name']}",
                model_version=meta["version"],
                version=meta["spacy_version"],
                example=get_minor_version_range(about.__version__),
            )
            warnings.warn(warn_msg)
    return meta


def get_model_meta(path: Union[str, Path]) -> Dict[str, Any]:
    """Get model meta.json from a directory path and validate its contents.

    path (str / Path): Path to model directory.
    RETURNS (Dict[str, Any]): The model's meta data.
    """
    model_path = ensure_path(path)
    return load_meta(model_path / "meta.json")


def is_package(name: str) -> bool:
    """Check if string maps to a package installed via pip.

    name (str): Name of package.
    RETURNS (bool): True if installed package, False if not.
    """
    try:
        importlib_metadata.distribution(name)  # type: ignore[attr-defined]
        return True
    except:  # noqa: E722
        return False


def get_package_path(name: str) -> Path:
    """Get the path to an installed package.

    name (str): Package name.
    RETURNS (Path): Path to installed package.
    """
    # Here we're importing the module just to find it. This is worryingly
    # indirect, but it's otherwise very difficult to find the package.
    pkg = importlib.import_module(name)
    return Path(cast(Union[str, os.PathLike], pkg.__file__)).parent


def replace_model_node(model: Model, target: Model, replacement: Model) -> None:
    """Replace a node within a model with a new one, updating refs.

    model (Model): The parent model.
    target (Model): The target node.
    replacement (Model): The node to replace the target with.
    """
    # Place the node into the sublayers
    for node in model.walk():
        if target in node.layers:
            node.layers[node.layers.index(target)] = replacement
    # Now fix any node references
    for node in model.walk():
        for ref_name in node.ref_names:
            if node.maybe_get_ref(ref_name) is target:
                node.set_ref(ref_name, replacement)


def split_command(command: str) -> List[str]:
    """Split a string command using shlex. Handles platform compatibility.

    command (str) : The command to split
    RETURNS (List[str]): The split command.
    """
    return shlex.split(command, posix=not is_windows)


def join_command(command: List[str]) -> str:
    """Join a command using shlex. shlex.join is only available for Python 3.8+,
    so we're using a workaround here.

    command (List[str]): The command to join.
    RETURNS (str): The joined command
    """
    return " ".join(shlex.quote(cmd) for cmd in command)


def run_command(
    command: Union[str, List[str]],
    *,
    stdin: Optional[Any] = None,
    capture: bool = False,
) -> subprocess.CompletedProcess:
    """Run a command on the command line as a subprocess. If the subprocess
    returns a non-zero exit code, a system exit is performed.

    command (str / List[str]): The command. If provided as a string, the
        string will be split using shlex.split.
    stdin (Optional[Any]): stdin to read from or None.
    capture (bool): Whether to capture the output and errors. If False,
        the stdout and stderr will not be redirected, and if there's an error,
        sys.exit will be called with the return code. You should use capture=False
        when you want to turn over execution to the command, and capture=True
        when you want to run the command more like a function.
    RETURNS (Optional[CompletedProcess]): The process object.
    """
    if isinstance(command, str):
        cmd_list = split_command(command)
        cmd_str = command
    else:
        cmd_list = command
        cmd_str = " ".join(command)
    try:
        ret = subprocess.run(
            cmd_list,
            env=os.environ.copy(),
            input=stdin,
            encoding="utf8",
            check=False,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.STDOUT if capture else None,
        )
    except FileNotFoundError:
        # Indicates the *command* wasn't found, it's an error before the command
        # is run.
        raise FileNotFoundError(
            Errors.E970.format(str_command=cmd_str, tool=cmd_list[0])
        ) from None
    if ret.returncode != 0 and capture:
        message = f"Error running command:\n\n{cmd_str}\n\n"
        message += f"Subprocess exited with status {ret.returncode}"
        if ret.stdout is not None:
            message += f"\n\nProcess log (stdout and stderr):\n\n"
            message += ret.stdout
        error = subprocess.SubprocessError(message)
        error.ret = ret  # type: ignore[attr-defined]
        error.command = cmd_str  # type: ignore[attr-defined]
        raise error
    elif ret.returncode != 0:
        sys.exit(ret.returncode)
    return ret


@contextmanager
def working_dir(path: Union[str, Path]) -> Iterator[Path]:
    """Change current working directory and returns to previous on exit.

    path (str / Path): The directory to navigate to.
    YIELDS (Path): The absolute path to the current working directory. This
        should be used if the block needs to perform actions within the working
        directory, to prevent mismatches with relative paths.
    """
    prev_cwd = Path.cwd()
    current = Path(path).resolve()
    os.chdir(str(current))
    try:
        yield current
    finally:
        os.chdir(str(prev_cwd))


@contextmanager
def make_tempdir() -> Generator[Path, None, None]:
    """Execute a block in a temporary directory and remove the directory and
    its contents at the end of the with block.

    YIELDS (Path): The path of the temp directory.
    """
    d = Path(tempfile.mkdtemp())
    yield d
    try:
        shutil.rmtree(str(d))
    except PermissionError as e:
        warnings.warn(Warnings.W091.format(dir=d, msg=e))


def is_cwd(path: Union[Path, str]) -> bool:
    """Check whether a path is the current working directory.

    path (Union[Path, str]): The directory path.
    RETURNS (bool): Whether the path is the current working directory.
    """
    return str(Path(path).resolve()).lower() == str(Path.cwd().resolve()).lower()


def is_in_jupyter() -> bool:
    """Check if user is running spaCy from a Jupyter notebook by detecting the
    IPython kernel. Mainly used for the displaCy visualizer.
    RETURNS (bool): True if in Jupyter, False if not.
    """
    # https://stackoverflow.com/a/39662359/6400719
    try:
        shell = get_ipython().__class__.__name__  # type: ignore[name-defined]
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
    except NameError:
        return False  # Probably standard Python interpreter
    return False


def get_object_name(obj: Any) -> str:
    """Get a human-readable name of a Python object, e.g. a pipeline component.

    obj (Any): The Python object, typically a function or class.
    RETURNS (str): A human-readable name.
    """
    if hasattr(obj, "name") and obj.name is not None:
        return obj.name
    if hasattr(obj, "__name__"):
        return obj.__name__
    if hasattr(obj, "__class__") and hasattr(obj.__class__, "__name__"):
        return obj.__class__.__name__
    return repr(obj)


def is_same_func(func1: Callable, func2: Callable) -> bool:
    """Approximately decide whether two functions are the same, even if their
    identity is different (e.g. after they have been live reloaded). Mostly
    used in the @Language.component and @Language.factory decorators to decide
    whether to raise if a factory already exists. Allows decorator to run
    multiple times with the same function.

    func1 (Callable): The first function.
    func2 (Callable): The second function.
    RETURNS (bool): Whether it's the same function (most likely).
    """
    if not callable(func1) or not callable(func2):
        return False
    if not hasattr(func1, "__qualname__") or not hasattr(func2, "__qualname__"):
        return False
    same_name = func1.__qualname__ == func2.__qualname__
    same_file = inspect.getfile(func1) == inspect.getfile(func2)
    same_code = inspect.getsourcelines(func1) == inspect.getsourcelines(func2)
    return same_name and same_file and same_code


def get_cuda_stream(
    require: bool = False, non_blocking: bool = True
) -> Optional[CudaStream]:
    ops = get_current_ops()
    if CudaStream is None:
        return None
    elif isinstance(ops, NumpyOps):
        return None
    else:
        return CudaStream(non_blocking=non_blocking)


def get_async(stream, numpy_array):
    if cupy is None:
        return numpy_array
    else:
        array = cupy.ndarray(numpy_array.shape, order="C", dtype=numpy_array.dtype)
        array.set(numpy_array, stream=stream)
        return array


def read_regex(path: Union[str, Path]) -> Pattern:
    path = ensure_path(path)
    with path.open(encoding="utf8") as file_:
        entries = file_.read().split("\n")
    expression = "|".join(
        ["^" + re.escape(piece) for piece in entries if piece.strip()]
    )
    return re.compile(expression)


def compile_prefix_regex(entries: Iterable[Union[str, Pattern]]) -> Pattern:
    """Compile a sequence of prefix rules into a regex object.

    entries (Iterable[Union[str, Pattern]]): The prefix rules, e.g.
        spacy.lang.punctuation.TOKENIZER_PREFIXES.
    RETURNS (Pattern): The regex object. to be used for Tokenizer.prefix_search.
    """
    expression = "|".join(["^" + piece for piece in entries if piece.strip()])  # type: ignore[operator, union-attr]
    return re.compile(expression)


def compile_suffix_regex(entries: Iterable[Union[str, Pattern]]) -> Pattern:
    """Compile a sequence of suffix rules into a regex object.

    entries (Iterable[Union[str, Pattern]]): The suffix rules, e.g.
        spacy.lang.punctuation.TOKENIZER_SUFFIXES.
    RETURNS (Pattern): The regex object. to be used for Tokenizer.suffix_search.
    """
    expression = "|".join([piece + "$" for piece in entries if piece.strip()])  # type: ignore[operator, union-attr]
    return re.compile(expression)


def compile_infix_regex(entries: Iterable[Union[str, Pattern]]) -> Pattern:
    """Compile a sequence of infix rules into a regex object.

    entries (Iterable[Union[str, Pattern]]): The infix rules, e.g.
        spacy.lang.punctuation.TOKENIZER_INFIXES.
    RETURNS (regex object): The regex object. to be used for Tokenizer.infix_finditer.
    """
    expression = "|".join([piece for piece in entries if piece.strip()])  # type: ignore[misc, union-attr]
    return re.compile(expression)


def add_lookups(default_func: Callable[[str], Any], *lookups) -> Callable[[str], Any]:
    """Extend an attribute function with special cases. If a word is in the
    lookups, the value is returned. Otherwise the previous function is used.

    default_func (callable): The default function to execute.
    *lookups (dict): Lookup dictionary mapping string to attribute value.
    RETURNS (callable): Lexical attribute getter.
    """
    # This is implemented as functools.partial instead of a closure, to allow
    # pickle to work.
    return functools.partial(_get_attr_unless_lookup, default_func, lookups)


def _get_attr_unless_lookup(
    default_func: Callable[[str], Any], lookups: Dict[str, Any], string: str
) -> Any:
    for lookup in lookups:
        if string in lookup:
            return lookup[string]  # type: ignore[index]
    return default_func(string)


def update_exc(
    base_exceptions: Dict[str, List[dict]], *addition_dicts
) -> Dict[str, List[dict]]:
    """Update and validate tokenizer exceptions. Will overwrite exceptions.

    base_exceptions (Dict[str, List[dict]]): Base exceptions.
    *addition_dicts (Dict[str, List[dict]]): Exceptions to add to the base dict, in order.
    RETURNS (Dict[str, List[dict]]): Combined tokenizer exceptions.
    """
    exc = dict(base_exceptions)
    for additions in addition_dicts:
        for orth, token_attrs in additions.items():
            if not all(isinstance(attr[ORTH], str) for attr in token_attrs):
                raise ValueError(Errors.E055.format(key=orth, orths=token_attrs))
            described_orth = "".join(attr[ORTH] for attr in token_attrs)
            if orth != described_orth:
                raise ValueError(Errors.E056.format(key=orth, orths=described_orth))
        exc.update(additions)
    exc = expand_exc(exc, "'", "’")
    return exc


def expand_exc(
    excs: Dict[str, List[dict]], search: str, replace: str
) -> Dict[str, List[dict]]:
    """Find string in tokenizer exceptions, duplicate entry and replace string.
    For example, to add additional versions with typographic apostrophes.

    excs (Dict[str, List[dict]]): Tokenizer exceptions.
    search (str): String to find and replace.
    replace (str): Replacement.
    RETURNS (Dict[str, List[dict]]): Combined tokenizer exceptions.
    """

    def _fix_token(token, search, replace):
        fixed = dict(token)
        fixed[ORTH] = fixed[ORTH].replace(search, replace)
        return fixed

    new_excs = dict(excs)
    for token_string, tokens in excs.items():
        if search in token_string:
            new_key = token_string.replace(search, replace)
            new_value = [_fix_token(t, search, replace) for t in tokens]
            new_excs[new_key] = new_value
    return new_excs


def normalize_slice(
    length: int, start: int, stop: int, step: Optional[int] = None
) -> Tuple[int, int]:
    if not (step is None or step == 1):
        raise ValueError(Errors.E057)
    if start is None:
        start = 0
    elif start < 0:
        start += length
    start = min(length, max(0, start))
    if stop is None:
        stop = length
    elif stop < 0:
        stop += length
    stop = min(length, max(start, stop))
    return start, stop


def filter_spans(spans: Iterable["Span"]) -> List["Span"]:
    """Filter a sequence of spans and remove duplicates or overlaps. Useful for
    creating named entities (where one token can only be part of one entity) or
    when merging spans with `Retokenizer.merge`. When spans overlap, the (first)
    longest span is preferred over shorter spans.

    spans (Iterable[Span]): The spans to filter.
    RETURNS (List[Span]): The filtered spans.
    """
    get_sort_key = lambda span: (span.end - span.start, -span.start)
    sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
    result = []
    seen_tokens: Set[int] = set()
    for span in sorted_spans:
        # Check for end - 1 here because boundaries are inclusive
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
            seen_tokens.update(range(span.start, span.end))
    result = sorted(result, key=lambda span: span.start)
    return result


def filter_chain_spans(*spans: Iterable["Span"]) -> List["Span"]:
    return filter_spans(itertools.chain(*spans))


@registry.misc("spacy.first_longest_spans_filter.v1")
def make_first_longest_spans_filter():
    return filter_chain_spans


def to_bytes(getters: Dict[str, Callable[[], bytes]], exclude: Iterable[str]) -> bytes:
    return srsly.msgpack_dumps(to_dict(getters, exclude))


def from_bytes(
    bytes_data: bytes,
    setters: Dict[str, Callable[[bytes], Any]],
    exclude: Iterable[str],
) -> None:
    return from_dict(srsly.msgpack_loads(bytes_data), setters, exclude)  # type: ignore[return-value]


def to_dict(
    getters: Dict[str, Callable[[], Any]], exclude: Iterable[str]
) -> Dict[str, Any]:
    serialized = {}
    for key, getter in getters.items():
        # Split to support file names like meta.json
        if key.split(".")[0] not in exclude:
            serialized[key] = getter()
    return serialized


def from_dict(
    msg: Dict[str, Any],
    setters: Dict[str, Callable[[Any], Any]],
    exclude: Iterable[str],
) -> Dict[str, Any]:
    for key, setter in setters.items():
        # Split to support file names like meta.json
        if key.split(".")[0] not in exclude and key in msg:
            setter(msg[key])
    return msg


def to_disk(
    path: Union[str, Path],
    writers: Dict[str, Callable[[Path], None]],
    exclude: Iterable[str],
) -> Path:
    path = ensure_path(path)
    if not path.exists():
        path.mkdir()
    for key, writer in writers.items():
        # Split to support file names like meta.json
        if key.split(".")[0] not in exclude:
            writer(path / key)
    return path


def from_disk(
    path: Union[str, Path],
    readers: Dict[str, Callable[[Path], None]],
    exclude: Iterable[str],
) -> Path:
    path = ensure_path(path)
    for key, reader in readers.items():
        # Split to support file names like meta.json
        if key.split(".")[0] not in exclude:
            reader(path / key)
    return path


def import_file(name: str, loc: Union[str, Path]) -> ModuleType:
    """Import module from a file. Used to load models from a directory.

    name (str): Name of module to load.
    loc (str / Path): Path to the file.
    RETURNS: The loaded module.
    """
    spec = importlib.util.spec_from_file_location(name, str(loc))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def minify_html(html: str) -> str:
    """Perform a template-specific, rudimentary HTML minification for displaCy.
    Disclaimer: NOT a general-purpose solution, only removes indentation and
    newlines.

    html (str): Markup to minify.
    RETURNS (str): "Minified" HTML.
    """
    return html.strip().replace("    ", "").replace("\n", "")


def escape_html(text: str) -> str:
    """Replace <, >, &, " with their HTML encoded representation. Intended to
    prevent HTML errors in rendered displaCy markup.

    text (str): The original text.
    RETURNS (str): Equivalent text to be safely used within HTML.
    """
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text


def get_words_and_spaces(
    words: Iterable[str], text: str
) -> Tuple[List[str], List[bool]]:
    """Given a list of words and a text, reconstruct the original tokens and
    return a list of words and spaces that can be used to create a Doc. This
    can help recover destructive tokenization that didn't preserve any
    whitespace information.

    words (Iterable[str]): The words.
    text (str): The original text.
    RETURNS (Tuple[List[str], List[bool]]): The words and spaces.
    """
    if "".join("".join(words).split()) != "".join(text.split()):
        raise ValueError(Errors.E194.format(text=text, words=words))
    text_words = []
    text_spaces = []
    text_pos = 0
    # normalize words to remove all whitespace tokens
    norm_words = [word for word in words if not word.isspace()]
    # align words with text
    for word in norm_words:
        try:
            word_start = text[text_pos:].index(word)
        except ValueError:
            raise ValueError(Errors.E194.format(text=text, words=words)) from None
        if word_start > 0:
            text_words.append(text[text_pos : text_pos + word_start])
            text_spaces.append(False)
            text_pos += word_start
        text_words.append(word)
        text_spaces.append(False)
        text_pos += len(word)
        if text_pos < len(text) and text[text_pos] == " ":
            text_spaces[-1] = True
            text_pos += 1
    if text_pos < len(text):
        text_words.append(text[text_pos:])
        text_spaces.append(False)
    return (text_words, text_spaces)


def copy_config(config: Union[Dict[str, Any], Config]) -> Config:
    """Deep copy a Config. Will raise an error if the config contents are not
    JSON-serializable.

    config (Config): The config to copy.
    RETURNS (Config): The copied config.
    """
    try:
        return Config(config).copy()
    except ValueError:
        raise ValueError(Errors.E961.format(config=config)) from None


def dot_to_dict(values: Dict[str, Any]) -> Dict[str, dict]:
    """Convert dot notation to a dict. For example: {"token.pos": True,
    "token._.xyz": True} becomes {"token": {"pos": True, "_": {"xyz": True }}}.

    values (Dict[str, Any]): The key/value pairs to convert.
    RETURNS (Dict[str, dict]): The converted values.
    """
    result: Dict[str, dict] = {}
    for key, value in values.items():
        path = result
        parts = key.lower().split(".")
        for i, item in enumerate(parts):
            is_last = i == len(parts) - 1
            path = path.setdefault(item, value if is_last else {})
    return result


def dict_to_dot(obj: Dict[str, dict]) -> Dict[str, Any]:
    """Convert dot notation to a dict. For example: {"token": {"pos": True,
    "_": {"xyz": True }}} becomes {"token.pos": True, "token._.xyz": True}.

    values (Dict[str, dict]): The dict to convert.
    RETURNS (Dict[str, Any]): The key/value pairs.
    """
    return {".".join(key): value for key, value in walk_dict(obj)}


def dot_to_object(config: Config, section: str):
    """Convert dot notation of a "section" to a specific part of the Config.
    e.g. "training.optimizer" would return the Optimizer object.
    Throws an error if the section is not defined in this config.

    config (Config): The config.
    section (str): The dot notation of the section in the config.
    RETURNS: The object denoted by the section
    """
    component = config
    parts = section.split(".")
    for item in parts:
        try:
            component = component[item]
        except (KeyError, TypeError):
            raise KeyError(Errors.E952.format(name=section)) from None
    return component


def set_dot_to_object(config: Config, section: str, value: Any) -> None:
    """Update a config at a given position from a dot notation.

    config (Config): The config.
    section (str): The dot notation of the section in the config.
    value (Any): The value to set in the config.
    """
    component = config
    parts = section.split(".")
    for i, item in enumerate(parts):
        try:
            if i == len(parts) - 1:
                component[item] = value
            else:
                component = component[item]
        except (KeyError, TypeError):
            raise KeyError(Errors.E952.format(name=section)) from None


def walk_dict(
    node: Dict[str, Any], parent: List[str] = []
) -> Iterator[Tuple[List[str], Any]]:
    """Walk a dict and yield the path and values of the leaves."""
    for key, value in node.items():
        key_parent = [*parent, key]
        if isinstance(value, dict):
            yield from walk_dict(value, key_parent)
        else:
            yield (key_parent, value)


def get_arg_names(func: Callable) -> List[str]:
    """Get a list of all named arguments of a function (regular,
    keyword-only).

    func (Callable): The function
    RETURNS (List[str]): The argument names.
    """
    argspec = inspect.getfullargspec(func)
    return list(dict.fromkeys([*argspec.args, *argspec.kwonlyargs]))


def combine_score_weights(
    weights: List[Dict[str, Optional[float]]],
    overrides: Dict[str, Optional[float]] = SimpleFrozenDict(),
) -> Dict[str, Optional[float]]:
    """Combine and normalize score weights defined by components, e.g.
    {"ents_r": 0.2, "ents_p": 0.3, "ents_f": 0.5} and {"some_other_score": 1.0}.

    weights (List[dict]): The weights defined by the components.
    overrides (Dict[str, Optional[Union[float, int]]]): Existing scores that
        should be preserved.
    RETURNS (Dict[str, float]): The combined and normalized weights.
    """
    # We divide each weight by the total weight sum.
    # We first need to extract all None/null values for score weights that
    # shouldn't be shown in the table *or* be weighted
    result: Dict[str, Optional[float]] = {
        key: value for w_dict in weights for (key, value) in w_dict.items()
    }
    result.update(overrides)
    weight_sum = sum([v if v else 0.0 for v in result.values()])
    for key, value in result.items():
        if value and weight_sum > 0:
            result[key] = round(value / weight_sum, 2)
    return result


class DummyTokenizer:
    def __call__(self, text):
        raise NotImplementedError

    def pipe(self, texts, **kwargs):
        for text in texts:
            yield self(text)

    # add dummy methods for to_bytes, from_bytes, to_disk and from_disk to
    # allow serialization (see #1557)
    def to_bytes(self, **kwargs):
        return b""

    def from_bytes(self, data: bytes, **kwargs) -> "DummyTokenizer":
        return self

    def to_disk(self, path: Union[str, Path], **kwargs) -> None:
        return None

    def from_disk(self, path: Union[str, Path], **kwargs) -> "DummyTokenizer":
        return self


def create_default_optimizer() -> Optimizer:
    return Adam()


def minibatch(items, size):
    """Iterate over batches of items. `size` may be an iterator,
    so that batch-size can vary on each step.
    """
    if isinstance(size, int):
        size_ = itertools.repeat(size)
    else:
        size_ = size
    items = iter(items)
    while True:
        batch_size = next(size_)
        batch = list(itertools.islice(items, int(batch_size)))
        if len(batch) == 0:
            break
        yield list(batch)


def is_cython_func(func: Callable) -> bool:
    """Slightly hacky check for whether a callable is implemented in Cython.
    Can be used to implement slightly different behaviors, especially around
    inspecting and parameter annotations. Note that this will only return True
    for actual cdef functions and methods, not regular Python functions defined
    in Python modules.

    func (Callable): The callable to check.
    RETURNS (bool): Whether the callable is Cython (probably).
    """
    attr = "__pyx_vtable__"
    if hasattr(func, attr):  # function or class instance
        return True
    # https://stackoverflow.com/a/55767059
    if (
        hasattr(func, "__qualname__")
        and hasattr(func, "__module__")
        and func.__module__ in sys.modules
    ):  # method
        cls_func = vars(sys.modules[func.__module__])[func.__qualname__.split(".")[0]]
        return hasattr(cls_func, attr)
    return False


def check_bool_env_var(env_var: str) -> bool:
    """Convert the value of an environment variable to a boolean. Add special
    check for "0" (falsy) and consider everything else truthy, except unset.

    env_var (str): The name of the environment variable to check.
    RETURNS (bool): Its boolean value.
    """
    value = os.environ.get(env_var, False)
    if value == "0":
        return False
    return bool(value)


def _pipe(
    docs: Iterable["Doc"],
    proc: "Pipe",
    name: str,
    default_error_handler: Callable[[str, "Pipe", List["Doc"], Exception], NoReturn],
    kwargs: Mapping[str, Any],
) -> Iterator["Doc"]:
    if hasattr(proc, "pipe"):
        yield from proc.pipe(docs, **kwargs)
    else:
        # We added some args for pipe that __call__ doesn't expect.
        kwargs = dict(kwargs)
        error_handler = default_error_handler
        if hasattr(proc, "get_error_handler"):
            error_handler = proc.get_error_handler()
        for arg in ["batch_size"]:
            if arg in kwargs:
                kwargs.pop(arg)
        for doc in docs:
            try:
                doc = proc(doc, **kwargs)  # type: ignore[call-arg]
                yield doc
            except Exception as e:
                error_handler(name, proc, [doc], e)


def raise_error(proc_name, proc, docs, e):
    raise e


def ignore_error(proc_name, proc, docs, e):
    pass


def warn_if_jupyter_cupy():
    """Warn about require_gpu if a jupyter notebook + cupy + mismatched
    contextvars vs. thread ops are detected
    """
    if is_in_jupyter():
        from thinc.backends.cupy_ops import CupyOps

        if CupyOps.xp is not None:
            from thinc.backends import contextvars_eq_thread_ops

            if not contextvars_eq_thread_ops():
                warnings.warn(Warnings.W111)


def check_lexeme_norms(vocab, component_name):
    lexeme_norms = vocab.lookups.get_table("lexeme_norm", {})
    if len(lexeme_norms) == 0 and vocab.lang in LEXEME_NORM_LANGS:
        langs = ", ".join(LEXEME_NORM_LANGS)
        logger.debug(Warnings.W033.format(model=component_name, langs=langs))


def to_ternary_int(val) -> int:
    """Convert a value to the ternary 1/0/-1 int used for True/None/False in
    attributes such as SENT_START: True/1/1.0 is 1 (True), None/0/0.0 is 0
    (None), any other values are -1 (False).
    """
    if val is True:
        return 1
    elif val is None:
        return 0
    elif val is False:
        return -1
    elif val == 1:
        return 1
    elif val == 0:
        return 0
    else:
        return -1


# The following implementation of packages_distributions() is adapted from
# importlib_metadata, which is distributed under the Apache 2.0 License.
# Copyright (c) 2017-2019 Jason R. Coombs, Barry Warsaw
# See licenses/3rd_party_licenses.txt
def packages_distributions() -> Dict[str, List[str]]:
    """Return a mapping of top-level packages to their distributions. We're
    inlining this helper from the importlib_metadata "backport" here, since
    it's not available in the builtin importlib.metadata.
    """
    pkg_to_dist = defaultdict(list)
    for dist in importlib_metadata.distributions():
        for pkg in (dist.read_text("top_level.txt") or "").split():
            pkg_to_dist[pkg].append(dist.metadata["Name"])
    return dict(pkg_to_dist)


def all_equal(iterable):
    """Return True if all the elements are equal to each other
    (or if the input is an empty sequence), False otherwise."""
    g = itertools.groupby(iterable)
    return next(g, True) and not next(g, False)
