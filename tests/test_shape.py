from __future__ import unicode_literals

import pytest

from spacy.orth import word_shape as ws


def test_capitalized():
    assert ws('Nasa') == 'Xxxx'

def test_truncate():
    assert ws('capitalized') == 'xxx'

def test_digits():
    assert ws('999999999') == 'ddd'

def test_mix():
    assert ws('C3P0') == 'XdXd'

def test_punct():
    assert ws(',') == ','

def test_space():
    assert ws('\n') == '\n'

def test_punct_seq():
    assert ws('``,-') == '``,-'
