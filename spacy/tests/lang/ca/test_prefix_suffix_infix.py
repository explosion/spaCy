import pytest


@pytest.mark.parametrize(
    "text,expected_tokens",
    [
        ("d'un", ["d'", "un"]),
        ("s'ha", ["s'", "ha"]),
        ("del", ["d", "el"]),
        ("cantar-te", ["cantar", "-te"]),
        ("-hola", ["-", "hola"]),
    ],
)
def test_contractions(ca_tokenizer, text, expected_tokens):
    """Test that the contractions are split into two tokens"""
    tokens = ca_tokenizer(text)
    assert len(tokens) == 2
    assert [t.text for t in tokens] == expected_tokens
