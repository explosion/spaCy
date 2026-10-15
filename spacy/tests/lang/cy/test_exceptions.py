import pytest


@pytest.mark.parametrize(
    "text,norm",
    [
        ("e.e.", "er enghraifft"),
        ("h.y.", "hynny yw"),
        ("a.y.b.", "ac yn y blaen"),
    ],
)
def test_cy_tokenizer_handles_abbreviation(cy_tokenizer, text, norm):
    tokens = cy_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].text == text
    assert tokens[0].norm_ == norm


def test_cy_tokenizer_abbreviation_in_sentence(cy_tokenizer):
    tokens = [t.text for t in cy_tokenizer("Ffrwythau, e.e. afalau a gellyg.")]
    assert tokens == ["Ffrwythau", ",", "e.e.", "afalau", "a", "gellyg", "."]


@pytest.mark.parametrize("text", ["Dr.", "Mr.", "Mrs."])
def test_cy_tokenizer_handles_title_abbreviation(cy_tokenizer, text):
    tokens = cy_tokenizer(text + " Jones")
    assert [t.text for t in tokens] == [text, "Jones"]
