from spacy.en import English

import pytest

NLP = English()


def test_root():
    tokens = NLP(u"i don't have other assistance")
    for t in tokens:
        assert t.dep != 0, t.orth_
