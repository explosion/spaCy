# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English
from spacy.tokens import Doc


def test_issue3468():
    """Test that sentence boundaries are set correctly so Doc.is_sentenced can
    be restored after serialization."""
    nlp = English()
    nlp.add_pipe(nlp.create_pipe("sentencizer"))
    doc = nlp("Hello world")
    assert doc[0].is_sent_start
    assert doc.is_sentenced
    assert len(list(doc.sents)) == 1
    doc_bytes = doc.to_bytes()
    new_doc = Doc(nlp.vocab).from_bytes(doc_bytes)
    assert new_doc[0].is_sent_start
    assert new_doc.is_sentenced
    assert len(list(new_doc.sents)) == 1
