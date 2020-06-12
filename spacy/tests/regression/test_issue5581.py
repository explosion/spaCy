# coding: utf-8
from __future__ import unicode_literals

import spacy
from ..util import make_tempdir


def test_issue5581():
    nlp = spacy.blank("fr")
    nlp.add_pipe(nlp.create_pipe("sentencizer"))
    nlp.add_pipe(nlp.create_pipe("tagger"))
    nlp.add_pipe(nlp.create_pipe("parser"))
    with make_tempdir() as d:
        nlp.to_disk(d)
