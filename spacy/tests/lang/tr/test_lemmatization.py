# coding: utf-8
from __future__ import unicode_literals

import pytest

@pytest.mark.parametrize('string,lemma', [('evlerimizdeki', 'ev'),
                                          ('işlerimizi', 'iş'),
                                          ('biran', 'biran'),
                                          ('bitirmeliyiz', 'bitir'),
                                          ('isteklerimizi', 'istek'),
                                          ('karşılaştırmamızın', 'karşılaştır'),
                                          ('çoğulculuktan', 'çoğulcu')])
def test_lemmatizer_lookup_assigns(tr_tokenizer, string, lemma):
    tokens = tr_tokenizer(string)
    assert tokens[0].lemma_ == lemma