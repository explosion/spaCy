"""Set up a model dir, given the (committed) lang_data."""
import plac
from pathlib import Path

from shutil import copyfile
import codecs

from spacy.en import get_lex_props
from spacy.vocab import Vocab


def setup_tokenizer(lang_data_dir, tok_dir):
    if not tok_dir.exists():
        tok_dir.mkdir()

    for filename in ('infix.txt', 'morphs.json', 'prefix.txt', 'specials.json',
                     'suffix.txt'):
        src = lang_data_dir / filename
        dst = tok_dir / filename
        if not dst.exists():
            copyfile(src, dst)


def _read_clusters(loc):
    clusters = {}
    for line in codecs.open(str(loc), 'r', 'utf8'):
        try:
            cluster, word, freq = line.split()
        except ValueError:
            continue
        clusters[word] = cluster
    return clusters


def _read_probs(loc):
    probs = {}
    for i, line in enumerate(codecs.open(str(loc), 'r', 'utf8')):
        prob, word = line.split()
        prob = float(prob)
        probs[word] = prob
    return probs



def setup_vocab(src_dir, dst_dir):
    if not dst_dir.exists():
        dst_dir.mkdir()
    vocab = Vocab(data_dir=None, get_lex_props=get_lex_props)
    clusters = _read_clusters(src_dir / 'clusters.txt')
    probs = _read_probs(src_dir / 'words.sgt.prob')
    lexicon = []
    for word, prob in reversed(sorted(probs.items(), key=lambda item: item[1])):
        entry = get_lex_props(word)
        if word in clusters or float(prob) >= -17:
            entry['prob'] = float(prob)
            cluster = clusters.get(word, '0')
            # Decode as a little-endian string, so that we can do & 15 to get
            # the first 4 bits. See _parse_features.pyx
            entry['cluster'] = int(cluster[::-1], 2)
            vocab[word] = entry
    vocab.dump(str(dst_dir / 'lexemes.bin'))
    vocab.strings.dump(str(dst_dir / 'strings.txt'))


def main(lang_data_dir, model_dir):
    model_dir = Path(model_dir)
    lang_data_dir = Path(lang_data_dir)

    if not model_dir.exists():
        model_dir.mkdir()

    setup_tokenizer(lang_data_dir, model_dir / 'tokenizer')
    setup_vocab(lang_data_dir, model_dir / 'vocab')


if __name__ == '__main__':
    plac.call(main)
