# coding: utf8
from __future__ import unicode_literals, print_function

import os
import importlib
import re
from pathlib import Path
import random
from collections import OrderedDict
from thinc.neural._classes.model import Model
from thinc.neural.ops import NumpyOps
import functools
import itertools
import numpy.random
import numpy
import srsly
import catalogue
import sys
import warnings
from . import about

try:
    import jsonschema
except ImportError:
    jsonschema = None

try:
    import cupy.random
except ImportError:
    cupy = None

from .symbols import ORTH
from .compat import cupy, CudaStream, path2str, basestring_, unicode_
from .compat import import_file
from .errors import Errors, Warnings


_data_path = Path(__file__).parent / "data"
_PRINT_ENV = False
OOV_RANK = numpy.iinfo(numpy.uint64).max


class registry(object):
    languages = catalogue.create("spacy", "languages", entry_points=True)
    architectures = catalogue.create("spacy", "architectures", entry_points=True)
    lookups = catalogue.create("spacy", "lookups", entry_points=True)
    factories = catalogue.create("spacy", "factories", entry_points=True)
    displacy_colors = catalogue.create("spacy", "displacy_colors", entry_points=True)


def set_env_log(value):
    global _PRINT_ENV
    _PRINT_ENV = value


def lang_class_is_loaded(lang):
    """Check whether a Language class is already loaded. Language classes are
    loaded lazily, to avoid expensive setup code associated with the language
    data.

    lang (unicode): Two-letter language code, e.g. 'en'.
    RETURNS (bool): Whether a Language class has been loaded.
    """
    return lang in registry.languages


def get_lang_class(lang):
    """Import and load a Language class.

    lang (unicode): Two-letter language code, e.g. 'en'.
    RETURNS (Language): Language class.
    """
    # Check if language is registered / entry point is available
    if lang in registry.languages:
        return registry.languages.get(lang)
    else:
        try:
            module = importlib.import_module(".lang.%s" % lang, "spacy")
        except ImportError as err:
            raise ImportError(Errors.E048.format(lang=lang, err=err))
        set_lang_class(lang, getattr(module, module.__all__[0]))
    return registry.languages.get(lang)


def set_lang_class(name, cls):
    """Set a custom Language class name that can be loaded via get_lang_class.

    name (unicode): Name of Language class.
    cls (Language): Language class.
    """
    registry.languages.register(name, func=cls)


def get_data_path(require_exists=True):
    """Get path to spaCy data directory.

    require_exists (bool): Only return path if it exists, otherwise None.
    RETURNS (Path or None): Data path or None.
    """
    if not require_exists:
        return _data_path
    else:
        return _data_path if _data_path.exists() else None


def set_data_path(path):
    """Set path to spaCy data directory.

    path (unicode or Path): Path to new data directory.
    """
    global _data_path
    _data_path = ensure_path(path)


def make_layer(arch_config):
    arch_func = registry.architectures.get(arch_config["arch"])
    return arch_func(arch_config["config"])


def ensure_path(path):
    """Ensure string is converted to a Path.

    path: Anything. If string, it's converted to Path.
    RETURNS: Path or original argument.
    """
    if isinstance(path, basestring_):
        return Path(path)
    else:
        return path


def load_language_data(path):
    """Load JSON language data using the given path as a base. If the provided
    path isn't present, will attempt to load a gzipped version before giving up.

    path (unicode / Path): The data to load.
    RETURNS: The loaded data.
    """
    path = ensure_path(path)
    if path.exists():
        return srsly.read_json(path)
    path = path.with_suffix(path.suffix + ".gz")
    if path.exists():
        return srsly.read_gzip_json(path)
    raise ValueError(Errors.E160.format(path=path2str(path)))


def get_module_path(module):
    if not hasattr(module, "__module__"):
        raise ValueError(Errors.E169.format(module=repr(module)))
    return Path(sys.modules[module.__module__].__file__).parent


