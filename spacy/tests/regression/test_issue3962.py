# coding: utf8
from __future__ import unicode_literals

import pytest

from ..util import get_doc


@pytest.fixture
def doc(en_tokenizer):
    text = "He jests at scars, that never felt a wound."
    heads = [1, 6, -1, -1, 3, 2, 1, 0, 1, -2, -3]
    deps = ["nsubj", "ccomp", "prep", "pobj", "punct", "nsubj", "neg", "ROOT",
            "det", "dobj", "punct"]
    tokens = en_tokenizer(text)
    return get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)


def test_issue3962(doc):
    span = doc[0:3]
    doc2 = span.as_doc()
    assert doc2
    doc2_json = doc2.to_json()
    assert doc2_json