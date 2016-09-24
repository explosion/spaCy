from sputnik.dir_package import DirPackage
from sputnik.package_list import (PackageNotFoundException,
                                  CompatiblePackageNotFoundException)

import sputnik
from . import about


def get_package(data_dir):
    if not isinstance(data_dir, six.string_types):
        raise RuntimeError('data_dir must be a string')
    return DirPackage(data_dir)


def get_package_by_name(name=None, via=None):
    if name is None:
        return
    lang = get_lang_class(name)
    try:
        return sputnik.package(about.__title__, about.__version__,
            name, data_path=via)
    except PackageNotFoundException as e:
        raise RuntimeError("Model '%s' not installed. Please run 'python -m "
                           "%s.download' to install latest compatible "
                           "model." % (name, lang.__module__))
    except CompatiblePackageNotFoundException as e:
        raise RuntimeError("Installed model is not compatible with spaCy "
                           "version. Please run 'python -m %s.download "
                           "--force' to install latest compatible model." %
                           (lang.__module__))




def read_lang_data(package):
    tokenization = package.load_json(('tokenizer', 'specials.json'))
    with package.open(('tokenizer', 'prefix.txt'), default=None) as file_:
        prefix = read_prefix(file_) if file_ is not None else None
    with package.open(('tokenizer', 'suffix.txt'), default=None) as file_:
        suffix = read_suffix(file_) if file_ is not None else None
    with package.open(('tokenizer', 'infix.txt'), default=None) as file_:
        infix = read_infix(file_) if file_ is not None else None
    return tokenization, prefix, suffix, infix



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



