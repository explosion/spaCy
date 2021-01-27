import pytest


def test_noun_chunks_is_parsed_fr(fr_tokenizer):
    """Test that noun_chunks raises Value Error for 'fr' language if Doc is not parsed."""
    doc = fr_tokenizer("trouver des travaux antérieurs")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
