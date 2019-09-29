# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.language import Language
from spacy.tokens import Span

from ..util import get_doc


@pytest.fixture
def doc(en_tokenizer):
    text = "I like New York in Autumn."
    heads = [1, 0, 1, -2, -3, -1, -5]
    tags = ["PRP", "IN", "NNP", "NNP", "IN", "NNP", "."]
    pos = ["PRON", "VERB", "PROPN", "PROPN", "ADP", "PROPN", "PUNCT"]
    deps = ["ROOT", "prep", "compound", "pobj", "prep", "pobj", "punct"]
    tokens = en_tokenizer(text)
    doc = get_doc(
        tokens.vocab,
        words=[t.text for t in tokens],
        heads=heads,
        tags=tags,
        pos=pos,
        deps=deps,
    )
    doc.ents = [Span(doc, 2, 4, doc.vocab.strings["GPE"])]
    doc.is_parsed = True
    doc.is_tagged = True
    return doc


def test_factories_merge_noun_chunks(doc):
    assert len(doc) == 7
    nlp = Language()
    merge_noun_chunks = nlp.create_pipe("merge_noun_chunks")
    merge_noun_chunks(doc)
    assert len(doc) == 6
    assert doc[2].text == "New York"


def test_factories_merge_ents(doc):
    assert len(doc) == 7
    assert len(list(doc.ents)) == 1
    nlp = Language()
    merge_entities = nlp.create_pipe("merge_entities")
    merge_entities(doc)
    assert len(doc) == 6
    assert len(list(doc.ents)) == 1
    assert doc[2].text == "New York"
