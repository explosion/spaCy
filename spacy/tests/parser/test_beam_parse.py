# coding: utf8
from __future__ import unicode_literals

import pytest
from ...language import Language
from ...pipeline import DependencyParser


@pytest.mark.models('en')
def test_beam_parse_en(EN):
    doc = EN(u'Australia is a country', disable=['ner'])
    ents = EN.entity(doc, beam_width=2)
    print(ents)


def test_beam_parse():
    nlp = Language()
    nlp.add_pipe(DependencyParser(nlp.vocab), name='parser')
    nlp.parser.add_label('nsubj')
    nlp.begin_training()

    doc = nlp.make_doc(u'Australia is a country')
    nlp.parser(doc, beam_width=2)
