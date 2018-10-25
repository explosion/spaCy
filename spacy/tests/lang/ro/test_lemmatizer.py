# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize('string,lemma', [('câini', 'câine'),
                                          ('expedițiilor', 'expediție'),
                                          ('pensete', 'pensetă'),
                                          ('erau', 'fi')])
def test_lemmatizer_lookup_assigns(ro_tokenizer, string, lemma):
    tokens = ro_tokenizer(string)
    assert tokens[0].lemma_ == lemma
