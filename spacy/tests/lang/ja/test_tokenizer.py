# coding: utf-8
from __future__ import unicode_literals

import pytest


TOKENIZER_TESTS = [
        ("日本語だよ", ['日本語', 'だ', 'よ']),
        ("東京タワーの近くに住んでいます。", ['東京', 'タワー', 'の', '近く', 'に', '住ん', 'で', 'い', 'ます', '。']),
        ("吾輩は猫である。", ['吾輩', 'は', '猫', 'で', 'ある', '。']),
        ("月に代わって、お仕置きよ!", ['月', 'に', '代わっ', 'て', '、', 'お仕置き', 'よ', '!']),
        ("すもももももももものうち", ['すもも', 'も', 'もも', 'も', 'もも', 'の', 'うち'])
]


@pytest.mark.parametrize('text,expected_tokens', TOKENIZER_TESTS)
def test_japanese_tokenizer(ja_tokenizer, text, expected_tokens):
    tokens = [token.text for token in ja_tokenizer(text)]
    assert tokens == expected_tokens
