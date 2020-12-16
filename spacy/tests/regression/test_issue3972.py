# coding: utf8
from __future__ import unicode_literals

from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc


def test_issue3972(en_vocab):
    """Test that the PhraseMatcher returns duplicates for duplicate match IDs.
    """
    matcher = PhraseMatcher(en_vocab)
    matcher.add("A", [Doc(en_vocab, words=["New", "York"])])
    matcher.add("B", [Doc(en_vocab, words=["New", "York"])])
    doc = Doc(en_vocab, words=["I", "live", "in", "New", "York"])
    matches = matcher(doc)

    assert len(matches) == 2

    # We should have a match for each of the two rules
    found_ids = [en_vocab.strings[ent_id] for (ent_id, _, _) in matches]
    assert "A" in found_ids
    assert "B" in found_ids