def load_model(name, **overrides):
    """Load a model from a shortcut link, package or data path.

    name (unicode): Package name, shortcut link or model path.
    **overrides: Specific overrides, like pipeline components to disable.
    RETURNS (Language): `Language` class with the loaded model.
    """
    data_path = get_data_path()
    if not data_path or not data_path.exists():
        raise IOError(Errors.E049.format(path=path2str(data_path)))
    if isinstance(name, basestring_):  # in data dir / shortcut
        if name.startswith("blank:"):  # shortcut for blank model
            return get_lang_class(name.replace("blank:", ""))()
        if name in set([d.name for d in data_path.iterdir()]):
            return load_model_from_link(name, **overrides)
        if is_package(name):  # installed as package
            return load_model_from_package(name, **overrides)
        if Path(name).exists():  # path to model data directory
            return load_model_from_path(Path(name), **overrides)
    elif hasattr(name, "exists"):  # Path or Path-like to model data
        return load_model_from_path(name, **overrides)
    raise IOError(Errors.E050.format(name=name))


def load_model_from_link(name, **overrides):
    """Load a model from a shortcut link, or directory in spaCy data path."""
    path = get_data_path() / name / "__init__.py"
    try:
        cls = import_file(name, path)
    except AttributeError:
        raise IOError(Errors.E051.format(name=name))
    return cls.load(**overrides)


def load_model_from_package(name, **overrides):
    """Load a model from an installed package."""
    cls = importlib.import_module(name)
    return cls.load(**overrides)


def load_model_from_path(model_path, meta=False, **overrides):
    """Load a model from a data directory path. Creates Language class with
    pipeline from meta.json and then calls from_disk() with path."""
    if not meta:
        meta = get_model_meta(model_path)
    # Support language factories registered via entry points (e.g. custom
    # language subclass) while keeping top-level language identifier "lang"
    lang = meta.get("lang_factory", meta["lang"])
    cls = get_lang_class(lang)
    nlp = cls(meta=meta, **overrides)
    pipeline = meta.get("pipeline", [])
    factories = meta.get("factories", {})
    disable = overrides.get("disable", [])
    if pipeline is True:
        pipeline = nlp.Defaults.pipe_names
    elif pipeline in (False, None):
        pipeline = []
    # skip "vocab" from overrides in component initialization since vocab is
    # already configured from overrides when nlp is initialized above
    if "vocab" in overrides:
        del overrides["vocab"]
    for name in pipeline:
        if name not in disable:
            config = meta.get("pipeline_args", {}).get(name, {})
            config.update(overrides)
            factory = factories.get(name, name)
            component = nlp.create_pipe(factory, config=config)
            nlp.add_pipe(component, name=name)
    return nlp.from_disk(model_path, exclude=disable)


def load_model_from_init_py(init_file, **overrides):
    """Helper function to use in the `load()` method of a model package's
    __init__.py.

    init_file (unicode): Path to model's __init__.py, i.e. `__file__`.
    **overrides: Specific overrides, like pipeline components to disable.
    RETURNS (Language): `Language` class with loaded model.
    """
    model_path = Path(init_file).parent
    meta = get_model_meta(model_path)
    data_dir = "%s_%s-%s" % (meta["lang"], meta["name"], meta["version"])
    data_path = model_path / data_dir
    if not model_path.exists():
        raise IOError(Errors.E052.format(path=path2str(data_path)))
    return load_model_from_path(data_path, meta, **overrides)


