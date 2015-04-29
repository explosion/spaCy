"""Set up a model directory.

Requires:

    lang_data --- Rules for the tokenizer
        * prefix.txt
        * suffix.txt
        * infix.txt
        * morphs.json
        * specials.json

    corpora --- Data files
        * WordNet
        * words.sgt.prob --- Smoothed unigram probabilities
        * clusters.txt --- Output of hierarchical clustering, e.g. Brown clusters
        * vectors.tgz --- output of something like word2vec
"""
import plac
from pathlib import Path

from shutil import copyfile
from shutil import copytree
import codecs

from spacy.en import get_lex_props
from spacy.vocab import Vocab
from spacy.vocab import write_binary_vectors


def setup_tokenizer(lang_data_dir, tok_dir):
    if not tok_dir.exists():
        tok_dir.mkdir()

    for filename in ('infix.txt', 'morphs.json', 'prefix.txt', 'specials.json',
                     'suffix.txt'):
        src = lang_data_dir / filename
        dst = tok_dir / filename
        if not dst.exists():
            copyfile(str(src), str(dst))


def _read_clusters(loc):
    clusters = {}
    for line in codecs.open(str(loc), 'r', 'utf8'):
        try:
            cluster, word, freq = line.split()
        except ValueError:
            continue
        # If the clusterer has only seen the word a few times, its cluster is
        # unreliable.
        if int(freq) >= 3:
            clusters[word] = cluster
        else:
            clusters[word] = '0'
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

    vectors_src = src_dir / 'vectors.tgz'
    if vectors_src.exists():
        write_binary_vectors(str(vectors_src), str(dst_dir / 'vec.bin'))
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


def main(lang_data_dir, corpora_dir, model_dir):
    model_dir = Path(model_dir)
    lang_data_dir = Path(lang_data_dir)
    corpora_dir = Path(corpora_dir)

    assert corpora_dir.exists()
    assert lang_data_dir.exists()

    if not model_dir.exists():
        model_dir.mkdir()

    setup_tokenizer(lang_data_dir, model_dir / 'tokenizer')
    setup_vocab(corpora_dir, model_dir / 'vocab')
    if not (model_dir / 'wordnet').exists():
        copytree(str(corpora_dir / 'wordnet'), str(model_dir / 'wordnet'))


if __name__ == '__main__':
    plac.call(main)
