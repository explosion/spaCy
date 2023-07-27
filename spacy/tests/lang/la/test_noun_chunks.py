import pytest

from spacy.tokens import Doc


def test_noun_chunks_is_parsed(la_tokenizer):
    """Test that noun_chunks raises Value Error for 'la' language if Doc is not parsed.
    To check this test, we're constructing a Doc
    with a new Vocab here and forcing is_parsed to 'False'
    to make sure the noun chunks don't run.
    """
    doc = la_tokenizer("Haec est sententia.")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


LA_NP_TEST_EXAMPLES = [
    (
        "Haec narrantur a poetis de Perseo.",
        ["DET", "VERB", "ADP", "NOUN", "ADP", "PROPN", "PUNCT"],
        ["nsubj:pass", "ROOT", "case", "obl", "case", "obl", "punct"],
        [1, 0, -1, -1, -3, -1, -5],
        ["poetis", "Perseo"],
    ),
    (
        "Perseus autem in sinu matris dormiebat.",
        ["NOUN", "ADV", "ADP", "NOUN", "NOUN", "VERB", "PUNCT"],
        ["nsubj", "discourse", "case", "obl", "nmod", "ROOT", "punct"],
        [5, 4, 3, -1, -1, 0, -1],
        ["Perseus", "sinu matris"],
    ),
]


@pytest.mark.parametrize(
    "text,pos,deps,heads,expected_noun_chunks", LA_NP_TEST_EXAMPLES
)
def test_la_noun_chunks(la_tokenizer, text, pos, deps, heads, expected_noun_chunks):
    tokens = la_tokenizer(text)

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
