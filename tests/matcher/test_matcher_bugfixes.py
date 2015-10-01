import pytest


from spacy.matcher import Matcher

def test_overlap_issue118(EN):
    '''Test a bug that arose from having overlapping matches'''
    doc = EN.tokenizer(u'how many points did lebron james score against the boston celtics last night')
    ORG = doc.vocab.strings['ORG']
    matcher = Matcher(EN.vocab, {'BostonCeltics': ('ORG', {}, [[{'lower': 'boston'}, {'lower': 'celtics'}], [{'lower': 'celtics'}]])})
    
    matches = matcher(doc)
    assert matches == [(ORG, 9, 11)]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11

