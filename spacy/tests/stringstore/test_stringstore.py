# coding: utf-8
from __future__ import unicode_literals

from ...strings import StringStore

import pytest


@pytest.mark.parametrize('text1,text2,text3', [(b'Hello', b'goodbye', b'hello')])
def test_stringstore_save_bytes(stringstore, text1, text2, text3):
    key = stringstore.add(text1)
    assert stringstore[text1] == key
    assert stringstore[text2] != key
    assert stringstore[text3] != key


@pytest.mark.parametrize('text1,text2,text3', [('Hello', 'goodbye', 'hello')])
def test_stringstore_save_unicode(stringstore, text1, text2, text3):
    key = stringstore.add(text1)
    assert stringstore[text1] == key
    assert stringstore[text2] != key
    assert stringstore[text3] != key


@pytest.mark.parametrize('text', [b'A'])
def test_stringstore_retrieve_id(stringstore, text):
    key = stringstore.add(text)
    assert len(stringstore) == 1
    assert stringstore[key] == text.decode('utf8')
    with pytest.raises(KeyError):
        stringstore[2]


@pytest.mark.parametrize('text1,text2', [(b'0123456789', b'A')])
def test_stringstore_med_string(stringstore, text1, text2):
    store = stringstore.add(text1)
    assert stringstore[store] == text1.decode('utf8')
    dummy = stringstore.add(text2)
    assert stringstore[text1] == store


def test_stringstore_long_string(stringstore):
    text = "INFORMATIVE](http://www.google.com/search?as_q=RedditMonkey&amp;hl=en&amp;num=50&amp;btnG=Google+Search&amp;as_epq=&amp;as_oq=&amp;as_eq=&amp;lr=&amp;as_ft=i&amp;as_filetype=&amp;as_qdr=all&amp;as_nlo=&amp;as_nhi=&amp;as_occt=any&amp;as_dt=i&amp;as_sitesearch=&amp;as_rights=&amp;safe=off"
    store = stringstore.add(text)
    assert stringstore[store] == text


@pytest.mark.parametrize('factor', [254, 255, 256])
def test_stringstore_multiply(stringstore, factor):
    text = 'a' * factor
    store = stringstore.add(text)
    assert stringstore[store] == text


def test_stringstore_massive_strings(stringstore):
    text = 'a' * 511
    store = stringstore.add(text)
    assert stringstore[store] == text
    text2 = 'z' * 512
    store = stringstore.add(text2)
    assert stringstore[store] == text2
    text3 = '1' * 513
    store = stringstore.add(text3)
    assert stringstore[store] == text3


@pytest.mark.parametrize('text', ["qqqqq"])
def test_stringstore_to_bytes(stringstore, text):
    store = stringstore.add(text)
    serialized = stringstore.to_bytes()
    new_stringstore = StringStore().from_bytes(serialized)
    assert new_stringstore[store] == text
