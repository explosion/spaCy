import spacy


def test_get_byte_arrays_for_search_chars_width_2_not_case_sensitive():
    (
        search,
        ref,
    ) = spacy.util.get_byte_arrays_for_search_chars("bféwfw", False)
    assert (
        ref
        == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xe9\x00\x00\x00\xe9\x00\x00\x00"
    )

    assert (
        search
        == b"B\x00\x00\x00F\x00\x00\x00W\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xc9\x00\x00\x00\xe9\x00\x00\x00"
    )


def test_get_byte_arrays_for_search_chars_width_2_case_sensitive():
    (
        search,
        ref,
    ) = spacy.util.get_byte_arrays_for_search_chars("bféwfw", True)
    assert (
        ref == search == b"b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xe9\x00\x00\x00"
    )


def test_get_byte_arrays_for_search_chars_width_4_not_case_sensitive():
    (
        search,
        ref,
    ) = spacy.util.get_byte_arrays_for_search_chars("bfé𐌞wf𐌞wÉ", False)
    assert (
        search
        == b"\x1e\x03\x01\x00B\x00\x00\x00F\x00\x00\x00W\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xc9\x00\x00\x00\xe9\x00\x00\x00"
    )

    assert (
        ref
        == b"\x1e\x03\x01\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xe9\x00\x00\x00\xe9\x00\x00\x00"
    )


def test_get_byte_arrays_for_search_chars_width_4_case_sensitive():
    (
        search,
        ref,
    ) = spacy.util.get_byte_arrays_for_search_chars("bfé𐌞wf𐌞wÉ", True)
    assert search == ref
    assert (
        ref
        == b"\x1e\x03\x01\x00b\x00\x00\x00f\x00\x00\x00w\x00\x00\x00\xc9\x00\x00\x00\xe9\x00\x00\x00"
    )
