# coding: utf8
from __future__ import unicode_literals, print_function

import os
import ujson
import pkg_resources
import importlib
import regex as re
from pathlib import Path
import sys
import textwrap
import random
from collections import OrderedDict
from thinc.neural._classes.model import Model
import functools
import cytoolz
import itertools
import numpy.random

from .symbols import ORTH
from .compat import cupy, CudaStream, path2str, basestring_, input_, unicode_
from .compat import import_file
from .errors import Errors

# Import these directly from Thinc, so that we're sure we always have the
# same version.
from thinc.neural._classes.model import msgpack
from thinc.neural._classes.model import msgpack_numpy


LANGUAGES = {}
_data_path = Path(__file__).parent / 'data'
_PRINT_ENV = False


def set_env_log(value):
    global _PRINT_ENV
    _PRINT_ENV = value


def get_lang_class(lang):
    """Import and load a Language class.

    lang (unicode): Two-letter language code, e.g. 'en'.
    RETURNS (Language): Language class.
    """
    global LANGUAGES
    if lang not in LANGUAGES:
        try:
            module = importlib.import_module('.lang.%s' % lang, 'spacy')
        except ImportError:
            raise ImportError(Errors.E048.format(lang=lang))
        LANGUAGES[lang] = getattr(module, module.__all__[0])
    return LANGUAGES[lang]


def set_lang_class(name, cls):
    """Set a custom Language class name that can be loaded via get_lang_class.

    name (unicode): Name of Language class.
    cls (Language): Language class.
    """
    global LANGUAGES
    LANGUAGES[name] = cls


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


def ensure_path(path):
    """Ensure string is converted to a Path.

    path: Anything. If string, it's converted to Path.
    RETURNS: Path or original argument.
    """
    if isinstance(path, basestring_):
        return Path(path)
    else:
        return path


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
        if name in set([d.name for d in data_path.iterdir()]):
            return load_model_from_link(name, **overrides)
        if is_package(name):  # installed as package
            return load_model_from_package(name, **overrides)
        if Path(name).exists():  # path to model data directory
            return load_model_from_path(Path(name), **overrides)
    elif hasattr(name, 'exists'):  # Path or Path-like to model data
        return load_model_from_path(name, **overrides)
    raise IOError(Errors.E050.format(name=name))


def load_model_from_link(name, **overrides):
    """Load a model from a shortcut link, or directory in spaCy data path."""
    path = get_data_path() / name / '__init__.py'
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
    cls = get_lang_class(meta['lang'])
    nlp = cls(meta=meta, **overrides)
    pipeline = meta.get('pipeline', [])
    disable = overrides.get('disable', [])
    if pipeline is True:
        pipeline = nlp.Defaults.pipe_names
    elif pipeline in (False, None):
        pipeline = []
    for name in pipeline:
        if name not in disable:
            config = meta.get('pipeline_args', {}).get(name, {})
            component = nlp.create_pipe(name, config=config)
            nlp.add_pipe(component, name=name)
    return nlp.from_disk(model_path)


def load_model_from_init_py(init_file, **overrides):
    """Helper function to use in the `load()` method of a model package's
    __init__.py.

    init_file (unicode): Path to model's __init__.py, i.e. `__file__`.
    **overrides: Specific overrides, like pipeline components to disable.
    RETURNS (Language): `Language` class with loaded model.
    """
    model_path = Path(init_file).parent
    meta = get_model_meta(model_path)
    data_dir = '%s_%s-%s' % (meta['lang'], meta['name'], meta['version'])
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
    meta_path = model_path / 'meta.json'
    if not meta_path.is_file():
        raise IOError(Errors.E053.format(path=meta_path))
    meta = read_json(meta_path)
    for setting in ['lang', 'name', 'version']:
        if setting not in meta or not meta[setting]:
            raise ValueError(Errors.E054.format(setting=setting))
    return meta


def is_package(name):
    """Check if string maps to a package installed via pip.

    name (unicode): Name of package.
    RETURNS (bool): True if installed package, False if not.
    """
    name = name.lower()  # compare package name against lowercase name
    packages = pkg_resources.working_set.by_key.keys()
    for package in packages:
        if package.lower().replace('-', '_') == name:
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
    try:
        cfg = get_ipython().config
        if cfg['IPKernelApp']['parent_appname'] == 'ipython-notebook':
            return True
    except NameError:
        return False
    return False


def get_cuda_stream(require=False):
    return CudaStream() if CudaStream is not None else None


def get_async(stream, numpy_array):
    if cupy is None:
        return numpy_array
    else:
        array = cupy.ndarray(numpy_array.shape, order='C',
                             dtype=numpy_array.dtype)
        array.set(numpy_array, stream=stream)
        return array


def env_opt(name, default=None):
    if type(default) is float:
        type_convert = float
    else:
        type_convert = int
    if 'SPACY_' + name.upper() in os.environ:
        value = type_convert(os.environ['SPACY_' + name.upper()])
        if _PRINT_ENV:
            print(name, "=", repr(value), "via", "$SPACY_" + name.upper())
        return value
    elif name in os.environ:
        value = type_convert(os.environ[name])
        if _PRINT_ENV:
            print(name, "=", repr(value), "via", '$' + name)
        return value
    else:
        if _PRINT_ENV:
            print(name, '=', repr(default), "by default")
        return default


def read_regex(path):
    path = ensure_path(path)
    with path.open() as file_:
        entries = file_.read().split('\n')
    expression = '|'.join(['^' + re.escape(piece)
                           for piece in entries if piece.strip()])
    return re.compile(expression)


