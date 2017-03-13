# coding: utf8
from __future__ import unicode_literals

from ...tokens.doc import Doc
import pytest


@pytest.mark.xfail
@pytest.mark.models
@pytest.mark.parametrize('text', ["I cant do this."])
def test_issue636(EN, text):
    """Test that to_bytes and from_bytes don't change the token lemma."""
    doc1 = EN(text)
    doc2 = Doc(EN.vocab)
    doc2.from_bytes(doc1.to_bytes())
    assert [t.lemma_ for t in doc1] == [t.lemma_ for t in doc2]
