import pytest

from spacy.lang.hy.lex_attrs import like_num


@pytest.mark.parametrize("word", ["հիսուն"])
def test_hy_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
