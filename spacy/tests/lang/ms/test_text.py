import pytest

from spacy.lang.ms.lex_attrs import like_num


@pytest.mark.parametrize("word", ["sebelas"])
def test_ms_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
