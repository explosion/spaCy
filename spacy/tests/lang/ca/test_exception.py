import pytest


@pytest.mark.parametrize(
    "text,lemma",
    [("aprox.", "aproximadament"), ("pàg.", "pàgina"), ("p.ex.", "per exemple")],
)
def test_ca_tokenizer_handles_abbr(ca_tokenizer, text, lemma):
    tokens = ca_tokenizer(text)
    assert len(tokens) == 1


def test_ca_tokenizer_handles_exc_in_text(ca_tokenizer):
    text = "La Núria i el Pere han vingut aprox. a les 7 de la tarda."
    tokens = ca_tokenizer(text)
    assert len(tokens) == 15
    assert tokens[7].text == "aprox."
