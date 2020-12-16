# coding: utf-8
from __future__ import unicode_literals

import pytest

from ...tokenizer.test_naughty_strings import NAUGHTY_STRINGS
from spacy.lang.ja import Japanese, DetailedToken

# fmt: off
TOKENIZER_TESTS = [
    ("日本語だよ", ['日本', '語', 'だ', 'よ']),
    ("東京タワーの近くに住んでいます。", ['東京', 'タワー', 'の', '近く', 'に', '住ん', 'で', 'い', 'ます', '。']),
    ("吾輩は猫である。", ['吾輩', 'は', '猫', 'で', 'ある', '。']),
    ("月に代わって、お仕置きよ!", ['月', 'に', '代わっ', 'て', '、', 'お', '仕置き', 'よ', '!']),
    ("すもももももももものうち", ['すもも', 'も', 'もも', 'も', 'もも', 'の', 'うち'])
]

TAG_TESTS = [
    ("日本語だよ", ['名詞-固有名詞-地名-国', '名詞-普通名詞-一般', '助動詞', '助詞-終助詞']),
    ("東京タワーの近くに住んでいます。", ['名詞-固有名詞-地名-一般', '名詞-普通名詞-一般', '助詞-格助詞', '名詞-普通名詞-副詞可能', '助詞-格助詞', '動詞-一般', '助詞-接続助詞', '動詞-非自立可能', '助動詞', '補助記号-句点']),
    ("吾輩は猫である。", ['代名詞', '助詞-係助詞', '名詞-普通名詞-一般', '助動詞', '動詞-非自立可能', '補助記号-句点']),
    ("月に代わって、お仕置きよ!", ['名詞-普通名詞-助数詞可能', '助詞-格助詞', '動詞-一般', '助詞-接続助詞', '補助記号-読点', '接頭辞', '名詞-普通名詞-一般', '助詞-終助詞', '補助記号-句点']),
    ("すもももももももものうち", ['名詞-普通名詞-一般', '助詞-係助詞', '名詞-普通名詞-一般', '助詞-係助詞', '名詞-普通名詞-一般', '助詞-格助詞', '名詞-普通名詞-副詞可能'])
]

POS_TESTS = [
    ('日本語だよ', ['fish', 'NOUN', 'AUX', 'PART']),
    ('東京タワーの近くに住んでいます。', ['PROPN', 'NOUN', 'ADP', 'NOUN', 'ADP', 'VERB', 'SCONJ', 'VERB', 'AUX', 'PUNCT']),
    ('吾輩は猫である。', ['PRON', 'ADP', 'NOUN', 'AUX', 'VERB', 'PUNCT']),
    ('月に代わって、お仕置きよ!', ['NOUN', 'ADP', 'VERB', 'SCONJ', 'PUNCT', 'NOUN', 'NOUN', 'PART', 'PUNCT']),
    ('すもももももももものうち', ['NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN'])
]

