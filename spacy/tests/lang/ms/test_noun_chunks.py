import pytest


def test_noun_chunks_is_parsed_ms(ms_tokenizer):
    """Test that noun_chunks raises Value Error for 'ms' language if Doc is not parsed."""
    doc = ms_tokenizer("sebelas")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
