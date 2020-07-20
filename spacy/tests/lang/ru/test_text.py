import pytest
from spacy.lang.ru.lex_attrs import like_num


@pytest.mark.parametrize("word", ["одиннадцать"])
def test_ru_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
