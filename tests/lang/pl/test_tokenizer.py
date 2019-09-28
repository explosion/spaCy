# coding: utf8
from __future__ import unicode_literals

import pytest

DOT_TESTS = [
    ("tel.", ["tel."]),
    ("np.", ["np."]),
    ("godz. 21:37", ["godz.", "21:37"]),
    ("inż.", ["inż."]),
    ("gosp.-polit.", ["gosp.-polit."]),
    ("ppoż", ["ppoż"]),
    ("płn", ["płn"]),
    ("ul.", ["ul."]),
    ("jw.", ["jw."]),
    ("itd.", ["itd."]),
    ("cdn.", ["cdn."]),
    ("itp.", ["itp."]),
    ("10,- zł", ["10,-", "zł"]),
    ("0 zł 99 gr", ["0", "zł", "99", "gr"]),
    ("0,99 rub.", ["0,99", "rub."]),
    ("dol.", ["dol."]),
    ("1000 m n.p.m.", ["1000", "m", "n.p.m."]),
    ("m.in.", ["m.in."]),
    ("p.n.e.", ["p.n.e."]),
    ("Sz.P.", ["Sz.P."]),
    ("p.o.", ["p.o."]),
    ("k.o.", ["k.o."]),
    ("m.st.", ["m.st."]),
    ("dra.", ["dra", "."]),
    ("pp.", ["pp."]),
    ("oo.", ["oo."]),
]

HYPHEN_TESTS = [
    ("5-fluoropentylo-3-pirydynyloindol", ["5-fluoropentylo-3-pirydynyloindol"]),
    ("NESS-040C5", ["NESS-040C5"]),
    ("JTE-7-31", ["JTE-7-31"]),
    ("BAY-59-3074", ["BAY-59-3074"]),
    ("BAY-38-7271", ["BAY-38-7271"]),
    ("STS-135", ["STS-135"]),
    ("5F-PB-22", ["5F-PB-22"]),
    ("cztero-", ["cztero-"]),
    ("jedno-", ["jedno-"]),
    ("dwu-", ["dwu-"]),
    ("trzy-", ["trzy-"]),
    ("b-adoratorzy", ["b-adoratorzy"]),
    ("2-3-4 drzewa", ["2-3-4", "drzewa"]),
    ("b-drzewa", ["b-drzewa"]),
]


TESTCASES = DOT_TESTS + HYPHEN_TESTS


@pytest.mark.parametrize("text,expected_tokens", TESTCASES)
def test_tokenizer_handles_testcases(pl_tokenizer, text, expected_tokens):
    tokens = pl_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
