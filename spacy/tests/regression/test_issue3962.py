# coding: utf8
from __future__ import unicode_literals

import pytest

from ..util import get_doc


@pytest.fixture
def doc(en_tokenizer):
    text = "He jests at scars, that never felt a wound."
    heads = [1, 6, -1, -1, 3, 2, 1, 0, 1, -2, -3]
    deps = [
        "nsubj",
        "ccomp",
        "prep",
        "pobj",
        "punct",
        "nsubj",
        "neg",
        "ROOT",
        "det",
        "dobj",
        "punct",
    ]
    tokens = en_tokenizer(text)
    return get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)


def test_issue3962(doc):
    """ Ensure that as_doc does not result in out-of-bound access of tokens.
    This is achieved by setting the head to itself if it would lie out of the span otherwise."""
    assert doc[0].head.text == "jests"
    assert doc[1].head.text == "felt"
    assert doc[2].head.text == "jests"
    assert doc[3].head.text == "at"
    assert doc[4].head.text == "felt"
    assert doc[5].head.text == "felt"
    assert doc[6].head.text == "felt"
    assert doc[7].head.text == "felt"
    assert doc[8].head.text == "wound"
    assert doc[9].head.text == "felt"
    assert doc[10].head.text == "felt"

    span2 = doc[1:5]
    doc2 = span2.as_doc()
    assert doc2
    doc2_json = doc2.to_json()
    assert doc2_json

    # Note: doc2 is now two sentences, because we can't recover from the lost ROOT "felt"

    assert doc2[0].head.text == "jests"  # head set back to itself
    assert doc2[0].dep_ == "dep"
    assert doc2[1].head.text == "jests"
    assert doc2[1].dep_ == "prep"
    assert doc2[2].head.text == "at"
    assert doc2[2].dep_ == "pobj"
    assert doc2[3].head.text == ","  # head set back to itself
    assert doc2[3].dep_ == "dep"

    span3 = doc[6:9]
    doc3 = span3.as_doc()
    assert doc3
    doc3_json = doc3.to_json()
    assert doc3_json
    print(doc3)

    assert doc3[0].head.text == "felt"
    assert doc3[0].dep_ == "neg"
    assert doc3[1].head.text == "felt"
    assert doc3[1].dep_ == "ROOT"
    assert doc3[2].head.text == "felt"  # head set to ancestor
    assert doc3[2].dep_ == "dep"

    # doc3 should still be one sentence as "a" can be attached to "felt" instead of "wound"
    assert len(list(doc3.sents)) == 1
