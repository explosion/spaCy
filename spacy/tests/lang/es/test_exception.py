import pytest


@pytest.mark.issue(3277)
def test_issue3277(es_tokenizer):
    """Test that hyphens are split correctly as prefixes."""
    doc = es_tokenizer("—Yo me llamo... –murmuró el niño– Emilio Sánchez Pérez.")
    assert len(doc) == 14
    assert doc[0].text == "\u2014"
    assert doc[5].text == "\u2013"
    assert doc[9].text == "\u2013"


@pytest.mark.parametrize(
    "text,lemma",
    [
        ("aprox.", "aproximadamente"),
        ("esq.", "esquina"),
        ("pág.", "página"),
        ("p.ej.", "por ejemplo"),
    ],
)
def test_es_tokenizer_handles_abbr(es_tokenizer, text, lemma):
    tokens = es_tokenizer(text)
    assert len(tokens) == 1


def test_es_tokenizer_handles_exc_in_text(es_tokenizer):
    text = "Mariano Rajoy ha corrido aprox. medio kilómetro"
    tokens = es_tokenizer(text)
    assert len(tokens) == 7
    assert tokens[4].text == "aprox."
