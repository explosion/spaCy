# coding: utf-8
from __future__ import unicode_literals

from ..util import get_doc

import pytest


@pytest.mark.models
def test_issue514(EN):
    """Test serializing after adding entity"""
    text = ["This", "is", "a", "sentence", "about", "pasta", "."]
    vocab = EN.entity.vocab
    doc = get_doc(vocab, text)
    EN.entity.add_label("Food")
    EN.entity(doc)
    label_id = vocab.strings[u'Food']
    doc.ents = [(label_id, 5,6)]
    assert [(ent.label_, ent.text) for ent in doc.ents] == [("Food", "pasta")]
    doc2 = get_doc(EN.entity.vocab).from_bytes(doc.to_bytes())
    assert [(ent.label_, ent.text) for ent in doc2.ents] == [("Food", "pasta")]
