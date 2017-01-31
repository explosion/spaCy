# coding: utf-8
from __future__ import unicode_literals


def test_issue792(en_tokenizer):
  """Test for Issue #792: Trailing whitespace is removed after parsing."""
  text = "This is a string "
  doc = en_tokenizer(text)
  assert(doc.text_with_ws == text)

  text_unicode = "This is a string\u0020"
  doc_unicode = en_tokenizer(text_unicode)
  assert(doc_unicode.text_with_ws == text_unicode)
