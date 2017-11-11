# coding: utf8
from __future__ import unicode_literals

import random
import string

import itertools
from compat import izip

from ...lang.en import English


def test_issue1506():
    nlp = English()

    def string_generator():
        for (_, t) in izip(range(10001), itertools.repeat("It's sentence produced by that bug.")):
            yield t

        for (_, t) in izip(range(10001), itertools.repeat("I erase lemmas.")):
            yield t

        for (_, t) in izip(range(10001), itertools.repeat("It's sentence produced by that bug.")):
            yield t

    for d in nlp.pipe(string_generator()):
        for t in d:
            str(t.lemma_)
