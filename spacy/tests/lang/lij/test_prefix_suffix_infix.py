import pytest


@pytest.mark.parametrize("text", ["'90", "’90", "‘90"])
def test_lij_tokenizer_handles_year_elision(lij_tokenizer, text):
    """Test that elided years (e.g. '90 for 1990) are not split."""
    tokens = lij_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text,expected_tokens", [("10°C", ["10", "°C"])])
def test_lij_tokenizer_handles_degrees(lij_tokenizer, text, expected_tokens):
    """Test that in degree units the degree symbol isn't split from the unit."""
    tokens = lij_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list


@pytest.mark.parametrize("text,expected_tokens", [("'n'atra", ["'n'", "atra"])])
def test_lij_tokenizer_handles_left_elision(lij_tokenizer, text, expected_tokens):
    """Test that left-eliding expressions are not split from their left apostrophe."""
    tokens = lij_tokenizer(text)
    token_list = [token.text for token in tokens if not token.is_space]
    assert expected_tokens == token_list
