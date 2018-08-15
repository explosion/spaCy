# coding: utf-8
from __future__ import unicode_literals
from spacy.lang.en import English
from spacy.matcher import Matcher

def get_rule_id(nlp, matcher, doc):
    matches = matcher(doc)
    for match_id, start, end in matches:
        rule_id = nlp.vocab.strings[match_id]
        span = doc[start:end]
        return rule_id


def test_issue2671():
    nlp = English()
    matcher = Matcher(nlp.vocab)

    pattern = [{'LOWER': 'high'}, {'IS_PUNCT': True, 'OP': '?'}, {'LOWER': 'adrenaline'}]
    matcher.add("test_pattern", None, pattern)

    doc1 = nlp("This is a high-adrenaline situation.")
    doc2 = nlp("This is a high adrenaline situation.")
    # Works correctly
    assert get_rule_id(nlp, matcher, doc1) == 'test_pattern'
    assert get_rule_id(nlp, matcher, doc2) == 'test_pattern'
