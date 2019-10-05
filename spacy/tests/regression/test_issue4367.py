# coding: utf8
from __future__ import unicode_literals

from spacy.tokens import DocBin


def test_issue4367():
    """Test that docbin init goes well"""
    doc_bin_1 = DocBin()
    doc_bin_2 = DocBin(attrs=["LEMMA"])
    doc_bin_3 = DocBin(attrs=["LEMMA", "ENT_IOB", "ENT_TYPE"])
