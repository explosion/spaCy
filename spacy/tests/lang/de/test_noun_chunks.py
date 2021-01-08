import pytest


def test_noun_chunks_is_parsed_de(de_tokenizer):
    """Test that noun_chunks raises Value Error for 'de' language if Doc is not parsed."""
    doc = de_tokenizer("Er lag auf seinem")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