def get_model_meta(path):
    """Get model meta.json from a directory path and validate its contents.

    path (unicode or Path): Path to model directory.
    RETURNS (dict): The model's meta data.
    """
    model_path = ensure_path(path)
    if not model_path.exists():
        raise IOError(Errors.E052.format(path=path2str(model_path)))
    meta_path = model_path / "meta.json"
    if not meta_path.is_file():
        raise IOError(Errors.E053.format(path=meta_path))
    meta = srsly.read_json(meta_path)
    for setting in ["lang", "name", "version"]:
        if setting not in meta or not meta[setting]:
            raise ValueError(Errors.E054.format(setting=setting))
    if "spacy_version" in meta:
        about_major_minor = ".".join(about.__version__.split(".")[:2])
        if not meta["spacy_version"].startswith(">=" + about_major_minor):
            # try to simplify version requirements from model meta to vx.x
            # for warning message
            meta_spacy_version = "v" + ".".join(
                meta["spacy_version"].replace(">=", "").split(".")[:2]
            )
            # if the format is unexpected, supply the full version
            if not re.match(r"v\d+\.\d+", meta_spacy_version):
                meta_spacy_version = meta["spacy_version"]
            warn_msg = Warnings.W031.format(
                model=meta["lang"] + "_" + meta["name"],
                model_version=meta["version"],
                version=meta_spacy_version,
                current=about.__version__,
            )
            warnings.warn(warn_msg)
    else:
        warn_msg = Warnings.W032.format(
            model=meta["lang"] + "_" + meta["name"],
            model_version=meta["version"],
            current=about.__version__,
        )
        warnings.warn(warn_msg)
    return meta


def is_package(name):
    """Check if string maps to a package installed via pip.

    name (unicode): Name of package.
    RETURNS (bool): True if installed package, False if not.
    """
    import pkg_resources

    name = name.lower()  # compare package name against lowercase name
    packages = pkg_resources.working_set.by_key.keys()
    for package in packages:
        if package.lower().replace("-", "_") == name:
            return True
    return False


def get_package_path(name):
    """Get the path to an installed package.

    name (unicode): Package name.
    RETURNS (Path): Path to installed package.
    """
    name = name.lower()  # use lowercase version to be safe
    # Here we're importing the module just to find it. This is worryingly
    # indirect, but it's otherwise very difficult to find the package.
    pkg = importlib.import_module(name)
    return Path(pkg.__file__).parent


def is_in_jupyter():
    """Check if user is running spaCy from a Jupyter notebook by detecting the
    IPython kernel. Mainly used for the displaCy visualizer.
    RETURNS (bool): True if in Jupyter, False if not.
    """
    # https://stackoverflow.com/a/39662359/6400719
    try:
        shell = get_ipython().__class__.__name__
        if shell == "ZMQInteractiveShell":
            return True  # Jupyter notebook or qtconsole
    except NameError:
        return False  # Probably standard Python interpreter
    return False


def get_component_name(component):
    if hasattr(component, "name"):
        return component.name
    if hasattr(component, "__name__"):
        return component.__name__
    if hasattr(component, "__class__") and hasattr(component.__class__, "__name__"):
        return component.__class__.__name__
    return repr(component)


def get_cuda_stream(require=False, non_blocking=True):
    if CudaStream is None:
        return None
    elif isinstance(Model.ops, NumpyOps):
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


def env_opt(name, default=None):
    if type(default) is float:
        type_convert = float
    else:
        type_convert = int
    if "SPACY_" + name.upper() in os.environ:
        value = type_convert(os.environ["SPACY_" + name.upper()])
        if _PRINT_ENV:
            print(name, "=", repr(value), "via", "$SPACY_" + name.upper())
        return value
    elif name in os.environ:
        value = type_convert(os.environ[name])
        if _PRINT_ENV:
            print(name, "=", repr(value), "via", "$" + name)
        return value
    else:
        if _PRINT_ENV:
            print(name, "=", repr(default), "by default")
        return default


def read_regex(path):
    path = ensure_path(path)
    with path.open(encoding="utf8") as file_:
        entries = file_.read().split("\n")
    expression = "|".join(
        ["^" + re.escape(piece) for piece in entries if piece.strip()]
    )
    return re.compile(expression)


