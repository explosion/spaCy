# coding: utf8
from __future__ import unicode_literals

from spacy.tokens import DocBin


def test_issue4367():
    """Test that docbin init goes well"""
    DocBin()
    DocBin(attrs=["LEMMA"])
    DocBin(attrs=["LEMMA", "ENT_IOB", "ENT_TYPE"])
