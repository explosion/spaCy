# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lang.zh import _get_pkuseg_trie_data


# fmt: off
TEXTS = ("作为语言而言，为世界使用人数最多的语言，目前世界有五分之一人口做为母语。",)
JIEBA_TOKENIZER_TESTS = [
    (TEXTS[0],
        ['作为', '语言', '而言', '，', '为', '世界', '使用', '人', '数最多',
         '的', '语言', '，', '目前', '世界', '有', '五分之一', '人口', '做',
         '为', '母语', '。']),
]
PKUSEG_TOKENIZER_TESTS = [
    (TEXTS[0],
        ['作为', '语言', '而言', '，', '为', '世界', '使用', '人数', '最多',
         '的', '语言', '，', '目前', '世界', '有', '五分之一', '人口', '做为',
         '母语', '。']),
]
# fmt: on


@pytest.mark.parametrize("text", TEXTS)
def test_zh_tokenizer_char(zh_tokenizer_char, text):
    tokens = [token.text for token in zh_tokenizer_char(text)]
    assert tokens == list(text)


@pytest.mark.parametrize("text,expected_tokens", JIEBA_TOKENIZER_TESTS)
def test_zh_tokenizer_jieba(zh_tokenizer_jieba, text, expected_tokens):
    tokens = [token.text for token in zh_tokenizer_jieba(text)]
    assert tokens == expected_tokens


@pytest.mark.parametrize("text,expected_tokens", PKUSEG_TOKENIZER_TESTS)
def test_zh_tokenizer_pkuseg(zh_tokenizer_pkuseg, text, expected_tokens):
    tokens = [token.text for token in zh_tokenizer_pkuseg(text)]
    assert tokens == expected_tokens


def test_zh_tokenizer_pkuseg_user_dict(zh_tokenizer_pkuseg):
    user_dict = _get_pkuseg_trie_data(zh_tokenizer_pkuseg.pkuseg_seg.preprocesser.trie)
    zh_tokenizer_pkuseg.pkuseg_update_user_dict(["nonsense_asdf"])
    updated_user_dict = _get_pkuseg_trie_data(
        zh_tokenizer_pkuseg.pkuseg_seg.preprocesser.trie
    )
    assert len(user_dict) == len(updated_user_dict) - 1

    # reset user dict
    zh_tokenizer_pkuseg.pkuseg_update_user_dict([], reset=True)
    reset_user_dict = _get_pkuseg_trie_data(
        zh_tokenizer_pkuseg.pkuseg_seg.preprocesser.trie
    )
    assert len(reset_user_dict) == 0


def test_extra_spaces(zh_tokenizer_char):
    # note: three spaces after "I"
    tokens = zh_tokenizer_char("I   like cheese.")
    assert tokens[1].orth_ == "  "
