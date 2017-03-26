# coding: utf8
from __future__ import unicode_literals

import gzip
import math
from ast import literal_eval
from pathlib import Path
from preshed.counter import PreshCounter

from ..vocab import write_binary_vectors
from .. import util


def model(lang, model_dir, freqs_data, clusters_data, vectors_data):
    model_path = Path(model_dir)
    freqs_path = Path(freqs_data)
    clusters_path = Path(clusters_data) if clusters_data else None
    vectors_path = Path(vectors_data) if vectors_data else None

    check_dirs(freqs_path, clusters_path, vectors_path)
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
    vocab.dump(lexemes_path.as_posix())
    with strings_path.open('w') as f:
        vocab.strings.dump(f)
    with oov_path.open('w') as f:
        f.write('%f' % oov_prob)
    if vectors_path:
        vectors_dest = model_path / 'vec.bin'
        write_binary_vectors(vectors_path.as_posix(), vectors_dest.as_posix())


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


def populate_vocab(vocab, clusters, probs, oov_probs):
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
    file_path_str = file_path.as_posix()
    if file_path_str.endswith('gz'):
        return gzip.open(file_path_str)
    else:
        return file_path.open()


def check_dirs(freqs_data, clusters_data, vectors_data):
    if not freqs_data.is_file():
        util.sys_exit(freqs_data.as_posix(), title="No frequencies file found")
    if clusters_data and not clusters_data.is_file():
        util.sys_exit(clusters_data.as_posix(), title="No Brown clusters file found")
    if vectors_data and not vectors_data.is_file():
        util.sys_exit(vectors_data.as_posix(), title="No word vectors file found")
