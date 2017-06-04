# coding: utf-8
from __future__ import unicode_literals

from ...util import get_lang_class
from ..util import make_tempdir, assert_packed_msg_equal

import pytest


def load_tokenizer(b):
    tok = get_lang_class('en').Defaults.create_tokenizer()
    tok.from_bytes(b)
    return tok


@pytest.mark.xfail
@pytest.mark.parametrize('text', ["I💜you", "they’re", "“hello”"])
def test_serialize_tokenizer_roundtrip_bytes(en_tokenizer, text):
    tokenizer = en_tokenizer
    new_tokenizer = load_tokenizer(tokenizer.to_bytes())
    assert_packed_msg_equal(new_tokenizer.to_bytes(), tokenizer.to_bytes())
    # assert new_tokenizer.to_bytes() == tokenizer.to_bytes()
    doc1 = tokenizer(text)
    doc2 = new_tokenizer(text)
    assert [token.text for token in doc1] == [token.text for token in doc2]


@pytest.mark.xfail
def test_serialize_tokenizer_roundtrip_disk(en_tokenizer):
    tokenizer = en_tokenizer
    with make_tempdir() as d:
        file_path = d / 'tokenizer'
        tokenizer.to_disk(file_path)
        tokenizer_d = en_tokenizer.from_disk(file_path)
        assert tokenizer.to_bytes() == tokenizer_d.to_bytes()
