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
    """ Ensure that as_doc does not result in out-of-bound access of tokens.
    This is achieved by setting the head to itself it it would lie out of the span otherwise."""
    assert doc[1].dep_ == "ccomp"
    assert doc[1].head.text == "felt"
    assert doc[2].dep_ == "prep"
    assert doc[2].head.text == "jests"
    assert doc[3].dep_ == "pobj"
    assert doc[3].head.text == "at"
    assert doc[4].dep_ == "punct"
    assert doc[4].head.text == "felt"
    span = doc[1:5]
    doc2 = span.as_doc()
    assert doc2
    doc2_json = doc2.to_json()
    assert doc2_json
    assert doc2[0].dep_ == "ccomp"
    assert doc2[0].head.text == "jests"  # head set back to itself
    assert doc2[1].dep_ == "prep"
    assert doc2[1].head.text == "jests"
    assert doc2[2].dep_ == "pobj"
    assert doc2[2].head.text == "at"
    assert doc2[3].dep_ == "punct"
    assert doc2[3].head.text == ","      # head set back to itself