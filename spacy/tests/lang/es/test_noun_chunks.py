import pytest


def test_noun_chunks_is_parsed_es(es_tokenizer):
    """Test that noun_chunks raises Value Error for 'es' language if Doc is not parsed."""
    doc = es_tokenizer("en Oxford este verano")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
