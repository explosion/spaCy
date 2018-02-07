# coding: utf8
from __future__ import unicode_literals

import plac
import math
from tqdm import tqdm
import numpy
from ast import literal_eval
from pathlib import Path
from preshed.counter import PreshCounter

from ..compat import fix_text
from ..vectors import Vectors
from ..util import prints, ensure_path, get_lang_class


@plac.annotations(
    lang=("model language", "positional", None, str),
    output_dir=("model output directory", "positional", None, Path),
    freqs_loc=("location of words frequencies file", "positional", None, Path),
    clusters_loc=("optional: location of brown clusters data",
                  "option", "c", str),
    vectors_loc=("optional: location of vectors file in GenSim text format",
                 "option", "v", str),
    prune_vectors=("optional: number of vectors to prune to",
                   "option", "V", int)
)
def init_model(lang, output_dir, freqs_loc, clusters_loc=None, vectors_loc=None, prune_vectors=-1):
    """
    Create a new model from raw data, like word frequencies, Brown clusters
    and word vectors.
    """
    if not freqs_loc.exists():
        prints(freqs_loc, title="Can't find words frequencies file", exits=1)
    clusters_loc = ensure_path(clusters_loc)
    vectors_loc = ensure_path(vectors_loc)

    probs, oov_prob = read_freqs(freqs_loc)
    vectors_data, vector_keys = read_vectors(vectors_loc) if vectors_loc else (None, None)
    clusters = read_clusters(clusters_loc) if clusters_loc else {}

    nlp = create_model(lang, probs, oov_prob, clusters, vectors_data, vector_keys, prune_vectors)

    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    return nlp


def create_model(lang, probs, oov_prob, clusters, vectors_data, vector_keys, prune_vectors):
    print("Creating model...")
    lang_class = get_lang_class(lang)
    nlp = lang_class()
    for lexeme in nlp.vocab:
        lexeme.rank = 0

    lex_added = 0
    for i, (word, prob) in enumerate(tqdm(sorted(probs.items(), key=lambda item: item[1], reverse=True))):
        lexeme = nlp.vocab[word]
        lexeme.rank = i
        lexeme.prob = prob
        lexeme.is_oov = False
        # Decode as a little-endian string, so that we can do & 15 to get
        # the first 4 bits. See _parse_features.pyx
        if word in clusters:
            lexeme.cluster = int(clusters[word][::-1], 2)
        else:
            lexeme.cluster = 0
        lex_added += 1
    nlp.vocab.cfg.update({'oov_prob': oov_prob})

    if len(vectors_data):
        nlp.vocab.vectors = Vectors(data=vectors_data, keys=vector_keys)
    if prune_vectors >= 1:
        nlp.vocab.prune_vectors(prune_vectors)
    vec_added = len(nlp.vocab.vectors)

    prints("{} entries, {} vectors".format(lex_added, vec_added),
           title="Sucessfully compiled vocab")
    return nlp


def read_vectors(vectors_loc):
    print("Reading vectors...")
    with vectors_loc.open() as f:
        shape = tuple(int(size) for size in f.readline().split())
        vectors_data = numpy.zeros(shape=shape, dtype='f')
        vectors_keys = []
        for i, line in enumerate(tqdm(f)):
            pieces = line.split()
            word = pieces.pop(0)
            vectors_data[i] = numpy.array([float(val_str) for val_str in pieces], dtype='f')
            vectors_keys.append(word)
    return vectors_data, vectors_keys


def read_freqs(freqs_loc, max_length=100, min_doc_freq=5, min_freq=50):
    print("Counting frequencies...")
    counts = PreshCounter()
    total = 0
    with freqs_loc.open() as f:
        for i, line in enumerate(f):
            freq, doc_freq, key = line.rstrip().split('\t', 2)
            freq = int(freq)
            counts.inc(i + 1, freq)
            total += freq
    counts.smooth()
    log_total = math.log(total)
    probs = {}
    with freqs_loc.open() as f:
        for line in tqdm(f):
            freq, doc_freq, key = line.rstrip().split('\t', 2)
            doc_freq = int(doc_freq)
            freq = int(freq)
            if doc_freq >= min_doc_freq and freq >= min_freq and len(key) < max_length:
                word = literal_eval(key)
                smooth_count = counts.smoother(int(freq))
                probs[word] = math.log(smooth_count) - log_total
    oov_prob = math.log(counts.smoother(0)) - log_total
    return probs, oov_prob


def read_clusters(clusters_loc):
    print("Reading clusters...")
    clusters = {}
    with clusters_loc.open() as f:
        for line in tqdm(f):
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
