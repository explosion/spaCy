# coding: utf-8
from __future__ import unicode_literals

from spacy.gold import GoldParse
from spacy.scorer import Scorer
from ..util import get_doc

test_samples = [
    [
        "100 - 200",
        {
            "entities": [
                [0, 3, "CARDINAL"],
                [6, 9, "CARDINAL"]
            ]
        }
    ]
]

def test_issue3625(en_vocab):
    scorer = Scorer()
    for input_, annot in test_samples:
        doc = get_doc(en_vocab, words = input_.split(' '), ents = [[0,1,'CARDINAL'], [2,3,'CARDINAL']]);    
        gold = GoldParse(doc, entities = annot['entities'])
        scorer.score(doc, gold)
    results = scorer.scores

    # Expects total accuracy and accuracy for each each entity to be 100%
    assert results['ents_p'] == 100
    assert results['ents_f'] == 100
    assert results['ents_r'] == 100
    assert results['ents_per_type']['CARDINAL']['p'] == 100
    assert results['ents_per_type']['CARDINAL']['f'] == 100
    assert results['ents_per_type']['CARDINAL']['r'] == 100
