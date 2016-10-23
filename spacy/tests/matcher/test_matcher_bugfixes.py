import pytest
import numpy
import os

import spacy
from spacy.matcher import Matcher
from spacy.attrs import ORTH, LOWER, ENT_IOB, ENT_TYPE
from spacy.attrs import ORTH, TAG, LOWER, IS_ALPHA, FLAG63
from spacy.symbols import DATE, LOC


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
    matches = [(ent_type, start, end) for ent_id, ent_type, start, end in matcher(doc)]
    assert matches == [(ORG, 9, 11), (ORG, 10, 11)]
    doc.ents = matches[:1]
    ents = list(doc.ents)
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


def test_overlap_issue242():
    '''Test overlapping multi-word phrases.'''

    patterns = [
        [{LOWER: 'food'}, {LOWER: 'safety'}],
        [{LOWER: 'safety'}, {LOWER: 'standards'}],
    ]

    if os.environ.get('SPACY_DATA'):
        data_dir = os.environ.get('SPACY_DATA')
    else:
        data_dir = None
 
    nlp = spacy.en.English(path=data_dir, tagger=False, parser=False, entity=False)
    nlp.matcher = Matcher(nlp.vocab)

    nlp.matcher.add('FOOD', 'FOOD', {}, patterns)

    doc = nlp.tokenizer(u'There are different food safety standards in different countries.')

    matches = [(ent_type, start, end) for ent_id, ent_type, start, end in nlp.matcher(doc)]
    doc.ents += tuple(matches)
    food_safety, safety_standards = matches
    assert food_safety[1] == 3
    assert food_safety[2] == 5
    assert safety_standards[1] == 4
    assert safety_standards[2] == 6


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
    matches = [(ent_type, start, end) for ent_id, ent_type, start, end in matcher(doc)]
    assert matches == [(ORG, 9, 11), (ORG, 10, 11)]
    doc.ents = matches[:1]
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
    matches = [(ent_type, start, end) for ent_id, ent_type, start, end in matcher(doc)]
    doc.ents = matches[1:]
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
    matches = [(ent_type, start, end) for ent_id, ent_type, start, end in matcher(doc)]
    doc.ents += tuple(matches)[1:]
    assert matches == [(ORG, 9, 10), (ORG, 9, 11)]
    ents = doc.ents
    assert len(ents) == 1
    assert ents[0].label == ORG
    assert ents[0].start == 9
    assert ents[0].end == 11


# @pytest.mark.models
# def test_ner_interaction(EN):
#     EN.matcher.add('LAX_Airport', 'AIRPORT', {}, [[{ORTH: 'LAX'}]])
#     EN.matcher.add('SFO_Airport', 'AIRPORT', {}, [[{ORTH: 'SFO'}]])
#     doc = EN(u'get me a flight from SFO to LAX leaving 20 December and arriving on January 5th')

#     ents = [(ent.label_, ent.text) for ent in doc.ents]
#     assert ents[0] == ('AIRPORT', 'SFO')
#     assert ents[1] == ('AIRPORT', 'LAX')
#     assert ents[2] == ('DATE', '20 December')
#     assert ents[3] == ('DATE', 'January 5th')
 

# @pytest.mark.models
# def test_ner_interaction(EN):
#     # ensure that matcher doesn't overwrite annotations set by the NER model
#     doc = EN.tokenizer.tokens_from_list(u'get me a flight from SFO to LAX leaving 20 December and arriving on January 5th'.split(' '))
#     EN.tagger(doc)

#     columns = [ENT_IOB, ENT_TYPE]
#     values = numpy.ndarray(shape=(len(doc),len(columns)), dtype='int32')
#     # IOB values are 0=missing, 1=I, 2=O, 3=B 
#     iobs = [2,2,2,2,2,3,2,3,2,3,1,2,2,2,3,1]
#     types = [0,0,0,0,0,LOC,0,LOC,0,DATE,DATE,0,0,0,DATE,DATE]
#     values[:] = zip(iobs,types)
#     doc.from_array(columns,values)

#     assert doc[5].ent_type_ == 'LOC'
#     assert doc[7].ent_type_ == 'LOC'
#     assert doc[9].ent_type_ == 'DATE'
#     assert doc[10].ent_type_ == 'DATE'
#     assert doc[14].ent_type_ == 'DATE'
#     assert doc[15].ent_type_ == 'DATE'

#     EN.matcher.add('LAX_Airport', 'AIRPORT', {}, [[{ORTH: 'LAX'}]])
#     EN.matcher.add('SFO_Airport', 'AIRPORT', {}, [[{ORTH: 'SFO'}]])
#     EN.matcher(doc)

#     assert doc[5].ent_type_ != 'AIRPORT'
#     assert doc[7].ent_type_ != 'AIRPORT'
#     assert doc[5].ent_type_ == 'LOC'
#     assert doc[7].ent_type_ == 'LOC'
#     assert doc[9].ent_type_ == 'DATE'
#     assert doc[10].ent_type_ == 'DATE'
#     assert doc[14].ent_type_ == 'DATE'
#     assert doc[15].ent_type_ == 'DATE'










