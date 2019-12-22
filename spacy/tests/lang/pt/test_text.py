import pytest
from spacy.lang.pt.lex_attrs import like_num


@pytest.mark.parametrize("word", ["onze", "quadragésimo"])
def test_pt_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
