from __future__ import unicode_literals
from spacy.en import English
from spacy.attrs import IS_ALPHA, IS_ASCII, IS_DIGIT, IS_LOWER, IS_PUNCT
from spacy.attrs import IS_SPACE, IS_TITLE, IS_UPPER, LIKE_URL, LIKE_NUM
from spacy.attrs import IS_STOP

import pytest
import numpy


@pytest.mark.models
def test_strings(EN):
    tokens = EN(u'Give it back! He pleaded.')
    token = tokens[0]
    assert token.orth_ == 'Give'
    assert token.text == 'Give'
    assert token.text_with_ws == 'Give '
    assert token.lower_ == 'give'
    assert token.shape_ == 'Xxxx'
    assert token.prefix_ == 'G'
    assert token.suffix_ == 'ive'
    assert token.lemma_ == 'give'
    assert token.pos_ == 'VERB'
    assert token.tag_ == 'VB'
    assert token.dep_ == 'ROOT'


def test_flags(EN):
    tokens = EN(u'Give it back! He pleaded.')
    token = tokens[0]
 
    assert token.check_flag(IS_ALPHA)
    assert not token.check_flag(IS_DIGIT)
    # TODO: Test more of these, esp. if a bug is found


def test_single_token_string(EN):
    tokens = EN(u'foobar')
    assert tokens[0].text == 'foobar'


def test_str_builtin(EN):
    tokens = EN('one two')
    assert str(tokens[0]) == u'one'
    assert str(tokens[1]) == u'two'


@pytest.mark.models
def test_is_properties(EN):
    Hi, comma, my, email, is_, addr = EN(u'Hi, my email is test@me.com')
    assert Hi.is_title
    assert Hi.is_alpha
    assert not Hi.is_digit
    assert comma.is_punct
    assert email.is_ascii
    assert not email.like_url
    assert is_.is_lower
    assert addr.like_email
    assert addr.is_oov
    assert not Hi.is_oov

@pytest.mark.models
def test_vectors(EN):
    apples, oranges, oov = EN(u'apples oranges ldskbjlsdkbflzdfbl')
    assert apples.has_vector
    assert oranges.has_vector
    assert not oov.has_vector
    assert apples.similarity(oranges) > apples.similarity(oov)
    assert apples.similarity(oranges) == oranges.similarity(apples)
    assert sum(apples.vector) != sum(oranges.vector)
    assert numpy.isclose(
                apples.vector_norm,
                numpy.sqrt(numpy.dot(apples.vector, apples.vector)))
    
@pytest.mark.models
def test_ancestors(EN):
    # the structure of this sentence depends on the English annotation scheme
    tokens = EN(u'Yesterday I saw a dog that barked loudly.')
    ancestors = [ t.orth_ for t in tokens[6].ancestors ]
    assert ancestors == ['dog','saw']
    ancestors = [ t.orth_ for t in tokens[1].ancestors ]
    assert ancestors == ['saw']
    ancestors = [ t.orth_ for t in tokens[2].ancestors ]
    assert ancestors == []

    assert tokens[2].is_ancestor_of(tokens[7])
    assert not tokens[6].is_ancestor_of(tokens[2])


@pytest.mark.models
def test_head_setter(EN):
    # the structure of this sentence depends on the English annotation scheme
    yesterday, i, saw, a, dog, that, barked, loudly, dot = EN(u'Yesterday I saw a dog that barked loudly.')
    assert barked.n_lefts == 1
    assert barked.n_rights == 1
    assert barked.left_edge == that
    assert barked.right_edge == loudly

    assert dog.n_lefts == 1
    assert dog.n_rights == 1
    assert dog.left_edge == a
    assert dog.right_edge == loudly
    
    assert a.n_lefts == 0
    assert a.n_rights == 0
    assert a.left_edge == a
    assert a.right_edge == a

    assert saw.left_edge == yesterday
    assert saw.right_edge == dot

    barked.head = a

    assert barked.n_lefts == 1
    assert barked.n_rights == 1
    assert barked.left_edge == that
    assert barked.right_edge == loudly

    assert a.n_lefts == 0
    assert a.n_rights == 1
    assert a.left_edge == a
    assert a.right_edge == loudly

    assert dog.n_lefts == 1
    assert dog.n_rights == 0
    assert dog.left_edge == a
    assert dog.right_edge == loudly

    assert saw.left_edge == yesterday
    assert saw.right_edge == dot

    yesterday.head = that

    assert that.left_edge == yesterday
    assert barked.left_edge == yesterday
    assert a.left_edge == yesterday
    assert dog.left_edge == yesterday
    assert saw.left_edge == yesterday
