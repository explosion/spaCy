# coding: utf-8
from __future__ import unicode_literals

import pytest


# fmt: off
TOKENIZER_TESTS = [
    ("日本語だよ", ['日本', '語', 'だ', 'よ']),
    ("東京タワーの近くに住んでいます。", ['東京', 'タワー', 'の', '近く', 'に', '住ん', 'で', 'い', 'ます', '。']),
    ("吾輩は猫である。", ['吾輩', 'は', '猫', 'で', 'ある', '。']),
    ("月に代わって、お仕置きよ!", ['月', 'に', '代わっ', 'て', '、', 'お', '仕置き', 'よ', '!']),
    ("すもももももももものうち", ['すもも', 'も', 'もも', 'も', 'もも', 'の', 'うち'])
]

TAG_TESTS = [
    ("日本語だよ", ['名詞,固有名詞,地名,国', '名詞,普通名詞,一般,*', '助動詞,*,*,*', '助詞,終助詞,*,*']),
    ("東京タワーの近くに住んでいます。", ['名詞,固有名詞,地名,一般', '名詞,普通名詞,一般,*', '助詞,格助詞,*,*', '名詞,普通名詞,副詞可能,*', '助詞,格助詞,*,*', '動詞,一般,*,*', '助詞,接続助詞,*,*', '動詞,非自立可能,*,*', '助動詞,*,*,*', '補助記号,句点,*,*']),
    ("吾輩は猫である。", ['代名詞,*,*,*', '助詞,係助詞,*,*', '名詞,普通名詞,一般,*', '助動詞,*,*,*', '動詞,非自立可能,*,*', '補助記号,句点,*,*']),
    ("月に代わって、お仕置きよ!", ['名詞,普通名詞,助数詞可能,*', '助詞,格助詞,*,*', '動詞,一般,*,*', '助詞,接続助詞,*,*', '補助記号,読点,*,*', '接頭辞,*,*,*', '名詞,普通名詞,一般,*', '助詞,終助詞,*,*', '補助記号,句点,*,*']),
    ("すもももももももものうち", ['名詞,普通名詞,一般,*', '助詞,係助詞,*,*', '名詞,普通名詞,一般,*', '助詞,係助詞,*,*', '名詞,普通名詞,一般,*', '助詞,格助詞,*,*', '名詞,普通名詞,副詞可能,*'])
]

POS_TESTS = [
    ('日本語だよ', ['PROPN', 'NOUN', 'AUX', 'PART']),
    ('東京タワーの近くに住んでいます。', ['PROPN', 'NOUN', 'ADP', 'NOUN', 'ADP', 'VERB', 'SCONJ', 'VERB', 'AUX', 'PUNCT']),
    ('吾輩は猫である。', ['PRON', 'ADP', 'NOUN', 'AUX', 'VERB', 'PUNCT']),
    ('月に代わって、お仕置きよ!', ['NOUN', 'ADP', 'VERB', 'SCONJ', 'PUNCT', 'NOUN', 'NOUN', 'PART', 'PUNCT']),
    ('すもももももももものうち', ['NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN'])
]
# fmt: on


@pytest.mark.parametrize("text,expected_tokens", TOKENIZER_TESTS)
def test_ja_tokenizer(ja_tokenizer, text, expected_tokens):
    tokens = [token.text for token in ja_tokenizer(text)]
    assert tokens == expected_tokens


@pytest.mark.parametrize("text,expected_tags", TAG_TESTS)
def test_ja_tokenizer_tags(ja_tokenizer, text, expected_tags):
    tags = [token.tag_ for token in ja_tokenizer(text)]
    assert tags == expected_tags


@pytest.mark.parametrize("text,expected_pos", POS_TESTS)
def test_ja_tokenizer_pos(ja_tokenizer, text, expected_pos):
    pos = [token.pos_ for token in ja_tokenizer(text)]
    assert pos == expected_pos
