# coding: utf8
from __future__ import unicode_literals

import spacy


def test_issue3962():
    nlp = spacy.load('en_core_web_md')  # TODO: not supposed to have a model in a unit test here
    doc = nlp('He jests at scars, that never felt a wound.')

    span = doc[0:3]
    doc2 = span.as_doc()
    assert doc2
    doc2_json = doc2.to_json()
    assert doc2_json

    # TODO: remove
    for i, token in enumerate(doc):
        print(i, token.text, token.pos, token.pos_, token.dep, token.dep_, token.head)
    print()
    for i, token in enumerate(doc2):
        print(i, token.text, token.pos, token.pos_, token.dep, token.dep_, token.head)