SENTENCE_TESTS = [
        ('あれ。これ。', ['あれ。', 'これ。']),
        ('「伝染るんです。」という漫画があります。', 
            ['「伝染るんです。」という漫画があります。']),
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


#XXX This isn't working? Always passes
@pytest.mark.parametrize("text,expected_pos", POS_TESTS)
def test_ja_tokenizer_pos(ja_tokenizer, text, expected_pos):
    pos = [token.pos_ for token in ja_tokenizer(text)]
    assert pos == expected_pos


@pytest.mark.skip(reason="sentence segmentation in tokenizer is buggy")
@pytest.mark.parametrize("text,expected_sents", SENTENCE_TESTS)
def test_ja_tokenizer_pos(ja_tokenizer, text, expected_sents):
    sents = [str(sent) for sent in ja_tokenizer(text).sents]
    assert sents == expected_sents


def test_ja_tokenizer_extra_spaces(ja_tokenizer):
    # note: three spaces after "I"
    tokens = ja_tokenizer("I   like cheese.")
    assert tokens[1].orth_ == "  "


@pytest.mark.parametrize("text", NAUGHTY_STRINGS)
def test_ja_tokenizer_naughty_strings(ja_tokenizer, text):
    tokens = ja_tokenizer(text)
    assert tokens.text_with_ws == text


@pytest.mark.parametrize("text,len_a,len_b,len_c",
    [
        ("選挙管理委員会", 4, 3, 1),
        ("客室乗務員", 3, 2, 1),
        ("労働者協同組合", 4, 3, 1),
        ("機能性食品", 3, 2, 1),
    ]
)
def test_ja_tokenizer_split_modes(ja_tokenizer, text, len_a, len_b, len_c):
    nlp_a = Japanese(meta={"tokenizer": {"config": {"split_mode": "A"}}})
    nlp_b = Japanese(meta={"tokenizer": {"config": {"split_mode": "B"}}})
    nlp_c = Japanese(meta={"tokenizer": {"config": {"split_mode": "C"}}})

    assert len(ja_tokenizer(text)) == len_a
    assert len(nlp_a(text)) == len_a
    assert len(nlp_b(text)) == len_b
    assert len(nlp_c(text)) == len_c


@pytest.mark.parametrize("text,sub_tokens_list_a,sub_tokens_list_b,sub_tokens_list_c",
    [
        (
            "選挙管理委員会",
            [None, None, None, None],
            [None, None, [
                [
                    DetailedToken(surface='委員', tag='名詞-普通名詞-一般', inf='', lemma='委員', reading='イイン', sub_tokens=None),
                    DetailedToken(surface='会', tag='名詞-普通名詞-一般', inf='', lemma='会', reading='カイ', sub_tokens=None),
                ]
            ]],
            [[
                [
                    DetailedToken(surface='選挙', tag='名詞-普通名詞-サ変可能', inf='', lemma='選挙', reading='センキョ', sub_tokens=None),
                    DetailedToken(surface='管理', tag='名詞-普通名詞-サ変可能', inf='', lemma='管理', reading='カンリ', sub_tokens=None),
                    DetailedToken(surface='委員', tag='名詞-普通名詞-一般', inf='', lemma='委員', reading='イイン', sub_tokens=None),
                    DetailedToken(surface='会', tag='名詞-普通名詞-一般', inf='', lemma='会', reading='カイ', sub_tokens=None),
                ], [
                    DetailedToken(surface='選挙', tag='名詞-普通名詞-サ変可能', inf='', lemma='選挙', reading='センキョ', sub_tokens=None),
                    DetailedToken(surface='管理', tag='名詞-普通名詞-サ変可能', inf='', lemma='管理', reading='カンリ', sub_tokens=None),
                    DetailedToken(surface='委員会', tag='名詞-普通名詞-一般', inf='', lemma='委員会', reading='イインカイ', sub_tokens=None),
                ]
            ]]
        ),
    ]
)
def test_ja_tokenizer_sub_tokens(ja_tokenizer, text, sub_tokens_list_a, sub_tokens_list_b, sub_tokens_list_c):
    nlp_a = Japanese(meta={"tokenizer": {"config": {"split_mode": "A"}}})
    nlp_b = Japanese(meta={"tokenizer": {"config": {"split_mode": "B"}}})
    nlp_c = Japanese(meta={"tokenizer": {"config": {"split_mode": "C"}}})

    assert ja_tokenizer(text).user_data["sub_tokens"] == sub_tokens_list_a
    assert nlp_a(text).user_data["sub_tokens"] == sub_tokens_list_a
    assert nlp_b(text).user_data["sub_tokens"] == sub_tokens_list_b
    assert nlp_c(text).user_data["sub_tokens"] == sub_tokens_list_c


@pytest.mark.parametrize("text,inflections,reading_forms",
    [
        (
            "取ってつけた",
            ("五段-ラ行,連用形-促音便", "", "下一段-カ行,連用形-一般", "助動詞-タ,終止形-一般"),
            ("トッ", "テ", "ツケ", "タ"),
        ),
    ]
)
def test_ja_tokenizer_inflections_reading_forms(ja_tokenizer, text, inflections, reading_forms):
    assert ja_tokenizer(text).user_data["inflections"] == inflections
    assert ja_tokenizer(text).user_data["reading_forms"] == reading_forms


def test_ja_tokenizer_emptyish_texts(ja_tokenizer):
    doc = ja_tokenizer("")
    assert len(doc) == 0
    doc = ja_tokenizer(" ")
    assert len(doc) == 1
    doc = ja_tokenizer("\n\n\n \t\t \n\n\n")
    assert len(doc) == 1
