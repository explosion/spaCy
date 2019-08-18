# coding: utf8
from __future__ import unicode_literals

from ..util import get_doc


def test_issue4104(en_vocab):
    """Test that English lookup lemmatization of spun & dry are correct
    expected mapping = {'dry': 'dry', 'spun': 'spin', 'spun-dry': 'spin-dry'}
    """
    text = "dry spun spun-dry"
    doc = get_doc(en_vocab, [t for t in text.split(" ")])
    # using a simple list to preserve order
    expected = ["dry", "spin", "spin-dry"]
    assert [token.lemma_ for token in doc] == expected
