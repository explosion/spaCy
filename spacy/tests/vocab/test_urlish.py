from __future__ import unicode_literals

from spacy.orth import like_url


def test_basic_url():
    assert like_url('www.google.com')
    assert like_url('google.com')
    assert like_url('sydney.com')
    assert like_url('Sydney.edu')
    assert like_url('2girls1cup.org')


def test_close_enough():
    assert like_url('http://stupid')
    assert like_url('www.hi')


def test_non_match():
    assert not like_url('dog')
    assert not like_url('1.2')
    assert not like_url('1.a')
    assert not like_url('hello.There')
