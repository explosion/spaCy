import os
import io
import json
import re
import os.path
from contextlib import contextmanager

from .attrs import TAG, HEAD, DEP, ENT_IOB, ENT_TYPE


def local_path(subdir):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


class MockPackage(object):
    @classmethod
    def create_or_return(cls, me_or_arg):
        return me_or_arg if isinstance(me_or_arg, cls) else me_or_arg

    def __init__(self, data_path=None):
        if data_path is None:
            data_path = local_path('data')
        self.name = None
        self.data_path = data_path
        self._root = self.data_path

    def get(self, key):
        pass

    def has_file(self, *path_parts):
        return os.path.exists(os.path.join(self._root, *path_parts))

    def file_path(self, *path_parts, **kwargs):
        return os.path.join(self._root, *path_parts)

    def dir_path(self, *path_parts, **kwargs):
        return os.path.join(self._root, *path_parts)

    def load_utf8(self, func, *path_parts, **kwargs):
        if kwargs.get('require', True):
            with io.open(self.file_path(os.path.join(*path_parts)),
                        mode='r', encoding='utf8') as f:
                return func(f)
        else:
            return None
    
    @contextmanager
    def open(self, path_parts, default=IOError):
        if isinstance(default, Exception):
            raise default

        # Enter
        file_ = io.open(self.file_path(os.path.join(*path_parts)),
                        mode='r', encoding='utf8')
        yield file_
        # Exit
        file_.close()



def get_package(name=None, data_path=None):
    return MockPackage(data_path)
    #if data_path is None:
    #    if os.environ.get('SPACY_DATA'):
    #        data_path = os.environ.get('SPACY_DATA')
    #    else:
    #        data_path = os.path.abspath(
    #            os.path.join(os.path.dirname(__file__), 'data'))

    #sputnik = Sputnik('spacy', '0.100.0')  # TODO: retrieve version
    #pool = sputnik.pool(data_path)
    #return pool.get(name or 'en_default')


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


def read_lang_data(package):
    tokenization = package.load_utf8(json.load, 'tokenizer', 'specials.json')
    prefix = package.load_utf8(read_prefix, 'tokenizer', 'prefix.txt')
    suffix = package.load_utf8(read_suffix, 'tokenizer', 'suffix.txt')
    infix = package.load_utf8(read_infix, 'tokenizer', 'infix.txt')
    return tokenization, prefix, suffix, infix


def read_prefix(fileobj):
    entries = fileobj.read().split('\n')
    expression = '|'.join(['^' + re.escape(piece) for piece in entries if piece.strip()])
    return expression


def read_suffix(fileobj):
    entries = fileobj.read().split('\n')
    expression = '|'.join([piece + '$' for piece in entries if piece.strip()])
    return expression


def read_infix(fileobj):
    entries = fileobj.read().split('\n')
    expression = '|'.join([piece for piece in entries if piece.strip()])
    return expression


# def read_tokenization(lang):
#     loc = path.join(DATA_DIR, lang, 'tokenization')
#     entries = []
#     seen = set()
#     with utf8open(loc) as file_:
#         for line in file_:
#             line = line.strip()
#             if line.startswith('#'):
#                 continue
#             if not line:
#                 continue
#             pieces = line.split()
#             chunk = pieces.pop(0)
#             assert chunk not in seen, chunk
#             seen.add(chunk)
#             entries.append((chunk, list(pieces)))
#             if chunk[0].isalpha() and chunk[0].islower():
#                 chunk = chunk[0].title() + chunk[1:]
#                 pieces[0] = pieces[0][0].title() + pieces[0][1:]
#                 seen.add(chunk)
#                 entries.append((chunk, pieces))
#     return entries


# def read_detoken_rules(lang): # Deprecated?
#     loc = path.join(DATA_DIR, lang, 'detokenize')
#     entries = []
#     with utf8open(loc) as file_:
#         for line in file_:
#             entries.append(line.strip())
#     return entries


def align_tokens(ref, indices): # Deprecated, surely?
    start = 0
    queue = list(indices)
    for token in ref:
        end = start + len(token)
        emit = []
        while queue and queue[0][1] <= end:
            emit.append(queue.pop(0))
        yield token, emit
        start = end
    assert not queue


def detokenize(token_rules, words): # Deprecated?
    """To align with treebanks, return a list of "chunks", where a chunk is a
    sequence of tokens that are separated by whitespace in actual strings. Each
    chunk should be a tuple of token indices, e.g.

    >>> detokenize(["ca<SEP>n't", '<SEP>!'], ["I", "ca", "n't", "!"])
    [(0,), (1, 2, 3)]
    """
    string = ' '.join(words)
    for subtoks in token_rules:
        # Algorithmically this is dumb, but writing a little list-based match
        # machine? Ain't nobody got time for that.
        string = string.replace(subtoks.replace('<SEP>', ' '), subtoks)
    positions = []
    i = 0
    for chunk in string.split():
        subtoks = chunk.split('<SEP>')
        positions.append(tuple(range(i, i+len(subtoks))))
        i += len(subtoks)
    return positions
