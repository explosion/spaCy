# coding: utf-8
from __future__ import unicode_literals

from ...strings import StringStore

import pytest


@pytest.mark.parametrize('text1,text2,text3', [(b'Hello', b'goodbye', b'hello')])
def test_stringstore_save_bytes(stringstore, text1, text2, text3):
    i = stringstore[text1]
    assert i == 1
    assert stringstore[text1] == 1
    assert stringstore[text2] != i
    assert stringstore[text3] != i
    assert i == 1


@pytest.mark.parametrize('text1,text2,text3', [('Hello', 'goodbye', 'hello')])
def test_stringstore_save_unicode(stringstore, text1, text2, text3):
    i = stringstore[text1]
    assert i == 1
    assert stringstore[text1] == 1
    assert stringstore[text2] != i
    assert stringstore[text3] != i
    assert i == 1


@pytest.mark.parametrize('text', [b'A'])
def test_stringstore_retrieve_id(stringstore, text):
    i = stringstore[text]
    assert stringstore.size == 1
    assert stringstore[1] == text.decode('utf8')
    with pytest.raises(IndexError):
        stringstore[2]


@pytest.mark.parametrize('text1,text2', [(b'0123456789', b'A')])
def test_stringstore_med_string(stringstore, text1, text2):
    store = stringstore[text1]
    assert stringstore[store] == text1.decode('utf8')
    dummy = stringstore[text2]
    assert stringstore[text1] == store


def test_stringstore_long_string(stringstore):
    text = "INFORMATIVE](http://www.google.com/search?as_q=RedditMonkey&amp;hl=en&amp;num=50&amp;btnG=Google+Search&amp;as_epq=&amp;as_oq=&amp;as_eq=&amp;lr=&amp;as_ft=i&amp;as_filetype=&amp;as_qdr=all&amp;as_nlo=&amp;as_nhi=&amp;as_occt=any&amp;as_dt=i&amp;as_sitesearch=&amp;as_rights=&amp;safe=off"
    store = stringstore[text]
    assert stringstore[store] == text


@pytest.mark.parametrize('factor', [254, 255, 256])
def test_stringstore_multiply(stringstore, factor):
    text = 'a' * factor
    store = stringstore[text]
    assert stringstore[store] == text


def test_stringstore_massive_strings(stringstore):
    text = 'a' * 511
    store = stringstore[text]
    assert stringstore[store] == text
    text2 = 'z' * 512
    store = stringstore[text2]
    assert stringstore[store] == text2
    text3 = '1' * 513
    store = stringstore[text3]
    assert stringstore[store] == text3


@pytest.mark.parametrize('text', ["qqqqq"])
def test_stringstore_dump_load(stringstore, text_file, text):
    store = stringstore[text]
    stringstore.dump(text_file)
    text_file.seek(0)
    new_stringstore = StringStore()
    new_stringstore.load(text_file)
    assert new_stringstore[store] == text
