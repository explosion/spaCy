import pytest


@pytest.mark.parametrize(
    "text,lemma",
    [("aprox.", "aproximadament"), ("pàg.", "pàgina"), ("p.ex.", "per exemple")],
)
def test_ca_tokenizer_handles_abbr(ca_tokenizer, text, lemma):
    tokens = ca_tokenizer(text)
    assert len(tokens) == 1


def test_ca_tokenizer_handles_exc_in_text(ca_tokenizer):
    text = "La Dra. Puig viu a la pl. dels Til·lers."
    doc = ca_tokenizer(text)
    assert [t.text for t in doc] == [
        "La",
        "Dra.",
        "Puig",
        "viu",
        "a",
        "la",
        "pl.",
        "d",
        "els",
        "Til·lers",
        ".",
    ]
