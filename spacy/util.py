# coding: utf8
from __future__ import unicode_literals, print_function
import os
import io
import json
import re
import os.path
import pathlib
import sys
import textwrap


try:
    basestring
except NameError:
    basestring = str


try:
    raw_input
except NameError: # Python 3
    raw_input = input


LANGUAGES = {}
_data_path = pathlib.Path(__file__).parent / 'data'


def set_lang_class(name, cls):
    global LANGUAGES
    LANGUAGES[name] = cls


def get_lang_class(name):
    lang = re.split('[^a-zA-Z0-9]', name, 1)[0]
    if lang not in LANGUAGES:
        raise RuntimeError('Language not supported: %s' % lang)
    return LANGUAGES[lang]


def get_data_path(require_exists=True):
    if not require_exists:
        return _data_path
    else:
        return _data_path if _data_path.exists() else None


def set_data_path(path):
    global _data_path
    if isinstance(path, basestring):
        path = pathlib.Path(path)
    _data_path = path


def or_(val1, val2):
    if val1 is not None:
        return val1
    elif callable(val2):
        return val2()
    else:
        return val2


def match_best_version(target_name, target_version, path):
    path = path if not isinstance(path, basestring) else pathlib.Path(path)
    if path is None or not path.exists():
        return None
    matches = []
    for data_name in path.iterdir():
        name, version = split_data_name(data_name.parts[-1])
        if name == target_name and constraint_match(target_version, version):
            matches.append((tuple(float(v) for v in version.split('.')), data_name))
    if matches:
        return pathlib.Path(max(matches)[1])
    else:
        return None


def split_data_name(name):
    return name.split('-', 1) if '-' in name else (name, '')


def constraint_match(constraint_string, version):
    # From http://github.com/spacy-io/sputnik
    if not constraint_string:
        return True

    constraints = [c.strip() for c in constraint_string.split(',') if c.strip()]

    for c in constraints:
        if not re.match(r'[><=][=]?\d+(\.\d+)*', c):
            raise ValueError('invalid constraint: %s' % c)

    return all(semver.match(version, c) for c in constraints)


def read_regex(path):
    path = path if not isinstance(path, basestring) else pathlib.Path(path)
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


def utf8open(loc, mode='r'):
    return io.open(loc, mode, encoding='utf8')


def check_renamed_kwargs(renamed, kwargs):
    for old, new in renamed.items():
        if old in kwargs:
            raise TypeError("Keyword argument %s now renamed to %s" % (old, new))


def is_windows():
    """Check if user is on Windows."""
    return sys.platform.startswith('win')


def is_python2():
    """Check if Python 2 is used."""
    return sys.version.startswith('2.')


def parse_package_meta(package_path, package, require=True):
    location = os.path.join(str(package_path), package, 'meta.json')
    if os.path.isfile(location):
        with io.open(location, encoding='utf8') as f:
            meta = json.load(f)
            return meta
    elif require:
        raise IOError("Could not read meta.json from %s" % location)
    else:
        return None


def get_raw_input(description, default=False):
    """Get user input via raw_input / input and return input value. Takes a
    description for the prompt, and an optional default value that's displayed
    with the prompt."""

    additional = ' (default: {d})'.format(d=default) if default else ''
    prompt = '    {d}{a}: '.format(d=description, a=additional)
    user_input = raw_input(prompt)
    return user_input


def print_table(data, **kwargs):
    """Print data in table format. Can either take a list of tuples or a
    dictionary, which will be converted to a list of tuples."""

    if type(data) == dict:
        data = list(data.items())

    tpl_msg = '\n{msg}\n'
    tpl_title = '\n    \033[93m{msg}\033[0m'
    tpl_row ="    {:<15}" * len(data[0])
    table = '\n'.join([tpl_row.format(l, v) for l, v in data])

    if 'title' in kwargs and kwargs['title']:
        print(tpl_title.format(msg=kwargs['title']))

    print(tpl_msg.format(msg=table))


def print_markdown(data, **kwargs):
    """Print listed data in GitHub-flavoured Markdown format so it can be
    copy-pasted into issues. Can either take a list of tuples or a dictionary,
    which will be converted to a list of tuples."""

    def excl_value(value):
        # don't print value if it contains absolute path of directory
        # (i.e. personal info that shouldn't need to be shared)
        # other conditions can be included here if necessary
        if str(pathlib.Path(__file__).parent) in value:
            return True

    if type(data) == dict:
        data = list(data.items())

    tpl_msg = "\n{msg}\n"
    tpl_title = "\n## {msg}"
    tpl_row = "* **{l}:** {v}"
    markdown = '\n'.join([tpl_row.format(l=l, v=v) for l, v in data if not excl_value(v)])

    if 'title' in kwargs and kwargs['title']:
        print(tpl_title.format(msg=kwargs['title']))

    print(tpl_msg.format(msg=markdown))


def print_msg(*text, **kwargs):
    """Print formatted message. Each positional argument is rendered as newline-
    separated paragraph. If kwarg 'title' exist, title is printed above the text
    and highlighted (using ANSI escape sequences manually to avoid unnecessary
    dependency)."""

    message = '\n\n'.join([_wrap_text(t) for t in text])
    tpl_msg = '\n{msg}\n'
    tpl_title = '\n\033[93m{msg}\033[0m'

    if 'title' in kwargs and kwargs['title']:
        title = _wrap_text(kwargs['title'])
        print(tpl_title.format(msg=title))
    print(tpl_msg.format(msg=message))


def _wrap_text(text):
    """Wrap text at given width using textwrap module. Indent should consist of
    spaces. Its length is deducted from wrap width to ensure exact wrapping."""

    wrap_max = 80
    indent = '    '
    wrap_width = wrap_max - len(indent)
    return textwrap.fill(text, width=wrap_width, initial_indent=indent,
                               subsequent_indent=indent, break_long_words=False,
                               break_on_hyphens=False)


def sys_exit(*messages, **kwargs):
    """Performs SystemExit. For modules used from the command line, like
    download and link. To print message, use the same arguments as for
    print_msg()."""

    if messages:
        print_msg(*messages, **kwargs)
    sys.exit(0)