def compile_prefix_regex(entries):
    """Compile a sequence of prefix rules into a regex object.

    entries (tuple): The prefix rules, e.g. spacy.lang.punctuation.TOKENIZER_PREFIXES.
    RETURNS (regex object): The regex object. to be used for Tokenizer.prefix_search.
    """
    if "(" in entries:
        # Handle deprecated data
        expression = "|".join(
            ["^" + re.escape(piece) for piece in entries if piece.strip()]
        )
        return re.compile(expression)
    else:
        expression = "|".join(["^" + piece for piece in entries if piece.strip()])
        return re.compile(expression)


def compile_suffix_regex(entries):
    """Compile a sequence of suffix rules into a regex object.

    entries (tuple): The suffix rules, e.g. spacy.lang.punctuation.TOKENIZER_SUFFIXES.
    RETURNS (regex object): The regex object. to be used for Tokenizer.suffix_search.
    """
    expression = "|".join([piece + "$" for piece in entries if piece.strip()])
    return re.compile(expression)


def compile_infix_regex(entries):
    """Compile a sequence of infix rules into a regex object.

    entries (tuple): The infix rules, e.g. spacy.lang.punctuation.TOKENIZER_INFIXES.
    RETURNS (regex object): The regex object. to be used for Tokenizer.infix_finditer.
    """
    expression = "|".join([piece for piece in entries if piece.strip()])
    return re.compile(expression)


def add_lookups(default_func, *lookups):
    """Extend an attribute function with special cases. If a word is in the
    lookups, the value is returned. Otherwise the previous function is used.

    default_func (callable): The default function to execute.
    *lookups (dict): Lookup dictionary mapping string to attribute value.
    RETURNS (callable): Lexical attribute getter.
    """
    # This is implemented as functools.partial instead of a closure, to allow
    # pickle to work.
    return functools.partial(_get_attr_unless_lookup, default_func, lookups)


def _get_attr_unless_lookup(default_func, lookups, string):
    for lookup in lookups:
        if string in lookup:
            return lookup[string]
    return default_func(string)


def update_exc(base_exceptions, *addition_dicts):
    """Update and validate tokenizer exceptions. Will overwrite exceptions.

    base_exceptions (dict): Base exceptions.
    *addition_dicts (dict): Exceptions to add to the base dict, in order.
    RETURNS (dict): Combined tokenizer exceptions.
    """
    exc = dict(base_exceptions)
    for additions in addition_dicts:
        for orth, token_attrs in additions.items():
            if not all(isinstance(attr[ORTH], unicode_) for attr in token_attrs):
                raise ValueError(Errors.E055.format(key=orth, orths=token_attrs))
            described_orth = "".join(attr[ORTH] for attr in token_attrs)
            if orth != described_orth:
                raise ValueError(Errors.E056.format(key=orth, orths=described_orth))
        exc.update(additions)
    exc = expand_exc(exc, "'", "’")
    return exc


