import pytest

from spacy.lang.cy.lex_attrs import like_num


@pytest.mark.parametrize("text", ["10", "1,000", "3.5", "1/2", "-7", "+12"])
def test_cy_like_num_digits(text):
    assert like_num(text)


@pytest.mark.parametrize(
    "text",
    [
        "un",
        "dau",
        "ddwy",
        "tri",
        "thair",
        "pedwar",
        "bum",
        "chwech",
        "deg",
        "ddeg",
        "deuddeg",
        "pymtheg",
        "deunaw",
        "ugain",
        "hugain",
        "cant",
        "gant",
        "mil",
        "miliwn",
        "Deg",
        "UGAIN",
    ],
)
def test_cy_like_num_number_words(text):
    assert like_num(text)


@pytest.mark.parametrize("text", ["ar", "cath", "a", "deng-", "unwaith"])
def test_cy_like_num_not_number(text):
    assert not like_num(text)


def test_cy_tokenizer_marks_number_words(cy_tokenizer):
    tokens = cy_tokenizer("un ar ddeg o gathod")
    assert [t.like_num for t in tokens] == [True, False, True, False, False]
