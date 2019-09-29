# coding: utf8
from __future__ import unicode_literals

from spacy.lang.el import Greek


def test_issue4272():
    """Test that lookup table can be accessed from Token.lemma if no POS tags
    are available."""
    nlp = Greek()
    doc = nlp("Χθες")
    assert doc[0].lemma_
