import spacy
import pytest


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_search_char_byte_arrays_1_width_only(case_sensitive):
    search_chars, width_offsets = spacy.util.get_search_char_byte_arrays(
        "zzaaEP", case_sensitive
    )
    if case_sensitive:
        assert search_chars == b"EPaz"
    else:
        assert search_chars == b"aepz"
    assert width_offsets == b"\x00\x04\x04\x04\x04"


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_search_char_byte_arrays_4_width_only(case_sensitive):
    search_chars, width_offsets = spacy.util.get_search_char_byte_arrays(
        "𐌞", case_sensitive
    )
    assert search_chars == "𐌞".encode("utf-8")
    assert width_offsets == b"\x00\x00\x00\x00\x04"


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_search_char_byte_arrays_all_widths(case_sensitive):
    search_chars, width_offsets = spacy.util.get_search_char_byte_arrays(
        "𐌞Éabé—B𐌞", case_sensitive
    )
    if case_sensitive:
        assert search_chars == "BabÉé—𐌞".encode("utf-8")
        assert width_offsets == b"\x00\x03\x07\x0a\x0e"
    else:
        assert search_chars == "abé—𐌞".encode("utf-8")
        assert width_offsets == b"\x00\x02\x04\x07\x0b"


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_search_char_byte_arrays_widths_1_and_3(case_sensitive):
    search_chars, width_offsets = spacy.util.get_search_char_byte_arrays(
        "B—", case_sensitive
    )
    if case_sensitive:
        assert search_chars == "B—".encode("utf-8")
    else:
        assert search_chars == "b—".encode("utf-8")
    assert width_offsets == b"\x00\x01\x01\x04\x04"


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_search_char_byte_arrays_widths_1_and_4(case_sensitive):
    search_chars, width_offsets = spacy.util.get_search_char_byte_arrays(
        "B𐌞", case_sensitive
    )
    if case_sensitive:
        assert search_chars == "B𐌞".encode("utf-8")
    else:
        assert search_chars == "b𐌞".encode("utf-8")
    assert width_offsets == b"\x00\x01\x01\x01\x05"


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_turkish_i_with_dot(case_sensitive):
    search_chars, width_offsets = spacy.util.get_search_char_byte_arrays(
        "İ", case_sensitive
    )
    if case_sensitive:
        assert search_chars == "İ".encode("utf-8")
        assert width_offsets == b"\x00\x00\x02\x02\x02"
    else:
        assert search_chars == b"i\xcc\x87"
        assert width_offsets == b"\x00\x01\x03\x03\x03"


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_turkish_i_with_dot_and_normal_i(case_sensitive):
    search_chars, width_offsets = spacy.util.get_search_char_byte_arrays(
        "İI", case_sensitive
    )
    if case_sensitive:
        assert search_chars == "Iİ".encode("utf-8")
        assert width_offsets == b"\x00\x01\x03\x03\x03"
    else:
        assert search_chars == b"i\xcc\x87"
        assert width_offsets == b"\x00\x01\x03\x03\x03"
