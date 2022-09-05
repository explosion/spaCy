import pytest


def test_la_tokenizer_handles_exc_in_text(la_tokenizer):
    text = "scio te omnia facturum, ut nobiscum quam primum sis"
    tokens = la_tokenizer(text)
    assert len(tokens) == 11
    assert tokens[6].text == "nobis"
