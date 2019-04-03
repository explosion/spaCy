# coding: utf-8
from __future__ import unicode_literals

import pytest

@pytest.mark.parametrize('string,lemma', [('Litwo', 'litwa'),
                                          ('ojczyzno', 'ojczyzna'),
                                          ('moja', 'mój'),
                                          ('ty', 'ty'),
                                          ('jesteś', 'być'),
                                          ('cię', 'ty'),
                                          ('dowie', 'dowiedzieć'),
                                          ('straciła', 'stracić')])
def test_lemmatizer_lookup_assigns(tr_tokenizer, string, lemma):
    tokens = tr_tokenizer(string)
    assert tokens[0].lemma_ == lemma