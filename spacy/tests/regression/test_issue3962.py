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
    span2 = doc[1:5]  # "jests at scars ,"
    doc2 = span2.as_doc()
    doc2_json = doc2.to_json()
    assert doc2_json

    assert doc2[0].head.text == "jests"  # head set to itself, being the new artificial root
    assert doc2[0].dep_ == "dep"
    assert doc2[1].head.text == "jests"
    assert doc2[1].dep_ == "prep"
    assert doc2[2].head.text == "at"
    assert doc2[2].dep_ == "pobj"
    assert doc2[3].head.text == "jests"  # head set to the new artificial root
    assert doc2[3].dep_ == "dep"

    # We should still have 1 sentence
    assert len(list(doc2.sents)) == 1

    span3 = doc[6:9]  # "never felt a"
    doc3 = span3.as_doc()
    doc3_json = doc3.to_json()
    assert doc3_json

    assert doc3[0].head.text == "felt"
    assert doc3[0].dep_ == "neg"
    assert doc3[1].head.text == "felt"
    assert doc3[1].dep_ == "ROOT"
    assert doc3[2].head.text == "felt"  # head set to ancestor
    assert doc3[2].dep_ == "dep"

    # We should still have 1 sentence as "a" can be attached to "felt" instead of "wound"
    assert len(list(doc3.sents)) == 1


@pytest.fixture
def two_sent_doc(en_tokenizer):
    text = "He jests at scars. They never felt a wound."
    heads = [1, 0, -1, -1, -3, 2, 1, 0, 1, -2, -3]
    deps = [
        "nsubj",
        "ROOT",
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


def test_issue3962_long(two_sent_doc):
    """ Ensure that as_doc does not result in out-of-bound access of tokens.
    This is achieved by setting the head to itself if it would lie out of the span otherwise."""
    span2 = two_sent_doc[1:7]  # "jests at scars. They never"
    doc2 = span2.as_doc()
    doc2_json = doc2.to_json()
    assert doc2_json

    assert doc2[0].head.text == "jests"  # head set to itself, being the new artificial root (in sentence 1)
    assert doc2[0].dep_ == "ROOT"
    assert doc2[1].head.text == "jests"
    assert doc2[1].dep_ == "prep"
    assert doc2[2].head.text == "at"
    assert doc2[2].dep_ == "pobj"
    assert doc2[3].head.text == "jests"
    assert doc2[3].dep_ == "punct"
    assert doc2[4].head.text == "They"  # head set to itself, being the new artificial root (in sentence 2)
    assert doc2[4].dep_ == "dep"
    assert doc2[4].head.text == "They"  # head set to the new artificial head (in sentence 2)
    assert doc2[4].dep_ == "dep"

    # We should still have 2 sentences
    sents = list(doc2.sents)
    assert len(sents) == 2
    assert sents[0].text == "jests at scars ."
    assert sents[1].text == "They never"
