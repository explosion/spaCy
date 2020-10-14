import pytest


def test_noun_chunks_is_parsed_nb(nb_tokenizer):
    """Test that noun_chunks raises Value Error for 'nb' language if Doc is not parsed."""
    doc = nb_tokenizer("Smørsausen brukes bl.a. til")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
