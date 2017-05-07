# coding: utf8
from __future__ import unicode_literals

import gzip
import math
from ast import literal_eval
from preshed.counter import PreshCounter

from ..vocab import write_binary_vectors
from ..compat import fix_text, path2str
from ..util import prints
from .. import util


def model(lang, model_dir, freqs_data, clusters_data, vectors_data):
    model_path = util.ensure_path(model_dir)
    freqs_path = util.ensure_path(freqs_data)
    clusters_path = util.ensure_path(clusters_data)
    vectors_path = util.ensure_path(vectors_data)
    if not freqs_path.is_file():
        prints(freqs_path, title="No frequencies file found", exits=True)
    if clusters_path and not clusters_path.is_file():
        prints(clusters_path, title="No Brown clusters file found", exits=True)
    if vectors_path and not vectors_path.is_file():
        prints(vectors_path, title="No word vectors file found", exits=True)
    vocab = util.get_lang_class(lang).Defaults.create_vocab()
    probs, oov_prob = read_probs(freqs_path)
    clusters = read_clusters(clusters_path) if clusters_path else {}
    populate_vocab(vocab, clusters, probs, oov_prob)
    create_model(model_path, vectors_path, vocab, oov_prob)


def create_model(model_path, vectors_path, vocab, oov_prob):
    vocab_path = model_path / 'vocab'
    lexemes_path = vocab_path / 'lexemes.bin'
    strings_path = vocab_path / 'strings.json'
    oov_path = vocab_path / 'oov_prob'

    if not model_path.exists():
        model_path.mkdir()
    if not vocab_path.exists():
        vocab_path.mkdir()
    vocab.dump(path2str(lexemes_path))
    with strings_path.open('w') as f:
        vocab.strings.dump(f)
    with oov_path.open('w') as f:
        f.write('%f' % oov_prob)
    if vectors_path:
        vectors_dest = vocab_path / 'vec.bin'
        write_binary_vectors(path2str(vectors_path), path2str(vectors_dest))


def read_probs(freqs_path, max_length=100, min_doc_freq=5, min_freq=200):
    counts = PreshCounter()
    total = 0
    freqs_file = check_unzip(freqs_path)
    for i, line in enumerate(freqs_file):
        freq, doc_freq, key = line.rstrip().split('\t', 2)
        freq = int(freq)
        counts.inc(i+1, freq)
        total += freq
    counts.smooth()
    log_total = math.log(total)
    freqs_file = check_unzip(freqs_path)
    probs = {}
    for line in freqs_file:
        freq, doc_freq, key = line.rstrip().split('\t', 2)
        doc_freq = int(doc_freq)
        freq = int(freq)
        if doc_freq >= min_doc_freq and freq >= min_freq and len(key) < max_length:
            word = literal_eval(key)
            smooth_count = counts.smoother(int(freq))
            probs[word] = math.log(smooth_count) - log_total
    oov_prob = math.log(counts.smoother(0)) - log_total
    return probs, oov_prob


def read_clusters(clusters_path):
    clusters = {}
    with clusters_path.open() as f:
        for line in f:
            try:
                cluster, word, freq = line.split()
                word = fix_text(word)
            except ValueError:
                continue
            # If the clusterer has only seen the word a few times, its
            # cluster is unreliable.
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


def populate_vocab(vocab, clusters, probs, oov_prob):
    # Ensure probs has entries for all words seen during clustering.
    for word in clusters:
        if word not in probs:
            probs[word] = oov_prob
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


def check_unzip(file_path):
    file_path_str = path2str(file_path)
    if file_path_str.endswith('gz'):
        return gzip.open(file_path_str)
    else:
        return file_path.open()
