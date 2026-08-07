import pytest


@pytest.mark.parametrize(
    "text,expected_tokens,expected_norms",
    [("a-e", ["a-", "e"], ["à", "e"]), ("co-i", ["co-", "i"], ["con", "i"])],
)
def test_prepositions(lij_tokenizer, text, expected_tokens, expected_norms):
    """Test that compound prepositions are split correctly."""
    tokens = lij_tokenizer(text)
    assert len(tokens) == 2
    assert [t.text for t in tokens] == expected_tokens
    assert [t.norm_ for t in tokens] == expected_norms
