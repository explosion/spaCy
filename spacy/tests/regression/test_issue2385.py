# coding: utf-8
import pytest

from ...gold import iob_to_biluo


@pytest.mark.xfail
@pytest.mark.parametrize('tags', [('B-ORG', 'L-ORG'),
                                  ('B-PERSON', 'I-PERSON', 'L-PERSON'),
                                  ('U-BRAWLER', 'U-BRAWLER')])
def test_issue2385_biluo(tags):
    """already biluo format"""
    assert iob_to_biluo(tags) == list(tags)


@pytest.mark.xfail
@pytest.mark.parametrize('tags', [('B-BRAWLER', 'I-BRAWLER', 'I-BRAWLER')])
def test_issue2385_iob_bcharacter(tags):
    """fix bug in labels with a 'b' character"""
    assert iob_to_biluo(tags) == ['B-BRAWLER', 'I-BRAWLER', 'L-BRAWLER']


@pytest.mark.xfail
@pytest.mark.parametrize('tags', [('I-ORG', 'I-ORG', 'B-ORG')])
def test_issue2385_iob1(tags):
    """maintain support for iob1 format"""
    assert iob_to_biluo(tags) == ['B-ORG', 'L-ORG', 'U-ORG']


@pytest.mark.xfail
@pytest.mark.parametrize('tags', [('B-PERSON', 'I-PERSON', 'B-PERSON')])
def test_issue2385_iob2(tags):
    """maintain support for iob2 format"""
    assert iob_to_biluo(tags) == ['B-PERSON', 'L-PERSON', 'U-PERSON']
