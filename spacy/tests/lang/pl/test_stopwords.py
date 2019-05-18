# coding: utf8
from __future__ import unicode_literals

import pytest

STOPWORD_TESTS = [
    ("Ten, który z demonami walczy, winien uważać, by samemu nie stać się jednym z nich.",
     [True, False, True, True, False, False, False, False, False,
      False, True, False, True, False, True, True, True, True, False]),

    ("Kiedy spoglądasz w otchłań ona również patrzy na ciebie.",
     [True, False, True, False, True, True, False, True, True, False]),

    ("Nie masz żadnej szansy, ale ją wykorzystaj.",
     [True, False, False, False, False, True, True, False, False]),

    ("Pamiętajcie, by patrzeć w gwiazdy, a nie pod swoje nogi.",
     [False, False, True, False, True, False, False, True, True, True, True, False, False])
]

TESTCASES = STOPWORD_TESTS


@pytest.mark.parametrize('text,expected_tokens', TESTCASES)
def test_tokenizer_handles_testcases(pl_tokenizer, text, expected_tokens):
    tokens = pl_tokenizer(text)
    token_list = [token.is_stop for token in tokens if not token.is_space]
    assert expected_tokens == token_list
