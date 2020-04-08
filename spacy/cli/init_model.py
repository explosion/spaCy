# coding: utf8
from __future__ import unicode_literals

import plac
import math
from tqdm import tqdm
import numpy
from ast import literal_eval
from pathlib import Path
from preshed.counter import PreshCounter
import tarfile
import gzip
import zipfile
import srsly
from wasabi import msg

from ..vectors import Vectors
from ..errors import Errors, Warnings, user_warning
from ..util import ensure_path, get_lang_class

try:
    import ftfy
except ImportError:
    ftfy = None


DEFAULT_OOV_PROB = -20


@plac.annotations(
    lang=("Model language", "positional", None, str),
    output_dir=("Model output directory", "positional", None, Path),
    freqs_loc=("Location of words frequencies file", "option", "f", Path),
    jsonl_loc=("Location of JSONL-formatted attributes file", "option", "j", Path),
    clusters_loc=("Optional location of brown clusters data", "option", "c", str),
    vectors_loc=("Optional vectors file in Word2Vec format", "option", "v", str),
    prune_vectors=("Optional number of vectors to prune to", "option", "V", int),
    vectors_name=(
        "Optional name for the word vectors, e.g. en_core_web_lg.vectors",
        "option",
        "vn",
        str,
    ),
    model_name=("Optional name for the model meta", "option", "mn", str),
)
def init_model(
    lang,
    output_dir,
    freqs_loc=None,
    clusters_loc=None,
    jsonl_loc=None,
    vectors_loc=None,
    prune_vectors=-1,
    vectors_name=None,
    model_name=None,
):
    """
    Create a new model from raw data, like word frequencies, Brown clusters
    and word vectors. If vectors are provided in Word2Vec format, they can
    be either a .txt or zipped as a .zip or .tar.gz.
    """
    if jsonl_loc is not None:
        if freqs_loc is not None or clusters_loc is not None:
            settings = ["-j"]
            if freqs_loc:
                settings.append("-f")
            if clusters_loc:
                settings.append("-c")
            msg.warn(
                "Incompatible arguments",
                "The -f and -c arguments are deprecated, and not compatible "
                "with the -j argument, which should specify the same "
                "information. Either merge the frequencies and clusters data "
                "into the JSONL-formatted file (recommended), or use only the "
                "-f and -c files, without the other lexical attributes.",
            )
        jsonl_loc = ensure_path(jsonl_loc)
        lex_attrs = srsly.read_jsonl(jsonl_loc)
    else:
        clusters_loc = ensure_path(clusters_loc)
        freqs_loc = ensure_path(freqs_loc)
        if freqs_loc is not None and not freqs_loc.exists():
            msg.fail("Can't find words frequencies file", freqs_loc, exits=1)
        lex_attrs = read_attrs_from_deprecated(freqs_loc, clusters_loc)

    with msg.loading("Creating model..."):
        nlp = create_model(lang, lex_attrs, name=model_name)
    msg.good("Successfully created model")
    if vectors_loc is not None:
        add_vectors(nlp, vectors_loc, prune_vectors, vectors_name)
    vec_added = len(nlp.vocab.vectors)
    lex_added = len(nlp.vocab)
    msg.good(
        "Sucessfully compiled vocab",
        "{} entries, {} vectors".format(lex_added, vec_added),
    )
    if not output_dir.exists():
        output_dir.mkdir()
    nlp.to_disk(output_dir)
    return nlp


def open_file(loc):
    """Handle .gz, .tar.gz or unzipped files"""
    loc = ensure_path(loc)
    if tarfile.is_tarfile(str(loc)):
        return tarfile.open(str(loc), "r:gz")
    elif loc.parts[-1].endswith("gz"):
        return (line.decode("utf8") for line in gzip.open(str(loc), "r"))
    elif loc.parts[-1].endswith("zip"):
        zip_file = zipfile.ZipFile(str(loc))
        names = zip_file.namelist()
        file_ = zip_file.open(names[0])
        return (line.decode("utf8") for line in file_)
    else:
        return loc.open("r", encoding="utf8")


def read_attrs_from_deprecated(freqs_loc, clusters_loc):
    if freqs_loc is not None:
        with msg.loading("Counting frequencies..."):
            probs, _ = read_freqs(freqs_loc)
        msg.good("Counted frequencies")
    else:
        probs, _ = ({}, DEFAULT_OOV_PROB)  # noqa: F841
    if clusters_loc:
        with msg.loading("Reading clusters..."):
            clusters = read_clusters(clusters_loc)
        msg.good("Read clusters")
    else:
        clusters = {}
    lex_attrs = []
    sorted_probs = sorted(probs.items(), key=lambda item: item[1], reverse=True)
    if len(sorted_probs):
        for i, (word, prob) in tqdm(enumerate(sorted_probs)):
            attrs = {"orth": word, "id": i, "prob": prob}
            # Decode as a little-endian string, so that we can do & 15 to get
            # the first 4 bits. See _parse_features.pyx
            if word in clusters:
                attrs["cluster"] = int(clusters[word][::-1], 2)
            else:
                attrs["cluster"] = 0
            lex_attrs.append(attrs)
    return lex_attrs


