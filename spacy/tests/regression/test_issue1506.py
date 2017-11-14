# coding: utf8
from __future__ import unicode_literals

import gc

from ...lang.en import English


def test_issue1506():
    nlp = English()

    def string_generator():
        for _ in range(10001):
            yield "It's sentence produced by that bug."

        yield "Oh snap."

        for _ in range(10001):
            yield "I erase lemmas."

        for _ in range(10001):
            yield "It's sentence produced by that bug."

        for _ in range(10001):
            yield "It's sentence produced by that bug."

    anchor = None
    remember = None
    for i, d in enumerate(nlp.pipe(string_generator())):
        if i == 9999:
            anchor = d
        elif 10001 == i:
            remember = d
        elif i == 10002:
            del anchor
            gc.collect()

        for t in d:
            str(t.lemma_)

    assert remember.text == 'Oh snap.'
