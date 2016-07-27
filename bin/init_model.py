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
        * vectors.bz2 --- output of something like word2vec, compressed with bzip
"""
from __future__ import unicode_literals

from ast import literal_eval
import math
import gzip
import json

import plac
from pathlib import Path

from shutil import copyfile
from shutil import copytree
from collections import defaultdict
import io

from spacy.vocab import Vocab
from spacy.vocab import write_binary_vectors
from spacy.strings import hash_string
from preshed.counter import PreshCounter

from spacy.parts_of_speech import NOUN, VERB, ADJ
from spacy.util import get_lang_class


try:
    unicode
except NameError:
    unicode = str


def setup_tokenizer(lang_data_dir, tok_dir):
    if not tok_dir.exists():
        tok_dir.mkdir()

    for filename in ('infix.txt', 'morphs.json', 'prefix.txt', 'specials.json',
                     'suffix.txt'):
        src = lang_data_dir / filename
        dst = tok_dir / filename
        copyfile(str(src), str(dst))


def _read_clusters(loc):
    if not loc.exists():
        print("Warning: Clusters file not found")
        return {}
    clusters = {}
    for line in io.open(str(loc), 'r', encoding='utf8'):
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
    # Expand clusters with re-casing
    for word, cluster in list(clusters.items()):
        if word.lower() not in clusters:
            clusters[word.lower()] = cluster
        if word.title() not in clusters:
            clusters[word.title()] = cluster
        if word.upper() not in clusters:
            clusters[word.upper()] = cluster
    return clusters


def _read_probs(loc):
    if not loc.exists():
        print("Probabilities file not found. Trying freqs.")
        return {}, 0.0
    probs = {}
    for i, line in enumerate(io.open(str(loc), 'r', encoding='utf8')):
        prob, word = line.split()
        prob = float(prob)
        probs[word] = prob
    return probs, probs['-OOV-']


def _read_freqs(loc, max_length=100, min_doc_freq=5, min_freq=200):
    if not loc.exists():
        print("Warning: Frequencies file not found")
        return {}, 0.0
    counts = PreshCounter()
    total = 0
    if str(loc).endswith('gz'):
        file_ = gzip.open(str(loc))
    else:
        file_ = loc.open()
    for i, line in enumerate(file_):
        freq, doc_freq, key = line.rstrip().split('\t', 2)
        freq = int(freq)
        counts.inc(i+1, freq)
        total += freq
    counts.smooth()
    log_total = math.log(total)
    if str(loc).endswith('gz'):
        file_ = gzip.open(str(loc))
    else:
        file_ = loc.open()
    probs = {}
    for line in file_:
        freq, doc_freq, key = line.rstrip().split('\t', 2)
        doc_freq = int(doc_freq)
        freq = int(freq)
        if doc_freq >= min_doc_freq and freq >= min_freq and len(key) < max_length:
            word = literal_eval(key)
            smooth_count = counts.smoother(int(freq))
            probs[word] = math.log(smooth_count) - log_total
    oov_prob = math.log(counts.smoother(0)) - log_total
    return probs, oov_prob


def _read_senses(loc):
    lexicon = defaultdict(lambda: defaultdict(list))
    if not loc.exists():
        print("Warning: WordNet senses not found")
        return lexicon
    sense_names = dict((s, i) for i, s in enumerate(spacy.senses.STRINGS))
    pos_ids = {'noun': NOUN, 'verb': VERB, 'adjective': ADJ}
    for line in codecs.open(str(loc), 'r', 'utf8'):
        sense_strings = line.split()
        word = sense_strings.pop(0)
        for sense in sense_strings:
            pos, sense = sense[3:].split('.')
            sense_name = '%s_%s' % (pos[0].upper(), sense.lower())
            if sense_name != 'N_tops':
                sense_id = sense_names[sense_name]
                lexicon[word][pos_ids[pos]].append(sense_id)
    return lexicon


def setup_vocab(get_lex_attr, tag_map, src_dir, dst_dir):
    if not dst_dir.exists():
        dst_dir.mkdir()

    vectors_src = src_dir / 'vectors.bz2'
    if vectors_src.exists():
        write_binary_vectors(str(vectors_src), str(dst_dir / 'vec.bin'))
    else:
        print("Warning: Word vectors file not found")
    vocab = Vocab(get_lex_attr=get_lex_attr, tag_map=tag_map)
    clusters = _read_clusters(src_dir / 'clusters.txt')
    probs, oov_prob = _read_probs(src_dir / 'words.sgt.prob')
    if not probs:
        probs, oov_prob = _read_freqs(src_dir / 'freqs.txt.gz')
    if not probs:
        oov_prob = -20
    else:
        oov_prob = min(probs.values())
    for word in clusters:
        if word not in probs:
            probs[word] = oov_prob

    lexicon = []
    for word, prob in reversed(sorted(list(probs.items()), key=lambda item: item[1])):
        # First encode the strings into the StringStore. This way, we can map
        # the orth IDs to frequency ranks
        orth = vocab.strings[word]
    # Now actually load the vocab
    for word, prob in reversed(sorted(list(probs.items()), key=lambda item: item[1])):
        lexeme = vocab[word]
        lexeme.prob = prob
        lexeme.is_oov = False
        # Decode as a little-endian string, so that we can do & 15 to get
        # the first 4 bits. See _parse_features.pyx
        if word in clusters:
            lexeme.cluster = int(clusters[word][::-1], 2)
        else:
            lexeme.cluster = 0
    vocab.dump(str(dst_dir / 'lexemes.bin'))
    with (dst_dir / 'strings.json').open('w') as file_:
        vocab.strings.dump(file_)
    with (dst_dir / 'oov_prob').open('w') as file_:
        file_.write('%f' % oov_prob)


def main(lang_id, lang_data_dir, corpora_dir, model_dir):
    model_dir = Path(model_dir)
    lang_data_dir = Path(lang_data_dir) / lang_id
    corpora_dir = Path(corpora_dir) / lang_id

    assert corpora_dir.exists()
    assert lang_data_dir.exists()

    if not model_dir.exists():
        model_dir.mkdir()

    tag_map = json.load((lang_data_dir / 'tag_map.json').open())
    setup_tokenizer(lang_data_dir, model_dir / 'tokenizer')
    setup_vocab(get_lang_class(lang_id).default_lex_attrs(), tag_map, corpora_dir,
                model_dir / 'vocab')

    if (lang_data_dir / 'gazetteer.json').exists():
        copyfile(str(lang_data_dir / 'gazetteer.json'),
                 str(model_dir / 'vocab' / 'gazetteer.json'))

    copyfile(str(lang_data_dir / 'tag_map.json'),
             str(model_dir / 'vocab' / 'tag_map.json'))

    if (lang_data_dir / 'lemma_rules.json').exists():
        copyfile(str(lang_data_dir / 'lemma_rules.json'),
                 str(model_dir / 'vocab' / 'lemma_rules.json'))

    if not (model_dir / 'wordnet').exists() and (corpora_dir / 'wordnet').exists():
        copytree(str(corpora_dir / 'wordnet' / 'dict'), str(model_dir / 'wordnet'))


if __name__ == '__main__':
    plac.call(main)