def create_model(lang, lex_attrs, name=None):
    lang_class = get_lang_class(lang)
    nlp = lang_class()
    for lexeme in nlp.vocab:
        lexeme.rank = 0
    lex_added = 0
    for attrs in lex_attrs:
        if "settings" in attrs:
            continue
        lexeme = nlp.vocab[attrs["orth"]]
        lexeme.set_attrs(**attrs)
        lexeme.is_oov = False
        lex_added += 1
        lex_added += 1
    if len(nlp.vocab):
        oov_prob = min(lex.prob for lex in nlp.vocab) - 1
    else:
        oov_prob = DEFAULT_OOV_PROB
    nlp.vocab.cfg.update({"oov_prob": oov_prob})
    if name:
        nlp.meta["name"] = name
    return nlp


def add_vectors(nlp, vectors_loc, prune_vectors, name=None):
    vectors_loc = ensure_path(vectors_loc)
    if vectors_loc and vectors_loc.parts[-1].endswith(".npz"):
        nlp.vocab.vectors = Vectors(data=numpy.load(vectors_loc.open("rb")))
        for lex in nlp.vocab:
            if lex.rank:
                nlp.vocab.vectors.add(lex.orth, row=lex.rank)
    else:
        if vectors_loc:
            with msg.loading("Reading vectors from {}".format(vectors_loc)):
                vectors_data, vector_keys = read_vectors(vectors_loc)
            msg.good("Loaded vectors from {}".format(vectors_loc))
        else:
            vectors_data, vector_keys = (None, None)
        if vector_keys is not None:
            for word in vector_keys:
                if word not in nlp.vocab:
                    lexeme = nlp.vocab[word]
                    lexeme.is_oov = False
        if vectors_data is not None:
            nlp.vocab.vectors = Vectors(data=vectors_data, keys=vector_keys)
    if name is None:
        nlp.vocab.vectors.name = "%s_model.vectors" % nlp.meta["lang"]
    else:
        nlp.vocab.vectors.name = name
    nlp.meta["vectors"]["name"] = nlp.vocab.vectors.name
    if prune_vectors >= 1:
        nlp.vocab.prune_vectors(prune_vectors)


def read_vectors(vectors_loc):
    f = open_file(vectors_loc)
    shape = tuple(int(size) for size in next(f).split())
    vectors_data = numpy.zeros(shape=shape, dtype="f")
    vectors_keys = []
    for i, line in enumerate(tqdm(f)):
        line = line.rstrip()
        pieces = line.rsplit(" ", vectors_data.shape[1])
        word = pieces.pop(0)
        if len(pieces) != vectors_data.shape[1]:
            msg.fail(Errors.E094.format(line_num=i, loc=vectors_loc), exits=1)
        vectors_data[i] = numpy.asarray(pieces, dtype="f")
        vectors_keys.append(word)
    return vectors_data, vectors_keys


def read_freqs(freqs_loc, max_length=100, min_doc_freq=5, min_freq=50):
    counts = PreshCounter()
    total = 0
    with freqs_loc.open() as f:
        for i, line in enumerate(f):
            freq, doc_freq, key = line.rstrip().split("\t", 2)
            freq = int(freq)
            counts.inc(i + 1, freq)
            total += freq
    counts.smooth()
    log_total = math.log(total)
    probs = {}
    with freqs_loc.open() as f:
        for line in tqdm(f):
            freq, doc_freq, key = line.rstrip().split("\t", 2)
            doc_freq = int(doc_freq)
            freq = int(freq)
            if doc_freq >= min_doc_freq and freq >= min_freq and len(key) < max_length:
                try:
                    word = literal_eval(key)
                except SyntaxError:
                    # Take odd strings literally.
                    word = literal_eval("'%s'" % key)
                smooth_count = counts.smoother(int(freq))
                probs[word] = math.log(smooth_count) - log_total
    oov_prob = math.log(counts.smoother(0)) - log_total
    return probs, oov_prob


def read_clusters(clusters_loc):
    clusters = {}
    if ftfy is None:
        user_warning(Warnings.W004)
    with clusters_loc.open() as f:
        for line in tqdm(f):
            try:
                cluster, word, freq = line.split()
                if ftfy is not None:
                    word = ftfy.fix_text(word)
            except ValueError:
                continue
            # If the clusterer has only seen the word a few times, its
            # cluster is unreliable.
            if int(freq) >= 3:
                clusters[word] = cluster
            else:
                clusters[word] = "0"
    # Expand clusters with re-casing
    for word, cluster in list(clusters.items()):
        if word.lower() not in clusters:
            clusters[word.lower()] = cluster
        if word.title() not in clusters:
            clusters[word.title()] = cluster
        if word.upper() not in clusters:
            clusters[word.upper()] = cluster
    return clusters
