# coding: utf8
from __future__ import unicode_literals

import pytest


INFIX_HYPHEN_TESTS = [
    ("Бала-чака жакшыбы?", "Бала-чака жакшыбы ?".split()),
    ("Кыз-келиндер кийими.", "Кыз-келиндер кийими .".split()),
]

PUNC_INSIDE_WORDS_TESTS = [
    (
        "Пассажир саны - 2,13 млн — киши/күнүнө (2010), 783,9 млн. киши/жылына.",
        "Пассажир саны - 2,13 млн — киши / күнүнө ( 2010 ) ,"
        " 783,9 млн. киши / жылына .".split(),
    ),
    ('То"кой', 'То " кой'.split()),
]

MIXED_ORDINAL_NUMS_TESTS = [("Эртең 22-январь...", "Эртең 22 - январь ...".split())]

ABBREV_TESTS = [
    ("Маселе б-ча эртең келет", "Маселе б-ча эртең келет".split()),
    ("Ахунбаев көч. турат.", "Ахунбаев көч. турат .".split()),
    ("«3-жылы (б.з.ч.) туулган", "« 3 - жылы ( б.з.ч. ) туулган".split()),
    ("Жүгөрү ж.б. дандар колдонулат", "Жүгөрү ж.б. дандар колдонулат".split()),
    ("3-4 кк. курулган.", "3 - 4 кк. курулган .".split()),
]

NAME_ABBREV_TESTS = [
    ("М.Жумаш", "М.Жумаш".split()),
    ("М.жумаш", "М.жумаш".split()),
    ("м.Жумаш", "м . Жумаш".split()),
    ("Жумаш М.Н.", "Жумаш М.Н.".split()),
    ("Жумаш.", "Жумаш .".split()),
]

TYPOS_IN_PUNC_TESTS = [
    ("«3-жылда , туулган", "« 3 - жылда , туулган".split()),
    ("«3-жылда,туулган", "« 3 - жылда , туулган".split()),
    ("«3-жылда,туулган.", "« 3 - жылда , туулган .".split()),
    ("Ал иштейт(качан?)", "Ал иштейт ( качан ? )".split()),
    ("Ал (качан?)иштейт", "Ал ( качан ?) иштейт".split()),  # "?)" => "?)" or "? )"
]

LONG_TEXTS_TESTS = [
    (
        "Алыскы өлкөлөргө аздыр-көптүр татаалыраак жүрүштөргө чыккандар "
        "азыраак: ал бир топ кымбат жана логистика маселесинин айынан "
        "кыйла татаал. Мисалы, январдагы майрамдарда Мароккого үчүнчү "
        "категориядагы маршрутка (100 чакырымдан кем эмес) барып "
        "келгенге аракет кылдык.",
        "Алыскы өлкөлөргө аздыр-көптүр татаалыраак жүрүштөргө чыккандар "
        "азыраак : ал бир топ кымбат жана логистика маселесинин айынан "
        "кыйла татаал . Мисалы , январдагы майрамдарда Мароккого үчүнчү "
        "категориядагы маршрутка ( 100 чакырымдан кем эмес ) барып "
        "келгенге аракет кылдык .".split(),
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
        "ит, мышык ж.б.у.с. үй жаныбарлары.",
        ["ит", ",", "мышык", "жана башка ушул сыяктуу", "үй", "жаныбарлары", "."],
    )
]


@pytest.mark.parametrize("text,expected_tokens", TESTCASES)
def test_ky_tokenizer_handles_testcases(ky_tokenizer, text, expected_tokens):
    tokens = [token.text for token in ky_tokenizer(text) if not token.is_space]
    assert expected_tokens == tokens


@pytest.mark.parametrize("text,norms", NORM_TESTCASES)
def test_ky_tokenizer_handles_norm_exceptions(ky_tokenizer, text, norms):
    tokens = ky_tokenizer(text)
    assert [token.norm_ for token in tokens] == norms
