# coding: utf8
from __future__ import unicode_literals, division, print_function

import plac
from pathlib import Path
import ujson
import cProfile
import pstats

import spacy
import sys
import tqdm
import cytoolz
import thinc.extra.datasets


def read_inputs(loc):
    if loc is None:
        file_ = sys.stdin
        file_ = (line.encode('utf8') for line in file_)
    else:
        file_ = Path(loc).open()
    for line in file_:
        data = ujson.loads(line)
        text = data['text']
        yield text


@plac.annotations(
    lang=("model/language", "positional", None, str),
    inputs=("Location of input file", "positional", None, read_inputs))
def profile(lang, inputs=None):
    """
    Profile a spaCy pipeline, to find out which functions take the most time.
    """
    if inputs is None:
        imdb_train, _ = thinc.extra.datasets.imdb()
        inputs, _ = zip(*imdb_train)
        inputs = inputs[:25000]
    nlp = spacy.load(lang)
    texts = list(cytoolz.take(10000, inputs))
    cProfile.runctx("parse_texts(nlp, texts)", globals(), locals(),
                    "Profile.prof")
    s = pstats.Stats("Profile.prof")
    s.strip_dirs().sort_stats("time").print_stats()


def parse_texts(nlp, texts):
    for doc in nlp.pipe(tqdm.tqdm(texts), batch_size=16):
        pass
