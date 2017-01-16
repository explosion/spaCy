# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc

import pytest


def test_parser_noun_chunks_standard(en_tokenizer):
    text = "A base phrase should be recognized."
    heads = [2, 1, 3, 2, 1, 0, -1]
    tags = ['DT', 'JJ', 'NN', 'MD', 'VB', 'VBN', '.']
    deps = ['det', 'amod', 'nsubjpass', 'aux', 'auxpass', 'ROOT', 'punct']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], tags=tags, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "A base phrase "


def test_parser_noun_chunks_coordinated(en_tokenizer):
    text = "A base phrase and a good phrase are often the same."
    heads = [2, 1, 5, -1, 2, 1, -4, 0, -1, 1, -3, -4]
    tags = ['DT', 'NN', 'NN', 'CC', 'DT', 'JJ', 'NN', 'VBP', 'RB', 'DT', 'JJ', '.']
    deps = ['det', 'compound', 'nsubj', 'cc', 'det', 'amod', 'conj', 'ROOT', 'advmod', 'det', 'attr', 'punct']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], tags=tags, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "A base phrase "
    assert chunks[1].text_with_ws == "a good phrase "


def test_parser_noun_chunks_pp_chunks(en_tokenizer):
    text = "A phrase with another phrase occurs."
    heads = [1, 4, -1, 1, -2, 0, -1]
    tags = ['DT', 'NN', 'IN', 'DT', 'NN', 'VBZ', '.']
    deps = ['det', 'nsubj', 'prep', 'det', 'pobj', 'ROOT', 'punct']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], tags=tags, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "A phrase "
    assert chunks[1].text_with_ws == "another phrase "


def test_parser_noun_chunks_standard_de(de_tokenizer):
    text = "Eine Tasse steht auf dem Tisch."
    heads = [1, 1, 0, -1, 1, -2, -4]
    tags = ['ART', 'NN', 'VVFIN', 'APPR', 'ART', 'NN', '$.']
    deps = ['nk', 'sb', 'ROOT', 'mo', 'nk', 'nk', 'punct']

    tokens = de_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], tags=tags, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "Eine Tasse "
    assert chunks[1].text_with_ws == "dem Tisch "


def test_de_extended_chunk(de_tokenizer):
    text = "Die Sängerin singt mit einer Tasse Kaffee Arien."
    heads = [1, 1, 0, -1, 1, -2, -1, -5, -6]
    tags = ['ART', 'NN', 'VVFIN', 'APPR', 'ART', 'NN', 'NN', 'NN', '$.']
    deps = ['nk', 'sb', 'ROOT', 'mo', 'nk', 'nk', 'nk', 'oa', 'punct']

    tokens = de_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], tags=tags, deps=deps, heads=heads)
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 3
    assert chunks[0].text_with_ws == "Die Sängerin "
    assert chunks[1].text_with_ws == "einer Tasse Kaffee "
    assert chunks[2].text_with_ws == "Arien "
