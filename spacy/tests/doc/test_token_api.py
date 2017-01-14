# coding: utf-8
from __future__ import unicode_literals

from ...attrs import IS_ALPHA, IS_DIGIT, IS_LOWER, IS_PUNCT, IS_TITLE, IS_STOP
from ..util import get_doc

import pytest
import numpy


def test_doc_token_api_strings(en_tokenizer):
    text = "Give it back! He pleaded."
    pos = ['VERB', 'PRON', 'PART', 'PUNCT', 'PRON', 'VERB', 'PUNCT']
    heads = [0, -1, -2, -3, 1, 0, -1]
    deps = ['ROOT', 'dobj', 'prt', 'punct', 'nsubj', 'ROOT', 'punct']

    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], pos=pos, heads=heads, deps=deps)
    assert doc[0].orth_ == 'Give'
    assert doc[0].text == 'Give'
    assert doc[0].text_with_ws == 'Give '
    assert doc[0].lower_ == 'give'
    assert doc[0].shape_ == 'Xxxx'
    assert doc[0].prefix_ == 'G'
    assert doc[0].suffix_ == 'ive'
    assert doc[0].pos_ == 'VERB'
    assert doc[0].dep_ == 'ROOT'


def test_doc_token_api_flags(en_tokenizer):
    text = "Give it back! He pleaded."
    tokens = en_tokenizer(text)
    assert tokens[0].check_flag(IS_ALPHA)
    assert not tokens[0].check_flag(IS_DIGIT)
    assert tokens[0].check_flag(IS_TITLE)
    assert tokens[1].check_flag(IS_LOWER)
    assert tokens[3].check_flag(IS_PUNCT)
    assert tokens[2].check_flag(IS_STOP)
    assert not tokens[5].check_flag(IS_STOP)
    # TODO: Test more of these, esp. if a bug is found


@pytest.mark.parametrize('text', ["Give it back! He pleaded."])
def test_doc_token_api_prob_inherited_from_vocab(en_tokenizer, text):
    word = text.split()[0]
    en_tokenizer.vocab[word].prob = -1
    tokens = en_tokenizer(text)
    assert tokens[0].prob != 0


@pytest.mark.parametrize('text', ["one two"])
def test_doc_token_api_str_builtin(en_tokenizer, text):
    tokens = en_tokenizer(text)
    assert str(tokens[0]) == text.split(' ')[0]
    assert str(tokens[1]) == text.split(' ')[1]


def test_doc_token_api_is_properties(en_vocab):
    text = ["Hi", ",", "my", "email", "is", "test@me.com"]
    doc = get_doc(en_vocab, text)
    assert doc[0].is_title
    assert doc[0].is_alpha
    assert not doc[0].is_digit
    assert doc[1].is_punct
    assert doc[3].is_ascii
    assert not doc[3].like_url
    assert doc[4].is_lower
    assert doc[5].like_email


@pytest.mark.parametrize('text,vectors', [
    ("apples oranges ldskbjls", ["apples -1 -1 -1", "oranges -1 -1 0"])
])
def test_doc_token_api_vectors(en_tokenizer, text_file, text, vectors):
    text_file.write('\n'.join(vectors))
    text_file.seek(0)
    vector_length = en_tokenizer.vocab.load_vectors(text_file)
    assert vector_length == 3

    tokens = en_tokenizer(text)
    assert tokens[0].has_vector
    assert tokens[1].has_vector
    assert not tokens[2].has_vector
    assert tokens[0].similarity(tokens[1]) > tokens[0].similarity(tokens[2])
    assert tokens[0].similarity(tokens[1]) == tokens[1].similarity(tokens[0])
    assert sum(tokens[0].vector) != sum(tokens[1].vector)
    assert numpy.isclose(
        tokens[0].vector_norm,
        numpy.sqrt(numpy.dot(tokens[0].vector, tokens[0].vector)))


def test_doc_token_api_ancestors(en_tokenizer):
    # the structure of this sentence depends on the English annotation scheme
    text = "Yesterday I saw a dog that barked loudly."
    heads = [2, 1, 0, 1, -2, 1, -2, -1, -6]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)
    assert [t.text for t in doc[6].ancestors] == ["dog", "saw"]
    assert [t.text for t in doc[1].ancestors] == ["saw"]
    assert [t.text for t in doc[2].ancestors] == []

    assert doc[2].is_ancestor_of(doc[7])
    assert not doc[6].is_ancestor_of(doc[2])


def test_doc_token_api_head_setter(en_tokenizer):
    # the structure of this sentence depends on the English annotation scheme
    text = "Yesterday I saw a dog that barked loudly."
    heads = [2, 1, 0, 1, -2, 1, -2, -1, -6]
    tokens = en_tokenizer(text)
    doc = get_doc(tokens.vocab, [t.text for t in tokens], heads=heads)

    assert doc[6].n_lefts == 1
    assert doc[6].n_rights == 1
    assert doc[6].left_edge.i == 5
    assert doc[6].right_edge.i == 7

    assert doc[4].n_lefts == 1
    assert doc[4].n_rights == 1
    assert doc[4].left_edge.i == 3
    assert doc[4].right_edge.i == 7

    assert doc[3].n_lefts == 0
    assert doc[3].n_rights == 0
    assert doc[3].left_edge.i == 3
    assert doc[3].right_edge.i == 3

    assert doc[2].left_edge.i == 0
    assert doc[2].right_edge.i == 8

    doc[6].head = doc[3]

    assert doc[6].n_lefts == 1
    assert doc[6].n_rights == 1
    assert doc[6].left_edge.i == 5
    assert doc[6].right_edge.i == 7

    assert doc[3].n_lefts == 0
    assert doc[3].n_rights == 1
    assert doc[3].left_edge.i == 3
    assert doc[3].right_edge.i == 7

    assert doc[4].n_lefts == 1
    assert doc[4].n_rights == 0
    assert doc[4].left_edge.i == 3
    assert doc[4].right_edge.i == 7

    assert doc[2].left_edge.i == 0
    assert doc[2].right_edge.i == 8

    doc[0].head = doc[5]

    assert doc[5].left_edge.i == 0
    assert doc[6].left_edge.i == 0
    assert doc[3].left_edge.i == 0
    assert doc[4].left_edge.i == 0
    assert doc[2].left_edge.i == 0
