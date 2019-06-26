# coding: utf8
from __future__ import unicode_literals

from spacy.displacy import parse_deps
from spacy.tokens import Doc


def test_issue3882(en_vocab):
    """Test that displaCy doesn't serialize the doc.user_data when making a
    copy of the Doc.
    """
    doc = Doc(en_vocab, words=["Hello", "world"])
    doc.is_parsed = True
    doc.user_data["test"] = set()
    parse_deps(doc)
