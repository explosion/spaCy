# coding: utf8
from __future__ import unicode_literals

import pytest


INFIX_HYPHEN_TESTS = [
    ("Явым-төшем күләме.", "Явым-төшем күләме .".split()),
    ("Хатын-кыз киеме.", "Хатын-кыз киеме .".split()),
]

PUNC_INSIDE_WORDS_TESTS = [
    (
        "Пассаҗир саны - 2,13 млн — кеше/көндә (2010), 783,9 млн. кеше/елда.",
        "Пассаҗир саны - 2,13 млн — кеше / көндә ( 2010 ) ,"
        " 783,9 млн. кеше / елда .".split(),
    ),
    ('Ту"кай', 'Ту " кай'.split()),
]

MIXED_ORDINAL_NUMS_TESTS = [
    ("Иртәгә 22нче гыйнвар...", "Иртәгә 22нче гыйнвар ...".split())
]

ABBREV_TESTS = [
    ("«3 елда (б.э.к.) туган", "« 3 елда ( б.э.к. ) туган".split()),
    ("тукымадан һ.б.ш. тегелгән.", "тукымадан һ.б.ш. тегелгән .".split()),
]

NAME_ABBREV_TESTS = [
    ("Ә.Тукай", "Ә.Тукай".split()),
    ("Ә.тукай", "Ә.тукай".split()),
    ("ә.Тукай", "ә . Тукай".split()),
    ("Миләүшә.", "Миләүшә .".split()),
]

TYPOS_IN_PUNC_TESTS = [
    ("«3 елда , туган", "« 3 елда , туган".split()),
    ("«3 елда,туган", "« 3 елда , туган".split()),
    ("«3 елда,туган.", "« 3 елда , туган .".split()),
    ("Ул эшли(кайчан?)", "Ул эшли ( кайчан ? )".split()),
    ("Ул (кайчан?)эшли", "Ул ( кайчан ?) эшли".split()),  # "?)" => "?)" or "? )"
]

LONG_TEXTS_TESTS = [
    (
        "Иң борынгы кешеләр суыклар һәм салкын кышлар булмый торган җылы"
        "якларда яшәгәннәр, шуңа күрә аларга кием кирәк булмаган.Йөз"
        "меңнәрчә еллар үткән, борынгы кешеләр акрынлап Европа һәм Азиянең"
        "салкын илләрендә дә яши башлаганнар. Алар кырыс һәм салкын"
        "кышлардан саклану өчен кием-салым уйлап тапканнар - итәк.",
        "Иң борынгы кешеләр суыклар һәм салкын кышлар булмый торган җылы"
        "якларда яшәгәннәр , шуңа күрә аларга кием кирәк булмаган . Йөз"
        "меңнәрчә еллар үткән , борынгы кешеләр акрынлап Европа һәм Азиянең"
        "салкын илләрендә дә яши башлаганнар . Алар кырыс һәм салкын"
        "кышлардан саклану өчен кием-салым уйлап тапканнар - итәк .".split(),
    )
]

TESTCASES = (
    INFIX_HYPHEN_TESTS
    + PUNC_INSIDE_WORDS_TESTS
    + MIXED_ORDINAL_NUMS_TESTS
    + ABBREV_TESTS
    + NAME_ABBREV_TESTS
    + LONG_TEXTS_TESTS
    + TYPOS_IN_PUNC_TESTS
)

NORM_TESTCASES = [
    (
        "тукымадан һ.б.ш. тегелгән.",
        ["тукымадан", "һәм башка шундыйлар", "тегелгән", "."],
    )
]


@pytest.mark.parametrize("text,expected_tokens", TESTCASES)
def test_tt_tokenizer_handles_testcases(tt_tokenizer, text, expected_tokens):
    tokens = [token.text for token in tt_tokenizer(text) if not token.is_space]
    assert expected_tokens == tokens


@pytest.mark.parametrize("text,norms", NORM_TESTCASES)
def test_tt_tokenizer_handles_norm_exceptions(tt_tokenizer, text, norms):
    tokens = tt_tokenizer(text)
    assert [token.norm_ for token in tokens] == norms
