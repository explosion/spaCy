import pytest

from spacy.tokens import Doc

from ...util import apply_transition_sequence


@pytest.mark.issue(309)
def test_issue309(en_vocab):
    """Test Issue #309: SBD fails on empty string"""
    doc = Doc(en_vocab, words=[" "], heads=[0], deps=["ROOT"])
    assert len(doc) == 1
    sents = list(doc.sents)
    assert len(sents) == 1


@pytest.mark.parametrize("words", [["A", "test", "sentence"]])
@pytest.mark.parametrize("punct", [".", "!", "?", ""])
def test_en_sbd_single_punct(en_vocab, words, punct):
    heads = [2, 2, 2, 2] if punct else [2, 2, 2]
    deps = ["dep"] * len(heads)
    words = [*words, punct] if punct else words
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    assert len(doc) == 4 if punct else 3
    assert len(list(doc.sents)) == 1
    assert sum(len(sent) for sent in doc.sents) == len(doc)


@pytest.mark.skip(
    reason="The step_through API was removed (but should be brought back)"
)
def test_en_sentence_breaks(en_vocab, en_parser):
    # fmt: off
    words = ["This", "is", "a", "sentence", ".", "This", "is", "another", "one", "."]
    heads = [1, 1, 3, 1, 1, 6, 6, 8, 6, 6]
    deps = ["nsubj", "ROOT", "det", "attr", "punct", "nsubj", "ROOT", "det",
            "attr", "punct"]
    transition = ["L-nsubj", "S", "L-det", "R-attr", "D", "R-punct", "B-ROOT",
                  "L-nsubj", "S", "L-attr", "R-attr", "D", "R-punct"]
    # fmt: on
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    apply_transition_sequence(en_parser, doc, transition)
    assert len(list(doc.sents)) == 2
    for token in doc:
        assert token.dep != 0 or token.is_space
    assert [token.head.i for token in doc] == [1, 1, 3, 1, 1, 6, 6, 8, 6, 6]
