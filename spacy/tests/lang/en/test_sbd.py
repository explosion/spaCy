# coding: utf-8
from __future__ import unicode_literals

import pytest

from ...util import get_doc, apply_transition_sequence


@pytest.mark.parametrize("text", ["A test sentence"])
@pytest.mark.parametrize("punct", [".", "!", "?", ""])
def test_en_sbd_single_punct(en_tokenizer, text, punct):
    heads = [2, 1, 0, -1] if punct else [2, 1, 0]
    tokens = en_tokenizer(text + punct)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads)
    assert len(doc) == 4 if punct else 3
    assert len(list(doc.sents)) == 1
    assert sum(len(sent) for sent in doc.sents) == len(doc)


@pytest.mark.xfail
def test_en_sentence_breaks(en_tokenizer, en_parser):
    # fmt: off
    text = "This is a sentence . This is another one ."
    heads = [1, 0, 1, -2, -3, 1, 0, 1, -2, -3]
    deps = ["nsubj", "ROOT", "det", "attr", "punct", "nsubj", "ROOT", "det",
            "attr", "punct"]
    transition = ["L-nsubj", "S", "L-det", "R-attr", "D", "R-punct", "B-ROOT",
                  "L-nsubj", "S", "L-attr", "R-attr", "D", "R-punct"]
    # fmt: on
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, words=[t.text for t in tokens], heads=heads, deps=deps)
    apply_transition_sequence(en_parser, doc, transition)
    assert len(list(doc.sents)) == 2
    for token in doc:
        assert token.dep != 0 or token.is_space
    assert [token.head.i for token in doc] == [1, 1, 3, 1, 1, 6, 6, 8, 6, 6]
