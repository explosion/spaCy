# coding: utf8
from __future__ import unicode_literals, print_function

import os
import ujson
import pip
import importlib
import regex as re
from pathlib import Path
import sys
import textwrap
import random

from .symbols import ORTH
from .compat import cupy, CudaStream, path2str, basestring_, input_, unicode_


LANGUAGES = {}
_data_path = Path(__file__).parent / 'data'


def get_lang_class(lang):
    """Import and load a Language class.

    lang (unicode): Two-letter language code, e.g. 'en'.
    RETURNS (Language): Language class.
    """
    global LANGUAGES
    if not lang in LANGUAGES:
        try:
            module = importlib.import_module('.lang.%s' % lang, 'spacy')
        except ImportError:
            raise ImportError("Can't import language %s from spacy.lang." %lang)
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


def resolve_model_path(name):
    """Resolve a model name or string to a model path.

    name (unicode): Package name, shortcut link or model path.
    RETURNS (Path): Path to model data directory.
    """
    data_path = get_data_path()
    if not data_path or not data_path.exists():
        raise IOError("Can't find spaCy data path: %s" % path2str(data_path))
    if isinstance(name, basestring_):
        if (data_path / name).exists(): # in data dir or shortcut link
            return (data_path / name)
        if is_package(name): # installed as a package
            return get_model_package_path(name)
        if Path(name).exists(): # path to model
            return Path(name)
    elif hasattr(name, 'exists'): # Path or Path-like object
        return name
    raise IOError("Can't find model '%s'" % name)


def is_package(name):
    """Check if string maps to a package installed via pip.

    name (unicode): Name of package.
    RETURNS (bool): True if installed package, False if not.
    """
    packages = pip.get_installed_distributions()
    for package in packages:
        if package.project_name.replace('-', '_') == name:
            return True
    return False


def get_model_package_path(package_name):
    """Get path to a model package installed via pip.

    package_name (unicode): Name of installed package.
    RETURNS (Path): Path to model data directory.
    """
    # Here we're importing the module just to find it. This is worryingly
    # indirect, but it's otherwise very difficult to find the package.
    # Python's installation and import rules are very complicated.
    pkg = importlib.import_module(package_name)
    package_path = Path(pkg.__file__).parent.parent
    meta = parse_package_meta(package_path / package_name)
    model_name = '%s-%s' % (package_name, meta['version'])
    return package_path / package_name / model_name


def parse_package_meta(package_path, require=True):
    """Check if a meta.json exists in a package and return its contents.

    package_path (Path): Path to model package directory.
    require (bool): If True, raise error if no meta.json is found.
    RETURNS (dict or None): Model meta.json data or None.
    """
    location = package_path / 'meta.json'
    if location.is_file():
        return read_json(location)
    elif require:
        raise IOError("Could not read meta.json from %s" % location)
    else:
        return None


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
    # TODO: Error and tell to install chainer if not found
    # Requires GPU
    return CudaStream() if CudaStream is not None else None


def get_async(stream, numpy_array):
    if cupy is None:
        return numpy_array
    else:
        array = cupy.ndarray(numpy_array.shape, order='C',
                           dtype=numpy_array.dtype)
        array.set(numpy_array, stream=stream)
        return array

