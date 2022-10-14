import sys
import spacy


def test_get_byte_arrays_for_search_chars_width_1_not_case_sensitive():
    (
        w1_search,
        w1_finding,
        w2_search,
        w2_finding,
        w4_search,
        w4_finding,
    ) = spacy.util.get_byte_arrays_for_search_chars("bfEWfwe", False)
    assert w1_search == b"BEFWbefw"
    assert w2_search == b"B\x00E\x00F\x00W\x00b\x00e\x00f\x00w\x00"
    assert (
        w4_search
        == b"B\x00\x00\x00E\x00\x00\x00F\x00\x00\x00W\x00\x00\x00b\x00\x00\x00e\x00\x00\x00f\x00\x00\x00w\x00\x00\x00"
    )
    assert w1_finding == w2_finding == w4_finding == w4_search.lower()


def test_get_byte_arrays_for_search_chars_width_1_case_sensitive():
    (
        w1_search,
        w1_finding,
        w2_search,
        w2_finding,
        w4_search,
        w4_finding,
    ) = spacy.util.get_byte_arrays_for_search_chars("bfewT", True)
    assert w1_search == b"Tbefw"
    assert w2_search == b"T\x00b\x00e\x00f\x00w\00"
    assert w4_search == b"T\x00\00\00b\x00\00\00e\x00\00\00f\x00\00\00w\00\00\00"
    assert w1_finding == w2_finding == w4_finding == w4_search


def test_get_byte_arrays_for_search_chars_width_2_not_case_sensitive():
    (
        w1_search,
        w1_finding,
        w2_search,
        w2_finding,
        w4_search,
        w4_finding,
    ) = spacy.util.get_byte_arrays_for_search_chars("bféwfw", False)
    assert w1_search == b"BFWbfw"
    assert (
        w1_finding
        == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00"
    )
    assert w2_search == b"B\x00F\x00W\x00b\x00f\x00w\x00\xc9\x00\xe9\x00"
    assert (
        w2_finding
        == w4_finding
        == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xe9\x00\x00\x00\xe9\x00\x00\x00"
    )
    assert (
        w4_search
        == b"B\x00\x00\x00F\x00\x00\x00W\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xc9\x00\x00\x00\xe9\x00\x00\x00"
    )


def test_get_byte_arrays_for_search_chars_width_2_case_sensitive():
    (
        w1_search,
        w1_finding,
        w2_search,
        w2_finding,
        w4_search,
        w4_finding,
    ) = spacy.util.get_byte_arrays_for_search_chars("bféwfw", True)
    assert w1_search == b"bfw"
    assert w1_finding == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00"
    assert w2_search == b"b\x00f\x00w\x00\xe9\x00"
    assert (
        w2_finding
        == w4_finding
        == w4_search
        == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xe9\x00\x00\x00"
    )


def test_get_byte_arrays_for_search_chars_width_4_not_case_sensitive():
    (
        w1_search,
        w1_finding,
        w2_search,
        w2_finding,
        w4_search,
        w4_finding,
    ) = spacy.util.get_byte_arrays_for_search_chars("bfé𐌞wf𐌞wÉ", False)
    assert w1_search == b"BFWbfw"
    assert (
        w1_finding
        == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00"
    )

    assert w2_search == b"B\x00F\x00W\x00b\x00f\x00w\x00\xc9\x00\xe9\x00"

    assert (
        w2_finding
        == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xe9\x00\x00\x00\xe9\x00\x00\x00"
    )

    assert (
        w4_search
        == b"\x1e\x03\x01\x00B\x00\x00\x00F\x00\x00\x00W\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xc9\x00\x00\x00\xe9\x00\x00\x00"
    )

    assert (
        w4_finding
        == b"\x1e\x03\x01\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xe9\x00\x00\x00\xe9\x00\x00\x00"
    )


def test_get_byte_arrays_for_search_chars_width_4_case_sensitive():
    (
        w1_search,
        w1_finding,
        w2_search,
        w2_finding,
        w4_search,
        w4_finding,
    ) = spacy.util.get_byte_arrays_for_search_chars("bfé𐌞wf𐌞wÉ", True)
    assert w1_search == b"bfw"
    assert w1_finding == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00"
    assert w2_search == b"b\x00f\x00w\x00\xc9\x00\xe9\x00"
    assert (
        w2_finding
        == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xc9\x00\x00\x00\xe9\x00\x00\x00"
    )

    assert w4_search == w4_finding
    assert (
        w4_finding
        == b"\x1e\x03\x01\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xc9\x00\x00\x00\xe9\x00\x00\x00"
    )
