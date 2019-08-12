# coding: utf8
from __future__ import unicode_literals

import pytest
from ..util import get_doc

@pytest.mark.parametrize('text', ['dry spun spun-dry'])

def test_issue4104(en_tokenizer, en_vocab, text):
    """Test that English lookup lemmatization of spun & dry are correct"""
    doc = get_doc(en_vocab, [t for t in text.split(" ")])
    expected = {'dry': 'dry', 'spun': 'spin', 'spun-dry': 'spin-dry'}
    assert [token.lemma_ for token in doc] == list(expected.values())
