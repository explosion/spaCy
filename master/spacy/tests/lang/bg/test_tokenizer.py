import pytest


def test_bg_tokenizer_handles_final_diacritics(bg_tokenizer):
    text = "Ня̀маше яйца̀. Ня̀маше яйца̀."
    tokens = bg_tokenizer(text)
    assert tokens[1].text == "яйца̀"
    assert tokens[2].text == "."
