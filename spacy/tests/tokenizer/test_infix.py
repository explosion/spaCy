from __future__ import unicode_literals

import pytest

def test_hyphen(en_tokenizer):
    tokens = en_tokenizer('best-known')
    assert len(tokens) == 3


def test_numeric_range(en_tokenizer):
    tokens = en_tokenizer('0.1-13.5')
    assert len(tokens) == 3

def test_period(en_tokenizer):
    tokens = en_tokenizer('best.Known')
    assert len(tokens) == 3
    tokens = en_tokenizer('zombo.com')
    assert len(tokens) == 1


def test_ellipsis(en_tokenizer):
    tokens = en_tokenizer('best...Known')
    assert len(tokens) == 3
    tokens = en_tokenizer('best...known')
    assert len(tokens) == 3

def test_big_ellipsis(en_tokenizer):
    '''Test regression identified in Issue #360'''
    tokens = en_tokenizer(u'$45...............Asking')
    assert len(tokens) > 2



def test_email(en_tokenizer):
    tokens = en_tokenizer('hello@example.com')
    assert len(tokens) == 1
    tokens = en_tokenizer('hi+there@gmail.it')
    assert len(tokens) == 1


def test_double_hyphen(en_tokenizer):
    tokens = en_tokenizer(u'No decent--let alone well-bred--people.')
    assert tokens[0].text == u'No'
    assert tokens[1].text == u'decent'
    assert tokens[2].text == u'--'
    assert tokens[3].text == u'let'
    assert tokens[4].text == u'alone'
    assert tokens[5].text == u'well'
    assert tokens[6].text == u'-'
    # TODO: This points to a deeper issue with the tokenizer: it doesn't re-enter
    # on infixes.
    assert tokens[7].text == u'bred'
    assert tokens[8].text == u'--'
    assert tokens[9].text == u'people'


def test_infix_comma(en_tokenizer):
    # Re issue #326
    tokens = en_tokenizer(u'Hello,world')
    assert tokens[0].text == u'Hello'
    assert tokens[1].text == u','
    assert tokens[2].text == u'world'
