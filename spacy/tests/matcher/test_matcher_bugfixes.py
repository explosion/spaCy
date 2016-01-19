import pytest
import numpy

from spacy.matcher import Matcher
from spacy.attrs import ORTH, LOWER, ENT_IOB, ENT_TYPE
from spacy.symbols import DATE


def test_overlap_issue118(EN):
    '''Test a bug that arose from having overlapping matches'''
    doc = EN.tokenizer(u'how many points did lebron james score against the boston celtics last night')
    ORG = doc.vocab.strings['ORG']
    matcher = Matcher(EN.vocab,
        {'BostonCeltics':
            ('ORG', {},
                [
                    [{LOWER: 'celtics'}],
                    [{LOWER: 'boston'}, {LOWER: 'celtics'}],
                ]
            )
        }
    )
    
    assert len(list(doc.ents)) == 0
    matches = matcher(doc)
    assert matches == [(ORG, 9, 11), (ORG, 10, 11)]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


def test_overlap_reorder(EN):
    '''Test order dependence'''
    doc = EN.tokenizer(u'how many points did lebron james score against the boston celtics last night')
    ORG = doc.vocab.strings['ORG']
    matcher = Matcher(EN.vocab,
        {'BostonCeltics':
            ('ORG', {},
                [
                    [{LOWER: 'boston'}, {LOWER: 'celtics'}],
                    [{LOWER: 'celtics'}],
                ]
            )
        }
    )
    
    assert len(list(doc.ents)) == 0
    matches = matcher(doc)
    assert matches == [(ORG, 9, 11), (ORG, 10, 11)]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


def test_overlap_prefix(EN):
    '''Test order dependence'''
    doc = EN.tokenizer(u'how many points did lebron james score against the boston celtics last night')
    ORG = doc.vocab.strings['ORG']
    matcher = Matcher(EN.vocab,
        {'BostonCeltics':
            ('ORG', {},
                [
                    [{LOWER: 'boston'}],
                    [{LOWER: 'boston'}, {LOWER: 'celtics'}],
                ]
            )
        }
    )
    
    assert len(list(doc.ents)) == 0
    matches = matcher(doc)
    assert matches == [(ORG, 9, 10), (ORG, 9, 11)]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


def test_overlap_prefix_reorder(EN):
    '''Test order dependence'''
    doc = EN.tokenizer(u'how many points did lebron james score against the boston celtics last night')
    ORG = doc.vocab.strings['ORG']
    matcher = Matcher(EN.vocab,
        {'BostonCeltics':
            ('ORG', {},
                [
                    [{LOWER: 'boston'}, {LOWER: 'celtics'}],
                    [{LOWER: 'boston'}],
                ]
            )
        }
    )
    
    assert len(list(doc.ents)) == 0
    matches = matcher(doc)
    assert matches == [(ORG, 9, 10), (ORG, 9, 11)]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


@pytest.mark.models
def test_ner_interaction(EN):
    EN.matcher.add('LAX_Airport', 'AIRPORT', {}, [[{ORTH: 'LAX'}]])
    EN.matcher.add('SFO_Airport', 'AIRPORT', {}, [[{ORTH: 'SFO'}]])
    doc = EN.tokenizer(u'get me a flight from SFO to LAX leaving 20 December and arriving on January 5th')
    EN.tagger(doc)
    EN.matcher(doc)
    EN.entity.add_label('AIRPORT')
    EN.entity(doc)

    ents = [(ent.label_, ent.text) for ent in doc.ents]
    assert ents[0] == ('AIRPORT', 'SFO')
    assert ents[1] == ('AIRPORT', 'LAX')
    assert ents[2] == ('DATE', '20 December')
    assert ents[3] == ('DATE', 'January 5th')
 
