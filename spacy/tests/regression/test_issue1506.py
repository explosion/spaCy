# coding: utf8
from __future__ import unicode_literals

import gc

from ...lang.en import English


def test_issue1506():
    nlp = English()

    def string_generator():
        for _ in range(10001):
            yield u"It's sentence produced by that bug."

        for _ in range(10001):
            yield u"I erase some hbdsaj lemmas."

        for _ in range(10001):
            yield u"I erase lemmas."

        for _ in range(10001):
            yield u"It's sentence produced by that bug."

        for _ in range(10001):
            yield u"It's sentence produced by that bug."

    for i, d in enumerate(nlp.pipe(string_generator())):
        # We should run cleanup more than one time to actually cleanup data.
        # In first run — clean up only mark strings as «not hitted».
        if i == 10000 or i == 20000 or i == 30000:
            gc.collect()

        for t in d:
            str(t.lemma_)
