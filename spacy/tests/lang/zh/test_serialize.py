# coding: utf-8
from __future__ import unicode_literals

import pytest
from spacy.lang.zh import Chinese
from ...util import make_tempdir


def zh_tokenizer_serialize(zh_tokenizer):
    tokenizer_bytes = zh_tokenizer.to_bytes()
    nlp = Chinese(meta={"tokenizer": {"config": {"use_jieba": False}}})
    nlp.tokenizer.from_bytes(tokenizer_bytes)
    assert tokenizer_bytes == nlp.tokenizer.to_bytes()

    with make_tempdir() as d:
        file_path = d / "tokenizer"
        zh_tokenizer.to_disk(file_path)
        nlp = Chinese(meta={"tokenizer": {"config": {"use_jieba": False}}})
        nlp.tokenizer.from_disk(file_path)
        assert tokenizer_bytes == nlp.tokenizer.to_bytes()


def test_zh_tokenizer_serialize_char(zh_tokenizer_char):
    zh_tokenizer_serialize(zh_tokenizer_char)


def test_zh_tokenizer_serialize_jieba(zh_tokenizer_jieba):
    zh_tokenizer_serialize(zh_tokenizer_jieba)


def test_zh_tokenizer_serialize_pkuseg(zh_tokenizer_pkuseg):
    zh_tokenizer_serialize(zh_tokenizer_pkuseg)


@pytest.mark.slow
def test_zh_tokenizer_serialize_pkuseg_with_processors(zh_tokenizer_pkuseg):
    nlp = Chinese(
        meta={
            "tokenizer": {
                "config": {
                    "use_jieba": False,
                    "use_pkuseg": True,
                    "pkuseg_model": "medicine",
                }
            }
        }
    )
    zh_tokenizer_serialize(nlp.tokenizer)