def expand_exc(excs, search, replace):
    """Find string in tokenizer exceptions, duplicate entry and replace string.
    For example, to add additional versions with typographic apostrophes.

    excs (dict): Tokenizer exceptions.
    search (unicode): String to find and replace.
    replace (unicode): Replacement.
    RETURNS (dict): Combined tokenizer exceptions.
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


def normalize_slice(length, start, stop, step=None):
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


def minibatch(items, size=8):
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


def compounding(start, stop, compound):
    """Yield an infinite series of compounding values. Each time the
    generator is called, a value is produced by multiplying the previous
    value by the compound rate.

    EXAMPLE:
      >>> sizes = compounding(1., 10., 1.5)
      >>> assert next(sizes) == 1.
      >>> assert next(sizes) == 1 * 1.5
      >>> assert next(sizes) == 1.5 * 1.5
    """

    def clip(value):
        return max(value, stop) if (start > stop) else min(value, stop)

    curr = float(start)
    while True:
        yield clip(curr)
        curr *= compound


def stepping(start, stop, steps):
    """Yield an infinite series of values that step from a start value to a
    final value over some number of steps. Each step is (stop-start)/steps.

    After the final value is reached, the generator continues yielding that
    value.

    EXAMPLE:
      >>> sizes = stepping(1., 200., 100)
      >>> assert next(sizes) == 1.
      >>> assert next(sizes) == 1 * (200.-1.) / 100
      >>> assert next(sizes) == 1 + (200.-1.) / 100 + (200.-1.) / 100
    """

    def clip(value):
        return max(value, stop) if (start > stop) else min(value, stop)

    curr = float(start)
    while True:
        yield clip(curr)
        curr += (stop - start) / steps


def decaying(start, stop, decay):
    """Yield an infinite series of linearly decaying values."""

    curr = float(start)
    while True:
        yield max(curr, stop)
        curr -= decay


def minibatch_by_words(items, size, tuples=True, count_words=len):
    """Create minibatches of a given number of words."""
    if isinstance(size, int):
        size_ = itertools.repeat(size)
    else:
        size_ = size
    items = iter(items)
    while True:
        batch_size = next(size_)
        batch = []
        while batch_size >= 0:
            try:
                if tuples:
                    doc, gold = next(items)
                else:
                    doc = next(items)
            except StopIteration:
                if batch:
                    yield batch
                return
            batch_size -= count_words(doc)
            if tuples:
                batch.append((doc, gold))
            else:
                batch.append(doc)
        if batch:
            yield batch


def itershuffle(iterable, bufsize=1000):
    """Shuffle an iterator. This works by holding `bufsize` items back
    and yielding them sometime later. Obviously, this is not unbiased –
    but should be good enough for batching. Larger bufsize means less bias.
    From https://gist.github.com/andres-erbsen/1307752

    iterable (iterable): Iterator to shuffle.
    bufsize (int): Items to hold back.
    YIELDS (iterable): The shuffled iterator.
    """
    iterable = iter(iterable)
    buf = []
    try:
        while True:
            for i in range(random.randint(1, bufsize - len(buf))):
                buf.append(next(iterable))
            random.shuffle(buf)
            for i in range(random.randint(1, bufsize)):
                if buf:
                    yield buf.pop()
                else:
                    break
    except StopIteration:
        random.shuffle(buf)
        while buf:
            yield buf.pop()
        raise StopIteration


def filter_spans(spans):
    """Filter a sequence of spans and remove duplicates or overlaps. Useful for
    creating named entities (where one token can only be part of one entity) or
    when merging spans with `Retokenizer.merge`. When spans overlap, the (first)
    longest span is preferred over shorter spans.

    spans (iterable): The spans to filter.
    RETURNS (list): The filtered spans.
    """
    get_sort_key = lambda span: (span.end - span.start, -span.start)
    sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
    result = []
    seen_tokens = set()
    for span in sorted_spans:
        # Check for end - 1 here because boundaries are inclusive
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
        seen_tokens.update(range(span.start, span.end))
    result = sorted(result, key=lambda span: span.start)
    return result


def to_bytes(getters, exclude):
    serialized = OrderedDict()
    for key, getter in getters.items():
        # Split to support file names like meta.json
        if key.split(".")[0] not in exclude:
            serialized[key] = getter()
    return srsly.msgpack_dumps(serialized)


def from_bytes(bytes_data, setters, exclude):
    msg = srsly.msgpack_loads(bytes_data)
    for key, setter in setters.items():
        # Split to support file names like meta.json
        if key.split(".")[0] not in exclude and key in msg:
            setter(msg[key])
    return msg


def to_disk(path, writers, exclude):
    path = ensure_path(path)
    if not path.exists():
        path.mkdir()
    for key, writer in writers.items():
        # Split to support file names like meta.json
        if key.split(".")[0] not in exclude:
            writer(path / key)
    return path


def from_disk(path, readers, exclude):
    path = ensure_path(path)
    for key, reader in readers.items():
        # Split to support file names like meta.json
        if key.split(".")[0] not in exclude:
            reader(path / key)
    return path


def minify_html(html):
    """Perform a template-specific, rudimentary HTML minification for displaCy.
    Disclaimer: NOT a general-purpose solution, only removes indentation and
    newlines.

    html (unicode): Markup to minify.
    RETURNS (unicode): "Minified" HTML.
    """
    return html.strip().replace("    ", "").replace("\n", "")


def escape_html(text):
    """Replace <, >, &, " with their HTML encoded representation. Intended to
    prevent HTML errors in rendered displaCy markup.

    text (unicode): The original text.
    RETURNS (unicode): Equivalent text to be safely used within HTML.
    """
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text


def use_gpu(gpu_id):
    try:
        import cupy.cuda.device
    except ImportError:
        return None
    from thinc.neural.ops import CupyOps

    device = cupy.cuda.device.Device(gpu_id)
    device.use()
    Model.ops = CupyOps()
    Model.Ops = CupyOps
    return device


def fix_random_seed(seed=0):
    random.seed(seed)
    numpy.random.seed(seed)
    if cupy is not None:
        cupy.random.seed(seed)


def get_json_validator(schema):
    # We're using a helper function here to make it easier to change the
    # validator that's used (e.g. different draft implementation), without
    # having to change it all across the codebase.
    # TODO: replace with (stable) Draft6Validator, if available
    if jsonschema is None:
        raise ValueError(Errors.E136)
    return jsonschema.Draft4Validator(schema)


def validate_schema(schema):
    """Validate a given schema. This just checks if the schema itself is valid."""
    validator = get_json_validator(schema)
    validator.check_schema(schema)


def validate_json(data, validator):
    """Validate data against a given JSON schema (see https://json-schema.org).

    data: JSON-serializable data to validate.
    validator (jsonschema.DraftXValidator): The validator.
    RETURNS (list): A list of error messages, if available.
    """
    errors = []
    for err in sorted(validator.iter_errors(data), key=lambda e: e.path):
        if err.path:
            err_path = "[{}]".format(" -> ".join([str(p) for p in err.path]))
        else:
            err_path = ""
        msg = err.message + " " + err_path
        if err.context:  # Error has suberrors, e.g. if schema uses anyOf
            suberrs = ["  - {}".format(suberr.message) for suberr in err.context]
            msg += ":\n{}".format("".join(suberrs))
        errors.append(msg)
    return errors


def get_serialization_exclude(serializers, exclude, kwargs):
    """Helper function to validate serialization args and manage transition from
    keyword arguments (pre v2.1) to exclude argument.
    """
    exclude = list(exclude)
    # Split to support file names like meta.json
    options = [name.split(".")[0] for name in serializers]
    for key, value in kwargs.items():
        if key in ("vocab",) and value is False:
            warnings.warn(Warnings.W015.format(arg=key), DeprecationWarning)
            exclude.append(key)
        elif key.split(".")[0] in options:
            raise ValueError(Errors.E128.format(arg=key))
        # TODO: user warning?
    return exclude


def get_words_and_spaces(words, text):
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
            raise ValueError(Errors.E194.format(text=text, words=words))
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


class SimpleFrozenDict(dict):
    """Simplified implementation of a frozen dict, mainly used as default
    function or method argument (for arguments that should default to empty
    dictionary). Will raise an error if user or spaCy attempts to add to dict.
    """

    def __setitem__(self, key, value):
        raise NotImplementedError(Errors.E095)

    def pop(self, key, default=None):
        raise NotImplementedError(Errors.E095)

    def update(self, other):
        raise NotImplementedError(Errors.E095)


class DummyTokenizer(object):
    # add dummy methods for to_bytes, from_bytes, to_disk and from_disk to
    # allow serialization (see #1557)
    def to_bytes(self, **kwargs):
        return b""

    def from_bytes(self, _bytes_data, **kwargs):
        return self

    def to_disk(self, _path, **kwargs):
        return None

    def from_disk(self, _path, **kwargs):
        return self
