# coding: utf8
from __future__ import unicode_literals

import pytest

from ...pipeline import EntityRecognizer
from ...vocab import Vocab


@pytest.mark.parametrize('label', ['U-JOB-NAME'])
def test_issue1967(label):
    ner = EntityRecognizer(Vocab())
    entry = ([0], ['word'], ['tag'], [0], ['dep'], [label])
    gold_parses = [(None, [(entry, None)])]
    ner.moves.get_actions(gold_parses=gold_parses)