def itershuffle(iterable, bufsize=1000):
    """Shuffle an iterator. This works by holding `bufsize` items back
    and yielding them sometime later. Obviously, this is not unbiased --
    but should be good enough for batching. Larger bufsize means less bias.

    From https://gist.github.com/andres-erbsen/1307752
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


def env_opt(name, default=None):
    if type(default) is float:
        type_convert = float
    else:
        type_convert = int
    if 'SPACY_' + name.upper() in os.environ:
        value = type_convert(os.environ['SPACY_' + name.upper()])
        print(name, "=", repr(value), "via", "$SPACY_" + name.upper())
        return value
    elif name in os.environ:
        value = type_convert(os.environ[name])
        print(name, "=", repr(value), "via", '$' + name)
        return value
    else:
        print(name, '=', repr(default), "by default")
        return default


def read_regex(path):
    path = ensure_path(path)
    with path.open() as file_:
        entries = file_.read().split('\n')
    expression = '|'.join(['^' + re.escape(piece) for piece in entries if piece.strip()])
    return re.compile(expression)


def compile_prefix_regex(entries):
    if '(' in entries:
        # Handle deprecated data
        expression = '|'.join(['^' + re.escape(piece) for piece in entries if piece.strip()])
        return re.compile(expression)
    else:
        expression = '|'.join(['^' + piece for piece in entries if piece.strip()])
        return re.compile(expression)


def compile_suffix_regex(entries):
    expression = '|'.join([piece + '$' for piece in entries if piece.strip()])
    return re.compile(expression)


def compile_infix_regex(entries):
    expression = '|'.join([piece for piece in entries if piece.strip()])
    return re.compile(expression)


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
                msg = "Invalid value for ORTH in exception: key='%s', orths='%s'"
                raise ValueError(msg % (orth, token_attrs))
            described_orth = ''.join(attr[ORTH] for attr in token_attrs)
            if orth != described_orth:
                raise ValueError("Invalid tokenizer exception: ORTH values "
                                 "combined don't match original string. "
                                 "key='%s', orths='%s'" % (orth, described_orth))
        # overlap = set(exc.keys()).intersection(set(additions))
        # assert not overlap, overlap
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
        raise ValueError("Stepped slices not supported in Span objects."
                         "Try: list(tokens)[start:stop:step] instead.")
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

    assert 0 <= start <= stop <= length
    return start, stop


def compounding(start, stop, compound):
    '''Yield an infinite series of compounding values. Each time the
    generator is called, a value is produced by multiplying the previous
    value by the compound rate.

    EXAMPLE

      >>> sizes = compounding(1., 10., 1.5)
      >>> assert next(sizes) == 1.
      >>> assert next(sizes) == 1 * 1.5
      >>> assert next(sizes) == 1.5 * 1.5
    '''
    def clip(value):
        return max(value, stop) if (start>stop) else min(value, start)
    curr = float(start)
    while True:
        yield clip(curr)
        curr *= compound


def decaying(start, stop, decay):
    '''Yield an infinite series of linearly decaying values.'''
    def clip(value):
        return max(value, stop) if (start>stop) else min(value, start)
    nr_upd = 1.
    while True:
        yield clip(start * 1./(1. + decay * nr_upd))
        nr_upd += 1


def check_renamed_kwargs(renamed, kwargs):
    for old, new in renamed.items():
        if old in kwargs:
            raise TypeError("Keyword argument %s now renamed to %s" % (old, new))


def read_json(location):
    """Open and load JSON from file.

    location (Path): Path to JSON file.
    RETURNS (dict): Loaded JSON content.
    """
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


def print_table(data, title=None):
    """Print data in table format.

    data (dict or list of tuples): Label/value pairs.
    title (unicode or None): Title, will be printed above.
    """
    if isinstance(data, dict):
        data = list(data.items())
    tpl_row = '    {:<15}' * len(data[0])
    table = '\n'.join([tpl_row.format(l, v) for l, v in data])
    if title:
        print('\n    \033[93m{}\033[0m'.format(title))
    print('\n{}\n'.format(table))


def print_markdown(data, title=None):
    """Print data in GitHub-flavoured Markdown format for issues etc.

    data (dict or list of tuples): Label/value pairs.
    title (unicode or None): Title, will be rendered as headline 2.
    """
    def excl_value(value):
        return Path(value).exists() # contains path (personal info)

    if isinstance(data, dict):
        data = list(data.items())
    markdown = ["* **{}:** {}".format(l, v) for l, v in data if not excl_value(v)]
    if title:
        print("\n## {}".format(title))
    print('\n{}\n'.format('\n'.join(markdown)))


def prints(*texts, **kwargs):
    """Print formatted message (manual ANSI escape sequences to avoid dependency)

    *texts (unicode): Texts to print. Each argument is rendered as paragraph.
    **kwargs: 'title' becomes coloured headline. 'exits'=True performs sys exit.
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
    Disclaimer: NOT a general-purpose solution, only removes indentation/newlines.

    html (unicode): Markup to minify.
    RETURNS (unicode): "Minified" HTML.
    """
    return html.strip().replace('    ', '').replace('\n', '')
