# coding: utf8
from __future__ import unicode_literals

from spacy.tokens import Doc
from spacy.vocab import Vocab


def test_issue3199():
    """Test that Span.noun_chunks works correctly if no noun chunks iterator
    is available. To make this test future-proof, we're constructing a Doc
    with a new Vocab here and setting is_parsed to make sure the noun chunks run.
    """
    doc = Doc(Vocab(), words=["This", "is", "a", "sentence"])
    doc.is_parsed = True
    assert list(doc[0:3].noun_chunks) == []
