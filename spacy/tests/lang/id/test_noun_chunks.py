import pytest


def test_noun_chunks_is_parsed_id(id_tokenizer):
    """Test that noun_chunks raises Value Error for 'id' language if Doc is not parsed."""
    doc = id_tokenizer("sebelas")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
