import time

import pytest

from spacy.lang.el.punctuation import TOKENIZER_INFIXES, TOKENIZER_SUFFIXES
from spacy.util import compile_infix_regex, compile_suffix_regex

el_infix_finditer = compile_infix_regex(TOKENIZER_INFIXES).finditer
el_suffix_search = compile_suffix_regex(TOKENIZER_SUFFIXES).search


@pytest.mark.parametrize(
    "text",
    [
        "abc/def/ghi",
        "abc-abc",
        "abc@cde-fgh.a",
        "10.9-6",
        "10,11-12,13",
        "1ης-2",
        "15/2/17",
    ],
)
def test_el_infixes_match(text):
    assert el_infix_finditer(text)


@pytest.mark.parametrize(
    "text",
    [
        # digits never matched `[a-zA-Z]` in the name1/name2/name3 pattern
        "name1/name2/name3",
        # no "-" present for the digit-run infix
        "10,11,12",
    ],
)
def test_el_infixes_no_match(text):
    assert not list(el_infix_finditer(text))


@pytest.mark.parametrize(
    "text",
    [
        "12'",
        "12&",
        "13mg",
        "1.2m",
        "πρώτος-δεύτερος",
    ],
)
def test_el_suffixes_match(text):
    assert el_suffix_search(text)


@pytest.mark.parametrize(
    "text",
    [
        "a" * 20000,
        "1" * 20000,
        "a@" + "c" * 20000,
    ],
    ids=["latin-run", "digit-run", "at-then-run"],
)
def test_el_infixes_are_linear_time(text):
    # unbounded + was quadratic here
    start = time.perf_counter()
    list(el_infix_finditer(text))
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0


@pytest.mark.parametrize(
    "text",
    [
        "1" * 20000,
        "α" * 20000,
    ],
    ids=["digit-run", "greek-run"],
)
def test_el_suffixes_are_linear_time(text):
    start = time.perf_counter()
    el_suffix_search(text)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0
