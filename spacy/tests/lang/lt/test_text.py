# coding: utf-8
from __future__ import unicode_literals

import pytest


def test_lt_tokenizer_handles_long_text(lt_tokenizer):
    text = """Tokios sausros kriterijus atitinka pirmadienį atlikti skaičiavimai, palyginus faktinį ir žemiausią vidutinį daugiametį vandens lygį. Nustatyta, kad iš 48 šalies vandens matavimo stočių 28-iose stotyse vandens lygis yra žemesnis arba lygus žemiausiam vidutiniam daugiamečiam šiltojo laikotarpio vandens lygiui."""
    tokens = lt_tokenizer(text)
    assert len(tokens) == 42


@pytest.mark.parametrize(
    "text,length",
    [
        (
            "177R Parodų rūmai–Ozo g. nuo vasario 18 d. bus skelbiamas interneto tinklalapyje.",
            17,
        ),
        (
            "ISM universiteto doc. dr. Ieva Augutytė-Kvedaravičienė pastebi, kad tyrimais nustatyti elgesio pokyčiai.",
            18,
        ),
    ],
)
def test_lt_tokenizer_handles_punct_abbrev(lt_tokenizer, text, length):
    tokens = lt_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize("text", ["km.", "pvz.", "biol."])
def test_lt_tokenizer_abbrev_exceptions(lt_tokenizer, text):
    tokens = lt_tokenizer(text)
    assert len(tokens) == 2


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10,000", True),
        ("10,00", True),
        ("999.0", True),
        ("vienas", True),
        ("du", True),
        ("milijardas", True),
        ("šuo", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lt_lex_attrs_like_number(lt_tokenizer, text, match):
    tokens = lt_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match
