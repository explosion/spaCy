import pytest


def test_noun_chunks_is_parsed_fa(fa_tokenizer):
    """Test that noun_chunks raises Value Error for 'fa' language if Doc is not parsed."""

    doc = fa_tokenizer("این یک جمله نمونه می باشد.")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
