# coding: utf8
from __future__ import unicode_literals

import pytest

from ...vocab import Vocab
from ...tokens import Doc, Span


@pytest.mark.xfail
def test_issue1547():
    """Test that entity labels still match after merging tokens."""
    words = ['\n', 'worda', '.', '\n', 'wordb', '-', 'Biosphere', '2', '-', ' \n']
    doc = Doc(Vocab(), words=words)
    doc.ents = [Span(doc, 6, 8, label=doc.vocab.strings['PRODUCT'])]
    doc[5:7].merge()
    assert [ent.text for ent in doc.ents]
