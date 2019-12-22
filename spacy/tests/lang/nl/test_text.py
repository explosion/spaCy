import pytest
from spacy.lang.nl.lex_attrs import like_num


@pytest.mark.parametrize("word", ["elf", "elfde"])
def test_nl_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())


@pytest.mark.parametrize(
    "text,num_tokens",
    [
        (
            "De aftredende minister-president benadrukte al dat zijn partij inhoudelijk weinig gemeen heeft met de groenen.",
            16,
        ),
        ("Hij is sociaal-cultureel werker.", 5),
        ("Er staan een aantal dure auto's in de garage.", 10),
    ],
)
def test_tokenizer_doesnt_split_hyphens(nl_tokenizer, text, num_tokens):
    tokens = nl_tokenizer(text)
    assert len(tokens) == num_tokens
