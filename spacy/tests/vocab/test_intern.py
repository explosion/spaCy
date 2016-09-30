# -*- coding: utf8 -*-
from __future__ import unicode_literals
import pickle

from spacy.strings import StringStore
from cymem.cymem import Pool

import pytest
import tempfile

import io


@pytest.fixture
def sstore():
    return StringStore()


def test_save_bytes(sstore):
    Hello_i = sstore.intern(b'Hello')
    assert Hello_i == 1
    assert sstore.intern(b'Hello') == 1
    assert sstore[b'Hello'] == 1
    assert sstore.intern(b'goodbye') != Hello_i
    assert sstore.intern(b'hello') != Hello_i
    assert Hello_i == 1


def test_save_unicode(sstore):
    Hello_i = sstore.intern(u'Hello')
    assert Hello_i == 1
    assert sstore.intern(u'Hello') == 1
    assert sstore[u'Hello'] == 1
    assert sstore.intern(u'goodbye') != Hello_i
    assert sstore.intern(u'hello') != Hello_i
    assert Hello_i == 1


def test_retrieve_id(sstore):
    A_i = sstore.intern(b'A')
    assert sstore.size == 1
    assert sstore[1] == 'A'
    with pytest.raises(IndexError):
        sstore[2]


def test_med_string(sstore):
    nine_char_string = sstore.intern(b'0123456789')
    assert sstore[nine_char_string] == u'0123456789'
    dummy = sstore.intern(b'A')
    assert sstore[b'0123456789'] == nine_char_string


def test_long_string(sstore):
    url = u'INFORMATIVE](http://www.google.com/search?as_q=RedditMonkey&amp;hl=en&amp;num=50&amp;btnG=Google+Search&amp;as_epq=&amp;as_oq=&amp;as_eq=&amp;lr=&amp;as_ft=i&amp;as_filetype=&amp;as_qdr=all&amp;as_nlo=&amp;as_nhi=&amp;as_occt=any&amp;as_dt=i&amp;as_sitesearch=&amp;as_rights=&amp;safe=off'
    orth = sstore.intern(url)
    assert sstore[orth] == url


def test_254_string(sstore):
    s254 = 'a' * 254
    orth = sstore.intern(s254)
    assert sstore[orth] == s254

def test_255_string(sstore):
    s255 = 'b' * 255
    orth = sstore.intern(s255)
    assert sstore[orth] == s255

def test_256_string(sstore):
    s256 = 'c' * 256
    orth = sstore.intern(s256)
    assert sstore[orth] == s256


def test_massive_strings(sstore):
    s511 = 'd' * 511
    orth = sstore.intern(s511)
    assert sstore[orth] == s511
    s512 = 'e' * 512
    orth = sstore.intern(s512)
    assert sstore[orth] == s512
    s513 = '1' * 513
    orth = sstore.intern(s513)
    assert sstore[orth] == s513


def test_intern_oov(sstore):
    mem1 = Pool()
    mem2 = Pool()
    one = sstore.intern(u'Pool1', mem=mem1)
    two = sstore.intern(u'Pool2', mem=mem2)
    assert sstore.decode_int(one, mem=mem1) == 'Pool1'
    assert sstore.decode_int(two, mem=mem2) == 'Pool2'
    with pytest.raises(IndexError):
        sstore.decode_int(one, mem=mem2)
        sstore.decode_int(two, mem=mem1)
    sstore.remove_oov_map(mem1)
    with pytest.raises(IndexError):
        sstore.decode_int(one, mem=mem1)



def test_pickle_string_store(sstore):
    hello_id = sstore.intern(u'Hi')
    string_file = io.BytesIO()
    pickle.dump(sstore, string_file)

    string_file.seek(0)
    
    loaded = pickle.load(string_file)

    assert loaded[hello_id] == u'Hi'


def test_dump_load(sstore):
    id_ = sstore.intern(u'qqqqq')
    with tempfile.TemporaryFile('w+t') as file_: 
        sstore.dump(file_)
        file_.seek(0)
        new_store = StringStore()
        new_store.load(file_)
    assert new_store[id_] == u'qqqqq'
