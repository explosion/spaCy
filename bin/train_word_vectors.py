#!/usr/bin/env python
from __future__ import print_function, unicode_literals, division

import logging
from pathlib import Path
from collections import defaultdict
from gensim.models import Word2Vec
import plac
import spacy

logger = logging.getLogger(__name__)


class Corpus(object):
    def __init__(self, directory, nlp):
        self.directory = directory
        self.nlp = nlp

    def __iter__(self):
        for text_loc in iter_dir(self.directory):
            with text_loc.open("r", encoding="utf-8") as file_:
                text = file_.read()

            # This is to keep the input to the blank model (which doesn't
            # sentencize) from being too long. It works particularly well with
            # the output of [WikiExtractor](https://github.com/attardi/wikiextractor)
            paragraphs = text.split('\n\n')
            for par in paragraphs:
                yield [word.orth_ for word in self.nlp(par)]


def iter_dir(loc):
    dir_path = Path(loc)
    for fn_path in dir_path.iterdir():
        if fn_path.is_dir():
            for sub_path in fn_path.iterdir():
                yield sub_path
        else:
            yield fn_path


@plac.annotations(
    lang=("ISO language code"),
    in_dir=("Location of input directory"),
    out_loc=("Location of output file"),
    n_workers=("Number of workers", "option", "n", int),
    size=("Dimension of the word vectors", "option", "d", int),
    window=("Context window size", "option", "w", int),
    min_count=("Min count", "option", "m", int),
    negative=("Number of negative samples", "option", "g", int),
    nr_iter=("Number of iterations", "option", "i", int),
)
def main(
    lang,
    in_dir,
    out_loc,
    negative=5,
    n_workers=4,
    window=5,
    size=128,
    min_count=10,
    nr_iter=5,
):
    logging.basicConfig(
        format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO
    )
    nlp = spacy.blank(lang)
    corpus = Corpus(in_dir, nlp)
    model = Word2Vec(
        sentences=corpus,
        size=size,
        window=window,
        min_count=min_count,
        workers=n_workers,
        sample=1e-5,
        negative=negative,
    )
    model.save(out_loc)

if __name__ == "__main__":
    plac.call(main)