def compile_prefix_regex(entries):
    if '(' in entries:
        # Handle deprecated data
        expression = '|'.join(['^' + re.escape(piece)
                               for piece in entries if piece.strip()])
        return re.compile(expression)
    else:
        expression = '|'.join(['^' + piece
                               for piece in entries if piece.strip()])
        return re.compile(expression)


def compile_suffix_regex(entries):
    expression = '|'.join([piece + '$' for piece in entries if piece.strip()])
    return re.compile(expression)


def compile_infix_regex(entries):
    expression = '|'.join([piece for piece in entries if piece.strip()])
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
            if not all(isinstance(attr[ORTH], unicode_)
                       for attr in token_attrs):
                raise ValueError(Errors.E055.format(key=orth, orths=token_attrs))
            described_orth = ''.join(attr[ORTH] for attr in token_attrs)
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
        batch = list(cytoolz.take(int(batch_size), items))
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


def decaying(start, stop, decay):
    """Yield an infinite series of linearly decaying values."""
    def clip(value):
        return max(value, stop) if (start > stop) else min(value, stop)
    nr_upd = 1.
    while True:
        yield clip(start * 1./(1. + decay * nr_upd))
        nr_upd += 1


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
            for i in range(random.randint(1, bufsize-len(buf))):
                buf.append(iterable.next())
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


def read_json(location):
    """Open and load JSON from file.

    location (Path): Path to JSON file.
    RETURNS (dict): Loaded JSON content.
    """
    location = ensure_path(location)
    with location.open('r', encoding='utf8') as f:
        return ujson.load(f)


def get_raw_input(description, default=False):
    """Get user input from the command line via raw_input / input.

    description (unicode): Text to display before prompt.
    default (unicode or False/None): Default value to display with prompt.
    RETURNS (unicode): User input.
    """
    additional = ' (default: %s)' % default if default else ''
    prompt = '    %s%s: ' % (description, additional)
    user_input = input_(prompt)
    return user_input


def to_bytes(getters, exclude):
    serialized = OrderedDict()
    for key, getter in getters.items():
        if key not in exclude:
            serialized[key] = getter()
    return msgpack.dumps(serialized, use_bin_type=True, encoding='utf8')


def from_bytes(bytes_data, setters, exclude):
    msg = msgpack.loads(bytes_data, raw=False)
    for key, setter in setters.items():
        if key not in exclude and key in msg:
            setter(msg[key])
    return msg


def to_disk(path, writers, exclude):
    path = ensure_path(path)
    if not path.exists():
        path.mkdir()
    for key, writer in writers.items():
        if key not in exclude:
            writer(path / key)
    return path


def from_disk(path, readers, exclude):
    path = ensure_path(path)
    for key, reader in readers.items():
        if key not in exclude:
            reader(path / key)
    return path


def print_table(data, title=None):
    """Print data in table format.

    data (dict or list of tuples): Label/value pairs.
    title (unicode or None): Title, will be printed above.
    """
    if isinstance(data, dict):
        data = list(data.items())
    tpl_row = '    {:<15}' * len(data[0])
    table = '\n'.join([tpl_row.format(l, unicode_(v)) for l, v in data])
    if title:
        print('\n    \033[93m{}\033[0m'.format(title))
    print('\n{}\n'.format(table))


def print_markdown(data, title=None):
    """Print data in GitHub-flavoured Markdown format for issues etc.

    data (dict or list of tuples): Label/value pairs.
    title (unicode or None): Title, will be rendered as headline 2.
    """
    def excl_value(value):
        # contains path, i.e. personal info
        return isinstance(value, basestring_) and Path(value).exists()

    if isinstance(data, dict):
        data = list(data.items())
    markdown = ["* **{}:** {}".format(l, unicode_(v))
                for l, v in data if not excl_value(v)]
    if title:
        print("\n## {}".format(title))
    print('\n{}\n'.format('\n'.join(markdown)))


def prints(*texts, **kwargs):
    """Print formatted message (manual ANSI escape sequences to avoid
    dependency)

    *texts (unicode): Texts to print. Each argument is rendered as paragraph.
    **kwargs: 'title' becomes coloured headline. exits=True performs sys exit.
    """
    exits = kwargs.get('exits', None)
    title = kwargs.get('title', None)
    title = '\033[93m{}\033[0m\n'.format(_wrap(title)) if title else ''
    message = '\n\n'.join([_wrap(text) for text in texts])
    print('\n{}{}\n'.format(title, message))
    if exits is not None:
        sys.exit(exits)


def _wrap(text, wrap_max=80, indent=4):
    """Wrap text at given width using textwrap module.

    text (unicode): Text to wrap. If it's a Path, it's converted to string.
    wrap_max (int): Maximum line length (indent is deducted).
    indent (int): Number of spaces for indentation.
    RETURNS (unicode): Wrapped text.
    """
    indent = indent * ' '
    wrap_width = wrap_max - len(indent)
    if isinstance(text, Path):
        text = path2str(text)
    return textwrap.fill(text, width=wrap_width, initial_indent=indent,
                         subsequent_indent=indent, break_long_words=False,
                         break_on_hyphens=False)


def minify_html(html):
    """Perform a template-specific, rudimentary HTML minification for displaCy.
    Disclaimer: NOT a general-purpose solution, only removes indentation and
    newlines.

    html (unicode): Markup to minify.
    RETURNS (unicode): "Minified" HTML.
    """
    return html.strip().replace('    ', '').replace('\n', '')


def escape_html(text):
    """Replace <, >, &, " with their HTML encoded representation. Intended to
    prevent HTML errors in rendered displaCy markup.

    text (unicode): The original text.
    RETURNS (unicode): Equivalent text to be safely used within HTML.
    """
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
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
