"""Test that tokens are created correctly for whitespace."""


from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('text', ["hello possums"])
def test_tokenizer_splits_single_space(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize('text', ["hello  possums"])
def test_tokenizer_splits_double_space(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == " "


@pytest.mark.parametrize('text', ["hello\npossums"])
def test_tokenizer_splits_newline(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3
    assert tokens[1].text == "\n"


@pytest.mark.parametrize('text', ["hello \npossums"])
def test_tokenizer_splits_newline_space(en_tokenizer, text):
    tokens = en_tokenizer('hello \npossums')
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["hello  \npossums"])
def test_tokenizer_splits_newline_double_space(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


@pytest.mark.parametrize('text', ["hello \n possums"])
def test_tokenizer_splits_newline_space_wrap(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert len(tokens) == 3


def test_leading_space_offsets(en_tokenizer):
    '''Issue #351
    # this works

    text1 = u"This is a cat."
    a = english_spacy(text1)

    tok0 = list(a.sents)[0][0]
    print tok0, tok0.idx, text1[tok0.idx]

    tok1 = list(a.sents)[0][1]
    print tok1, tok1.idx, text1[tok1.idx]

    print "=="

    # this does not work

    text2 = u"   This is a cat."
    b = english_spacy(text2)

    tok0 = list(b.sents)[0][0]
print tok0, tok0.idx, text2[tok0.idx]

    tok1 = list(b.sents)[0][1]
    print tok1, tok1.idx, text2[tok1.idx]
    '''
    doc = en_tokenizer(u"   This is a cat.")
    assert doc[0].idx == 0
    assert len(doc[0]) == 3
    assert doc[1].idx == 3
