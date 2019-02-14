# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.tokens import Doc
from spacy.compat import pickle


def test_issue2833(en_vocab):
    """Test that a custom error is raised if a token or span is pickled."""
    doc = Doc(en_vocab, words=["Hello", "world"])
    with pytest.raises(NotImplementedError):
        pickle.dumps(doc[0])
    with pytest.raises(NotImplementedError):
        pickle.dumps(doc[0:2])
