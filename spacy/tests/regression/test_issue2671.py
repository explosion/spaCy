# coding: utf-8
from __future__ import unicode_literals

from spacy.lang.en import English
from spacy.matcher import Matcher


def test_issue2671():
    """Ensure the correct entity ID is returned for matches with quantifiers.
    See also #2675
    """
    nlp = English()
    matcher = Matcher(nlp.vocab)
    pattern_id = "test_pattern"
    pattern = [
        {"LOWER": "high"},
        {"IS_PUNCT": True, "OP": "?"},
        {"LOWER": "adrenaline"},
    ]
    matcher.add(pattern_id, None, pattern)
    doc1 = nlp("This is a high-adrenaline situation.")
    doc2 = nlp("This is a high adrenaline situation.")
    matches1 = matcher(doc1)
    for match_id, start, end in matches1:
        assert nlp.vocab.strings[match_id] == pattern_id
    matches2 = matcher(doc2)
    for match_id, start, end in matches2:
        assert nlp.vocab.strings[match_id] == pattern_id
