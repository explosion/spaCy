import pytest


@pytest.mark.parametrize("text", ["ہےں۔", "کیا۔"])
def test_contractions(ur_tokenizer, text):
    """Test specific Urdu punctuation character"""
    tokens = ur_tokenizer(text)
    assert len(tokens) == 2
