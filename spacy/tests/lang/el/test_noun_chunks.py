import pytest


def test_noun_chunks_is_parsed_el(el_tokenizer):
    """Test that noun_chunks raises Value Error for 'el' language if Doc is not parsed."""
    doc = el_tokenizer("είναι χώρα της νοτιοανατολικής")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
