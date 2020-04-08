# coding: utf8
from __future__ import unicode_literals

import pytest

import spacy


@pytest.fixture
def nlp():
    return spacy.blank("en")


def test_issue4924(nlp):
    docs_golds = [("", {})]
    nlp.evaluate(docs_golds)
