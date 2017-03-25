from pathlib import Path
from . import about
from . import util
from .cli import download
from .cli import link


try:
    basestring
except NameError:
    basestring = str


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


def fix_glove_vectors_loading(overrides):
    """Special-case hack for loading the GloVe vectors, to support deprecated
    <1.0 stuff. Phase this out once the data is fixed."""

    if 'data_dir' in overrides and 'path' not in overrides:
        raise ValueError("The argument 'data_dir' has been renamed to 'path'")
    if overrides.get('path') is False:
        return overrides
    if overrides.get('path') in (None, True):
        data_path = util.get_data_path()
    else:
        path = overrides['path']
        if isinstance(path, basestring):
            path = Path(path)
        data_path = path.parent
    vec_path = None
    if 'add_vectors' not in overrides:
        if 'vectors' in overrides:
            vec_path = util.match_best_version(overrides['vectors'], None, data_path)
            if vec_path is None:
                return overrides
        else:
            vec_path = util.match_best_version('en_glove_cc_300_1m_vectors', None, data_path)
        if vec_path is not None:
            vec_path = vec_path / 'vocab' / 'vec.bin'
    if vec_path is not None:
        overrides['add_vectors'] = lambda vocab: vocab.load_vectors_from_bin_loc(vec_path)
    return overrides


def resolve_model_name(name):
    """If spaCy is loaded with 'de', check if symlink already exists. If
    not, user have upgraded from older version and have old models installed.
    Check if old model directory exists and if so, return that instead and create
    shortcut link. If English model is found and no shortcut exists, raise error
    and tell user to install new model.
    """

    if name == 'en' or name == 'de':
        versions = ['1.0.0', '1.1.0']
        data_path = Path(util.get_data_path())
        model_path = data_path / name
        v_model_paths = [data_path / Path(name + '-' + v) for v in versions]

        if not model_path.exists(): # no shortcut found
            for v_path in v_model_paths:
                if v_path.exists(): # versioned model directory found
                    if name == 'de':
                        link(v_path, name)
                        return name
                    else:
                        raise ValueError(
                            "Found English model at {p}. This model is not "
                            "compatible with the current version. See "
                            "https://spacy.io/docs/usage/models to download the "
                            "new model.".format(p=v_path))
    return name


class ModelDownload():
    """Replace download modules within en and de with deprecation warning and
    download default language model (using shortcut). Use classmethods to allow
    importing ModelDownload as download and calling download.en() etc."""

    @classmethod
    def load(self, lang):
        util.print_msg(
            "The spacy.{l}.download command is now deprecated. Please use "
            "python -m spacy download [model name or shortcut] instead. For more "
            "info and available models, see the documentation: {d}. "
            "Downloading default '{l}' model now...".format(d=about.__docs__, l=lang),
            title="Warning: deprecated command")
        download(lang)

    @classmethod
    def en(cls, *args, **kwargs):
        cls.load('en')

    @classmethod
    def de(cls, *args, **kwargs):
        cls.load('de')
