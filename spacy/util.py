# coding: utf8
from __future__ import unicode_literals, print_function

import ujson
import pip
import importlib
import regex as re
from pathlib import Path
import sys
import textwrap

from .symbols import ORTH
from .compat import path2str, basestring_, input_, unicode_


LANGUAGES = {}
_data_path = Path(__file__).parent / 'data'


def set_lang_class(name, cls):
    global LANGUAGES
    LANGUAGES[name] = cls


def get_lang_class(name):
    if name in LANGUAGES:
        return LANGUAGES[name]
    lang = re.split('[^a-zA-Z0-9]', name, 1)[0]
    if lang not in LANGUAGES:
        raise RuntimeError('Language not supported: %s' % name)
    return LANGUAGES[lang]


def get_data_path(require_exists=True):
    if not require_exists:
        return _data_path
    else:
        return _data_path if _data_path.exists() else None


def set_data_path(path):
    global _data_path
    _data_path = ensure_path(path)


def ensure_path(path):
    if isinstance(path, basestring_):
        return Path(path)
    else:
        return path


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
    exc = dict(base_exceptions)
    for additions in addition_dicts:
        for orth, token_attrs in additions.items():
            if not all(isinstance(attr[ORTH], unicode_) for attr in token_attrs):
                msg = "Invalid value for ORTH in exception: key='%s', orths='%s'"
                raise ValueError(msg % (orth, token_attrs))
            described_orth = ''.join(attr[ORTH] for attr in token_attrs)
            if orth != described_orth:
                # TODO: Better error
                msg = "Invalid tokenizer exception: key='%s', orths='%s'"
                raise ValueError(msg % (orth, described_orth))
        # overlap = set(exc.keys()).intersection(set(additions))
        # assert not overlap, overlap
        exc.update(additions)
    expand_exc(exc, "'", "’")
    return exc


def expand_exc(excs, search, replace):
    def _fix_token(token, search, replace):
        fixed = dict(token)
        fixed[ORTH] = fixed[ORTH].replace(search, replace)
        return fixed
    updates = {}
    for token_string, tokens in excs.items():
        if search in token_string:
            new_key = token_string.replace(search, replace)
            new_value = [_fix_token(t, search, replace) for t in tokens]
            updates[new_key] = new_value
    return updates


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


def check_renamed_kwargs(renamed, kwargs):
    for old, new in renamed.items():
        if old in kwargs:
            raise TypeError("Keyword argument %s now renamed to %s" % (old, new))


def read_json(location):
    with location.open('r', encoding='utf8') as f:
        return ujson.load(f)


def resolve_model_path(name):
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


def is_package(origin):
    """
    Check if string maps to a package installed via pip.
    """
    packages = pip.get_installed_distributions()
    for package in packages:
        if package.project_name.replace('-', '_') == origin:
            return True
    return False


def get_model_package_path(package_name):
    # Here we're importing the module just to find it. This is worryingly
    # indirect, but it's otherwise very difficult to find the package.
    # Python's installation and import rules are very complicated.
    pkg = importlib.import_module(package_name)
    package_path = Path(pkg.__file__).parent.parent
    meta = parse_package_meta(package_path / package_name)
    model_name = '%s-%s' % (package_name, meta['version'])
    return package_path / package_name / model_name


def parse_package_meta(package_path, require=True):
    """
    Check if a meta.json exists in a package and return its contents as a
    dictionary. If require is set to True, raise an error if no meta.json found.
    """
    location = package_path / 'meta.json'
    if location.is_file():
        return read_json(location)
    elif require:
        raise IOError("Could not read meta.json from %s" % location)
    else:
        return None


def get_raw_input(description, default=False):
    """
    Get user input via raw_input / input and return input value. Takes a
    description, and an optional default value to display with the prompt.
    """
    additional = ' (default: %s)' % default if default else ''
    prompt = '    %s%s: ' % (description, additional)
    user_input = input_(prompt)
    return user_input


def print_table(data, title=None):
    """
    Print data in table format. Can either take a list of tuples or a
    dictionary, which will be converted to a list of tuples.
    """
    if type(data) == dict:
        data = list(data.items())
    tpl_row = '    {:<15}' * len(data[0])
    table = '\n'.join([tpl_row.format(l, v) for l, v in data])
    if title:
        print('\n    \033[93m{}\033[0m'.format(title))
    print('\n{}\n'.format(table))


def print_markdown(data, title=None):
    """
    Print listed data in GitHub-flavoured Markdown format so it can be
    copy-pasted into issues. Can either take a list of tuples or a dictionary.
    """
    def excl_value(value):
        return Path(value).exists() # contains path (personal info)

    if type(data) == dict:
        data = list(data.items())
    markdown = ["* **{}:** {}".format(l, v) for l, v in data if not excl_value(v)]
    if title:
        print("\n## {}".format(title))
    print('\n{}\n'.format('\n'.join(markdown)))


def prints(*texts, **kwargs):
    """
    Print formatted message. Each positional argument is rendered as newline-
    separated paragraph. An optional highlighted title is printed above the text
    (using ANSI escape sequences manually to avoid unnecessary dependency).
    """
    exits = kwargs.get('exits', False)
    title = kwargs.get('title', None)
    title = '\033[93m{}\033[0m\n'.format(_wrap(title)) if title else ''
    message = '\n\n'.join([_wrap(text) for text in texts])
    print('\n{}{}\n'.format(title, message))
    if exits:
        sys.exit(0)


def _wrap(text, wrap_max=80, indent=4):
    """
    Wrap text at given width using textwrap module. Indent should consist of
    spaces. Its length is deducted from wrap width to ensure exact wrapping.
    """
    indent = indent * ' '
    wrap_width = wrap_max - len(indent)
    if isinstance(text, Path):
        text = path2str(text)
    return textwrap.fill(text, width=wrap_width, initial_indent=indent,
                         subsequent_indent=indent, break_long_words=False,
                         break_on_hyphens=False)
