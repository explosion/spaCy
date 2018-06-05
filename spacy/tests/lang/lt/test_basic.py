from __future__ import unicode_literals

import pytest

from spacy.lang.lt import LithuanianLanguage

util.set_lang_class('lt', LithuanianLanguage)
lang_class = util.get_lang_class('lt')
nlp = lang_class()

# Change to Lithuanian
@pytest.mark.parametrize('text,length', [
    ("The U.S. Army likes Shock and Awe.", 8),
    ("U.N. regulations are not a part of their concern.", 10),
    ("“Isn't it?”", 6)])
def test_en_tokenizer_handles_punct_abbrev(en_tokenizer, text, length):
    tokens = en_tokenizer(text)
    assert len(tokens) == length