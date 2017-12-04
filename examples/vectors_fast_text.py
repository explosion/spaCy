#!/usr/bin/env python
# coding: utf8
"""Load vectors for a language trained using fastText
https://github.com/facebookresearch/fastText/blob/master/pretrained-vectors.md
Compatible with: spaCy v2.0.0+
"""
from __future__ import unicode_literals
import plac
import numpy

import spacy
from spacy.language import Language


@plac.annotations(
    vectors_loc=("Path to .vec file", "positional", None, str),
    lang=("Optional language ID. If not set, blank Language() will be used.",
          "positional", None, str))
def main(vectors_loc, lang=None):
    if lang is None:
        nlp = Language()
    else:
        # create empty language class – this is required if you're planning to
        # save the model to disk and load it back later (models always need a
        # "lang" setting). Use 'xx' for blank multi-language class.
        nlp = spacy.blank(lang)
    with open(vectors_loc, 'rb') as file_:
        header = file_.readline()
        nr_row, nr_dim = header.split()
        nlp.vocab.reset_vectors(width=int(nr_dim))
        for line in file_:
            line = line.rstrip().decode('utf8')
            pieces = line.rsplit(' ', int(nr_dim))
            word = pieces[0]
            vector = numpy.asarray([float(v) for v in pieces[1:]], dtype='f')
            nlp.vocab.set_vector(word, vector)  # add the vectors to the vocab
    # test the vectors and similarity
    text = 'class colspan'
    doc = nlp(text)
    print(text, doc[0].similarity(doc[1]))


if __name__ == '__main__':
    plac.call(main)
