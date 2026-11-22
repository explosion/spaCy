import time

import pytest

from spacy.lang.pt.punctuation import TOKENIZER_INFIXES
from spacy.util import compile_infix_regex

pt_infix_finditer = compile_infix_regex(TOKENIZER_INFIXES).finditer


@pytest.mark.parametrize(
    "text",
    [
        "português-luso",
        "1234-5678",
    ],
)
def test_pt_infixes_match(text):
    assert pt_infix_finditer(text)


@pytest.mark.parametrize(
    "text",
    [
        "a" * 60000,
        "1" * 60000,
    ],
    ids=["latin-run", "digit-run"],
)
def test_pt_infixes_are_linear_time(text):
    # unbounded \w+-\w+ was quadratic
    start = time.perf_counter()
    list(pt_infix_finditer(text))
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0
