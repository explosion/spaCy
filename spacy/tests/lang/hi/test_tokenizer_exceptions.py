import pytest


def test_hi_tokenizer_handles_long_text(hi_tokenizer):
    text = """मैंने आपको कल कुछ फल रस बनाने के लिए दिए थे।"""
    tokens = hi_tokenizer(text)
    expected_tokens = ["मैं", "ने", "आप", "को",]
    assert expected_tokens == [t.text for t in tokens[:4]]
