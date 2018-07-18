# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.gold import iob_to_biluo


def test_issue2385():
    # fix bug in labels with a 'b' character
    tags1 = ('B-BRAWLER', 'I-BRAWLER', 'I-BRAWLER')
    assert iob_to_biluo(tags1) == ['B-BRAWLER', 'I-BRAWLER', 'L-BRAWLER']
    # maintain support for iob1 format
    tags2 = ('I-ORG', 'I-ORG', 'B-ORG')
    assert iob_to_biluo(tags2) == ['B-ORG', 'L-ORG', 'U-ORG']
    # maintain support for iob2 format
    tags3 = ('B-PERSON', 'I-PERSON', 'B-PERSON')
    assert iob_to_biluo(tags3) ==['B-PERSON', 'L-PERSON', 'U-PERSON']


@pytest.mark.parametrize('tags', [
    ('B-ORG', 'L-ORG'), ('B-PERSON', 'I-PERSON', 'L-PERSON'), ('U-BRAWLER', 'U-BRAWLER')])
def test_issue2385_biluo(tags):
    assert iob_to_biluo(tags) == list(tags)
