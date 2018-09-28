# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lang.en import English
from spacy.matcher import Matcher


def test_issue2671():
    """Ensure the correct entity ID is returned for matches with quantifiers.
    See also #2675
    """
    def get_rule_id(nlp, matcher, doc):
        matches = matcher(doc)
        for match_id, start, end in matches:
            rule_id = nlp.vocab.strings[match_id]
            span = doc[start:end]
            return rule_id

    nlp = English()
    matcher = Matcher(nlp.vocab)
    pattern_id = 'test_pattern'
    pattern = [{'LOWER': 'high'},
               {'IS_PUNCT': True, 'OP': '?'},
               {'LOWER': 'adrenaline'}]
    matcher.add(pattern_id, None, pattern)
    doc1 = nlp("This is a high-adrenaline situation.")
    doc2 = nlp("This is a high adrenaline situation.")
    assert get_rule_id(nlp, matcher, doc1) == pattern_id
    assert get_rule_id(nlp, matcher, doc2) == pattern_id
