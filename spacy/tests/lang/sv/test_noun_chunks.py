import pytest
from spacy.tokens import Doc


def test_noun_chunks_is_parsed_sv(sv_tokenizer):
    """Test that noun_chunks raises Value Error for 'sv' language if Doc is not parsed."""
    doc = sv_tokenizer("Studenten läste den bästa boken")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


SV_NP_TEST_EXAMPLES = [
    (
        "En student läste en bok",  # A student read a book
        ["DET", "NOUN", "VERB", "DET", "NOUN"],
        ["det", "nsubj", "ROOT", "det", "dobj"],
        [1, 2, 2, 4, 2],
        ["En student", "en bok"],
    ),
    (
        "Studenten läste den bästa boken.",  # The student read the best book
        ["NOUN", "VERB", "DET", "ADJ", "NOUN", "PUNCT"],
        ["nsubj", "ROOT", "det", "amod", "dobj", "punct"],
        [1, 1, 4, 4, 1, 1],
        ["Studenten", "den bästa boken"],
    ),
    (
        "De samvetslösa skurkarna hade stulit de största juvelerna på söndagen",  # The remorseless crooks had stolen the largest jewels that sunday
        ["DET", "ADJ", "NOUN", "VERB", "VERB", "DET", "ADJ", "NOUN", "ADP", "NOUN"],
        ["det", "amod", "nsubj", "aux", "root", "det", "amod", "dobj", "case", "nmod"],
        [2, 2, 4, 4, 4, 7, 7, 4, 9, 4],
        ["De samvetslösa skurkarna", "de största juvelerna", "på söndagen"],
    ),
]


@pytest.mark.parametrize(
    "text,pos,deps,heads,expected_noun_chunks", SV_NP_TEST_EXAMPLES
)
def test_sv_noun_chunks(sv_tokenizer, text, pos, deps, heads, expected_noun_chunks):
    tokens = sv_tokenizer(text)
    assert len(heads) == len(pos)
    words = [t.text for t in tokens]
    doc = Doc(tokens.vocab, words=words, heads=heads, deps=deps, pos=pos)
    noun_chunks = list(doc.noun_chunks)
    assert len(noun_chunks) == len(expected_noun_chunks)
    for i, np in enumerate(noun_chunks):
        assert np.text == expected_noun_chunks[i]
