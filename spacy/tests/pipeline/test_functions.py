# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.pipeline.functions import merge_subtokens
from ..util import get_doc


@pytest.fixture
def doc(en_tokenizer):
    # fmt: off
    text = "This is a sentence. This is another sentence. And a third."
    heads = [1, 0, 1, -2, -3, 1, 0, 1, -2, -3, 1, 1, 1, 0]
    deps = ["nsubj", "ROOT", "subtok", "attr", "punct", "nsubj", "ROOT",
            "subtok", "attr", "punct", "subtok", "subtok", "subtok", "ROOT"]
    # fmt: on
    tokens = en_tokenizer(text)
    return get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)


def test_merge_subtokens(doc):
    doc = merge_subtokens(doc)
    # get_doc() doesn't set spaces, so the result is "And a third ."
    assert [t.text for t in doc] == [
        "This",
        "is",
        "a sentence",
        ".",
        "This",
        "is",
        "another sentence",
        ".",
        "And a third .",
    ]
