import spacy
import pytest


@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_search_char_byte_arrays_1_width_only(case_sensitive):
    sc1, sc2, sc3, sc4 = spacy.util.get_search_char_byte_arrays("zzaaEP", case_sensitive)
    if case_sensitive:
        assert sc1 == b"EPaz" 
    else:
        assert sc1 == b"aepz"
    assert sc2 == b""
    assert sc3 == b""
    assert sc4 == b""

@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_search_char_byte_arrays_4_width_only(case_sensitive):
    sc1, sc2, sc3, sc4 = spacy.util.get_search_char_byte_arrays("𐌞", case_sensitive)
    assert sc1 == b""
    assert sc2 == b""
    assert sc3 == b""
    assert sc4 == "𐌞".encode("utf-8")

@pytest.mark.parametrize("case_sensitive", [True, False])
def test_get_search_char_byte_arrays_all_widths(case_sensitive):
    sc1, sc2, sc3, sc4 = spacy.util.get_search_char_byte_arrays("𐌞Éabé—B𐌞", case_sensitive)
    if case_sensitive:
        assert sc1 == b"Bab"
        assert sc2 == "Éé".encode("utf-8")
    else:
        assert sc1 == b"ab"
        assert sc2 == "é".encode("utf-8")
    assert sc3 == "—".encode("utf-8")
    assert sc4 == "𐌞".encode("utf-8")

@pytest.mark.parametrize("case_sensitive", [True, False])
def test_turkish_i_with_dot(case_sensitive):
    sc1, sc2, sc3, sc4 = spacy.util.get_search_char_byte_arrays("İ", case_sensitive)
    if case_sensitive:
        assert sc2 == "İ".encode("utf-8")
        assert sc1 == sc3 == sc4 == b""
    else:
        assert sc1 == b"i"
        assert sc2 == b"\xcc\x87"
        assert sc3 == sc4 == b""

@pytest.mark.parametrize("case_sensitive", [True, False])
def test_turkish_i_with_dot_and_normal_i(case_sensitive):
    sc1, sc2, sc3, sc4 = spacy.util.get_search_char_byte_arrays("İI", case_sensitive)
    if case_sensitive:
        assert sc1 == b"I"
        assert sc2 == "İ".encode("utf-8")
        assert sc3 == sc4 == b""
    else:
        assert sc1 == b"i"
        assert sc2 == b"\xcc\x87"
        assert sc3 == sc4 == b""