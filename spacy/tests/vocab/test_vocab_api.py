from __future__ import unicode_literals
import pytest
import io
import cloudpickle
import pickle

from spacy.attrs import LEMMA, ORTH, PROB, IS_ALPHA
from spacy.parts_of_speech import NOUN, VERB

from spacy.attrs import LEMMA, ORTH, PROB, IS_ALPHA
from spacy.parts_of_speech import NOUN, VERB


def test_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['bye'].orth != addr.orth


def test_eq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['Hello'].orth == addr.orth


def test_case_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['hello'].orth != addr.orth


def test_punct_neq(en_vocab):
    addr = en_vocab['Hello']
    assert en_vocab['Hello,'].orth != addr.orth


def test_shape_attr(en_vocab):
    example = en_vocab['example']
    assert example.orth != example.shape


def test_symbols(en_vocab):
    assert en_vocab.strings['IS_ALPHA'] == IS_ALPHA
    assert en_vocab.strings['NOUN'] == NOUN
    assert en_vocab.strings['VERB'] == VERB
    assert en_vocab.strings['LEMMA'] == LEMMA
    assert en_vocab.strings['ORTH'] == ORTH
    assert en_vocab.strings['PROB'] == PROB


def test_contains(en_vocab):
    assert 'Hello' in en_vocab
    assert 'LKsdjvlsakdvlaksdvlkasjdvljasdlkfvm' not in en_vocab
    

@pytest.mark.xfail
def test_pickle_vocab(en_vocab):
    file_ = io.BytesIO()
    cloudpickle.dump(en_vocab, file_)

    file_.seek(0)

    loaded = pickle.load(file_)


@pytest.mark.xfail
def test_pickle_vocab_vectors(en_vocab):
    vectors_length = en_vocab.vectors_length
    assert vectors_length != 0

    apples = en_vocab['apples']
    oranges = en_vocab['oranges']
    hippos = en_vocab['hippos']
    
    assert apples.similarity(oranges) > apples.similarity(hippos)

    apples.vector = hippos.vector

    assert apples.similarity(oranges) < apples.similarity(hippos)

    file_ = io.BytesIO()
    cloudpickle.dump(en_vocab, file_)

    file_.seek(0)

    loaded = pickle.load(file_)

    apples = loaded['apples']
    oranges = loaded['oranges']
    hippos = loaded['hippos']

    assert apples.similarity(oranges) < apples.similarity(hippos)
   
