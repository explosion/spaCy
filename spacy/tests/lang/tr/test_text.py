import pytest
from spacy.lang.tr.lex_attrs import like_num


@pytest.mark.parametrize(
    "word",
    [
        "bir",
        "iki",
        "dört",
        "altı",
        "milyon",
        "100",
        "birinci",
        "üçüncü",
        "beşinci",
        "100üncü",
        "8inci",
    ],
)
def test_tr_lex_attrs_like_number_cardinal_ordinal(word):
    assert like_num(word)


@pytest.mark.parametrize("word", ["beş", "yedi", "yedinci", "birinci"])
def test_tr_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
