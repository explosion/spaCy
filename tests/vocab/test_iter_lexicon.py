import pytest


def test_range_iter(en_vocab):
    for i in range(len(en_vocab)):
        lex = en_vocab[i]


def test_iter(en_vocab):
    i = 0
    for lex in en_vocab:
        i += 1
