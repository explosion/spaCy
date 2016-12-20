from __future__ import unicode_literals
import spacy 
from spacy.attrs import ORTH


def merge_phrases(matcher, doc, i, matches):
    '''
    Merge a phrase. We have to be careful here because we'll change the token indices.
    To avoid problems, merge all the phrases once we're called on the last match.
    '''
    if i != len(matches)-1:
        return None
    # Get Span objects
    spans = [(ent_id, label, doc[start : end]) for ent_id, label, start, end in matches]
    for ent_id, label, span in spans:
        span.merge('NNP' if label else span.root.tag_, span.text, doc.vocab.strings[label])

def test_entity_ID_assignment():
    nlp = spacy.en.English()
    text = u"""The golf club is broken"""
    doc = nlp(text)

    golf_pattern =     [ 
            { ORTH: "golf"},
            { ORTH: "club"}
        ]

    matcher = spacy.matcher.Matcher(nlp.vocab)
    matcher.add_entity('Sport_Equipment', on_match = merge_phrases)
    matcher.add_pattern("Sport_Equipment", golf_pattern, label = 'Sport_Equipment')

    match = matcher(doc)
    entities = list(doc.ents)

    assert entities != [] #assertion 1
    assert entities[0].label != 0 #assertion 2
