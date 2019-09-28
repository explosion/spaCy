# coding: utf-8
from __future__ import unicode_literals

import pytest


@pytest.mark.parametrize(
    "text,norms",
    [("пн.", ["понедельник"]), ("пт.", ["пятница"]), ("дек.", ["декабрь"])],
)
def test_ru_tokenizer_abbrev_exceptions(ru_tokenizer, text, norms):
    tokens = ru_tokenizer(text)
    assert len(tokens) == 1
    assert [token.norm_ for token in tokens] == norms
