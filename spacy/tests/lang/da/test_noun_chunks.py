import pytest

from spacy.tokens import Doc


def test_noun_chunks_is_parsed(da_tokenizer):
    """Test that noun_chunks raises Value Error for 'da' language if Doc is not parsed.
    To check this test, we're constructing a Doc
    with a new Vocab here and forcing is_parsed to 'False'
    to make sure the noun chunks don't run.
    """
    doc = da_tokenizer("Det er en sætning")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


DA_NP_TEST_EXAMPLES = [
    (
        "Hun elsker at plukker frugt.",
        ["PRON", "VERB", "PART", "VERB", "NOUN", "PUNCT"],
        ["nsubj", "ROOT", "mark", "obj", "obj", "punct"],
        [1, 0, 1, -2, -1, -4],
        ["Hun", "frugt"],
    ),
    (
        "Påfugle er de smukkeste fugle.",
        ["NOUN", "AUX", "DET", "ADJ", "NOUN", "PUNCT"],
        ["nsubj", "cop", "det", "amod", "ROOT", "punct"],
        [4, 3, 2, 1, 0, -1],
        ["Påfugle", "de smukkeste fugle"],
    ),
    (
        "Rikke og Jacob Jensen glæder sig til en hyggelig skovtur",
        [
            "PROPN",
            "CCONJ",
            "PROPN",
            "PROPN",
            "VERB",
            "PRON",
            "ADP",
            "DET",
            "ADJ",
            "NOUN",
        ],
        ["nsubj", "cc", "conj", "flat", "ROOT", "obj", "case", "det", "amod", "obl"],
        [4, 1, -2, -1, 0, -1, 3, 2, 1, -5],
        ["Rikke", "Jacob Jensen", "sig", "en hyggelig skovtur"],
    ),
]


@pytest.mark.parametrize(
    "text,pos,deps,heads,expected_noun_chunks", DA_NP_TEST_EXAMPLES
)
def test_da_noun_chunks(da_tokenizer, text, pos, deps, heads, expected_noun_chunks):
    tokens = da_tokenizer(text)

    assert len(heads) == len(pos)
    doc = Doc(
        tokens.vocab,
        words=[t.text for t in tokens],
        heads=[head + i for i, head in enumerate(heads)],
        deps=deps,
        pos=pos,
    )

    noun_chunks = list(doc.noun_chunks)
    assert len(noun_chunks) == len(expected_noun_chunks)
    for i, np in enumerate(noun_chunks):
        assert np.text == expected_noun_chunks[i]
