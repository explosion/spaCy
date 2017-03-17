# coding: utf-8
from __future__ import unicode_literals

from ...tokens.doc import Doc
from ...attrs import HEAD
from ..util import get_doc, apply_transition_sequence

import pytest


def test_parser_space_attachment(en_tokenizer):
    text = "This is a test.\nTo ensure  spaces are attached well."
    heads = [1, 0, 1, -2, -3, -1, 1, 4, -1, 2, 1, 0, -1, -2]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)

    for sent in doc.sents:
        if len(sent) == 1:
            assert not sent[-1].is_space


def test_parser_sentence_space(en_tokenizer):
    text = "I look forward to using Thingamajig.  I've been told it will make my life easier..."
    heads = [1, 0, -1, -2, -1, -1, -5, -1, 3, 2, 1, 0, 2, 1, -3, 1, 1, -3, -7]
    deps = ['nsubj', 'ROOT', 'advmod', 'prep', 'pcomp', 'dobj', 'punct', '',
            'nsubjpass', 'aux', 'auxpass', 'ROOT', 'nsubj', 'aux', 'ccomp',
            'poss', 'nsubj', 'ccomp', 'punct']
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads, deps=deps)
    assert len(list(doc.sents)) == 2


def test_parser_space_attachment_leading(en_tokenizer, en_parser):
    text = "\t \n This is a sentence ."
    heads = [1, 1, 0, 1, -2, -3]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, text.split(' '), heads=heads)
    assert doc[0].is_space
    assert doc[1].is_space
    assert doc[2].text == 'This'
    with en_parser.step_through(doc) as stepwise:
        pass
    assert doc[0].head.i == 2
    assert doc[1].head.i == 2
    assert stepwise.stack == set([2])


def test_parser_space_attachment_intermediate_trailing(en_tokenizer, en_parser):
    text = "This is \t a \t\n \n sentence . \n\n \n"
    heads = [1, 0, -1, 2, -1, -4, -5, -1]
    transition = ['L-nsubj', 'S', 'L-det', 'R-attr', 'D', 'R-punct']
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, text.split(' '), heads=heads)
    assert doc[2].is_space
    assert doc[4].is_space
    assert doc[5].is_space
    assert doc[8].is_space
    assert doc[9].is_space

    apply_transition_sequence(en_parser, doc, transition)
    for token in doc:
        assert token.dep != 0 or token.is_space
    assert [token.head.i for token in doc] == [1, 1, 1, 6, 3, 3, 1, 1, 7, 7]


@pytest.mark.parametrize('text,length', [(['\n'], 1),
                                         (['\n', '\t', '\n\n', '\t'], 4)])
def test_parser_space_attachment_space(en_tokenizer, en_parser, text, length):
    doc = Doc(en_parser.vocab, words=text)
    assert len(doc) == length
    with en_parser.step_through(doc) as _:
        pass
    assert doc[0].is_space
    for token in doc:
        assert token.head.i == length-1
