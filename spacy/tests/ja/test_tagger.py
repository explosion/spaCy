# coding: utf-8
from __future__ import unicode_literals

import pytest

TAGGER_TESTS = [
    ('あれならそこにあるよ', 
      (('代名詞,*,*,*', 'PRON'),
      ('助動詞,*,*,*', 'AUX'),
      ('代名詞,*,*,*', 'PRON'),
      ('助詞,格助詞,*,*', 'ADP'),
      ('動詞,非自立可能,*,*', 'VERB'),
      ('助詞,終助詞,*,*', 'PART'))),
    ('このファイルには小さなテストが入っているよ', 
      (('連体詞,*,*,*,DET', 'DET'),
      ('名詞,普通名詞,サ変可能,*', 'NOUN'),
      ('助詞,格助詞,*,*', 'ADP'),
      ('助詞,係助詞,*,*', 'ADP'),
      ('連体詞,*,*,*,ADJ', 'ADJ'),
      ('名詞,普通名詞,サ変可能,*', 'NOUN'),
      ('助詞,格助詞,*,*', 'ADP'),
      ('動詞,一般,*,*', 'VERB'),
      ('助詞,接続助詞,*,*', 'SCONJ'),
      ('動詞,非自立可能,*,*', 'VERB'),
      ('助詞,終助詞,*,*', 'PART'))),
    ('プププランドに行きたい',
      (('名詞,普通名詞,一般,*', 'NOUN'),
      ('助詞,格助詞,*,*', 'ADP'),
      ('動詞,非自立可能,*,*', 'VERB'),
      ('助動詞,*,*,*', 'AUX')))
]

@pytest.mark.parametrize('text,expected_tags', TAGGER_TESTS)
def test_japanese_tagger(japanese, text, expected_tags):
    tokens = japanese.make_doc(text)
    assert len(tokens) == len(expected_tags)
    for token, res in zip(tokens, expected_tags):
        assert token.tag_ == res[0] and token.pos_ == res[1]
