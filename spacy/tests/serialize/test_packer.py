from __future__ import unicode_literals

import re

import pytest
import numpy

from spacy.language import Language
from spacy.en import English
from spacy.vocab import Vocab
from spacy.tokens.doc import Doc
from spacy.tokenizer import Tokenizer
from os import path
import os

from spacy import util
from spacy.attrs import ORTH, SPACY, TAG, DEP, HEAD
from spacy.serialize.packer import Packer

from spacy.serialize.bits import BitArray


@pytest.fixture
def vocab():
    path = os.environ.get('SPACY_DATA')
    if path is None:
        path = util.match_best_version('en', None, util.get_data_path())
    else:
        path = util.match_best_version('en', None, path)

    vocab = English.Defaults.create_vocab()
    lex = vocab['dog']
    assert vocab[vocab.strings['dog']].orth_ == 'dog'
    lex  = vocab['the']
    lex = vocab['quick']
    lex = vocab['jumped']
    return vocab


@pytest.fixture
def tokenizer(vocab):
    null_re = re.compile(r'!!!!!!!!!')
    tokenizer = Tokenizer(vocab, {}, null_re.search, null_re.search, null_re.finditer)
    return tokenizer


def test_char_packer(vocab):
    packer = Packer(vocab, [])
    bits = BitArray()
    bits.seek(0)

    byte_str = bytearray(b'the dog jumped')
    packer.char_codec.encode(byte_str, bits)
    bits.seek(0)
    result = [b''] * len(byte_str)
    packer.char_codec.decode(bits, result)
    assert bytearray(result) == byte_str


def test_packer_unannotated(tokenizer):
    packer = Packer(tokenizer.vocab, [])

    msg = tokenizer(u'the dog jumped')

    assert msg.string == 'the dog jumped'
    

    bits = packer.pack(msg)

    result = packer.unpack(bits)

    assert result.string == 'the dog jumped'


@pytest.mark.models
def test_packer_annotated(tokenizer):
    vocab = tokenizer.vocab
    nn = vocab.strings['NN']
    dt = vocab.strings['DT']
    vbd = vocab.strings['VBD']
    jj = vocab.strings['JJ']
    det = vocab.strings['det']
    nsubj = vocab.strings['nsubj']
    adj = vocab.strings['adj']
    root = vocab.strings['ROOT']

    attr_freqs = [
        (TAG, [(nn, 0.1), (dt, 0.2), (jj, 0.01), (vbd, 0.05)]),
        (DEP, {det: 0.2, nsubj: 0.1, adj: 0.05, root: 0.1}.items()),
        (HEAD, {0: 0.05, 1: 0.2, -1: 0.2, -2: 0.1, 2: 0.1}.items())
    ]

    packer = Packer(vocab, attr_freqs)

    msg = tokenizer(u'the dog jumped')

    msg.from_array(
        [TAG, DEP, HEAD],
        numpy.array([
            [dt, det, 1],
            [nn, nsubj, 1],
            [vbd, root, 0]
        ], dtype=numpy.int32))

    assert msg.string == 'the dog jumped'
    assert [t.tag_ for t in msg] == ['DT', 'NN', 'VBD']
    assert [t.dep_ for t in msg] == ['det', 'nsubj', 'ROOT']
    assert [(t.head.i - t.i) for t in msg] == [1, 1, 0]

    bits = packer.pack(msg)
    result = packer.unpack(bits)

    assert result.string == 'the dog jumped'
    assert [t.tag_ for t in result] == ['DT', 'NN', 'VBD']
    assert [t.dep_ for t in result] == ['det', 'nsubj', 'ROOT']
    assert [(t.head.i - t.i) for t in result] == [1, 1, 0]


def test_packer_bad_chars(tokenizer):
    string = u'naja gut, is eher bl\xf6d und nicht mit reddit.com/digg.com vergleichbar; vielleicht auf dem weg dahin'
    packer = Packer(tokenizer.vocab, [])

    doc = tokenizer(string)
    bits = packer.pack(doc)
    result = packer.unpack(bits)
    assert result.string == doc.string


@pytest.mark.models
def test_packer_bad_chars(EN):
    string = u'naja gut, is eher bl\xf6d und nicht mit reddit.com/digg.com vergleichbar; vielleicht auf dem weg dahin'
    doc = EN(string)
    byte_string = doc.to_bytes()
    result = Doc(EN.vocab).from_bytes(byte_string)
    assert [t.tag_ for t in result] == [t.tag_ for t in doc]
