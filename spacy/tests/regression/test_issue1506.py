# coding: utf8
from __future__ import unicode_literals

from ...lang.en import English


def test_issue1506():
    nlp = English()

    def string_generator():
        for _ in range(10001):
            yield "It's sentence produced by that bug."

        for _ in range(10001):
            yield "I erase lemmas."

        for _ in range(10001):
            yield "It's sentence produced by that bug."

    for d in nlp.pipe(string_generator()):
        for t in d:
            str(t.lemma_)
