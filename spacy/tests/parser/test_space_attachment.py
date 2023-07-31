import pytest

from spacy.tokens import Doc

from ..util import apply_transition_sequence


def test_parser_space_attachment(en_vocab):
    # fmt: off
    words = ["This", "is", "a", "test", ".", "\n", "To", "ensure", " ", "spaces", "are", "attached", "well", "."]
    heads = [1, 1, 3, 1, 1, 4, 7, 11, 7, 11, 11, 11, 11, 11]
    # fmt: on
    deps = ["dep"] * len(heads)
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    for sent in doc.sents:
        if len(sent) == 1:
            assert not sent[-1].is_space


def test_parser_sentence_space(en_vocab):
    # fmt: off
    words = ["I", "look", "forward", "to", "using", "Thingamajig", ".", " ", "I", "'ve", "been", "told", "it", "will", "make", "my", "life", "easier", "..."]
    heads = [1, 1, 1, 1, 3, 4, 1, 6, 11, 11, 11, 11, 14, 14, 11, 16, 17, 14, 11]
    deps = ["nsubj", "ROOT", "advmod", "prep", "pcomp", "dobj", "punct", "",
            "nsubjpass", "aux", "auxpass", "ROOT", "nsubj", "aux", "ccomp",
            "poss", "nsubj", "ccomp", "punct"]
    # fmt: on
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    assert len(list(doc.sents)) == 2


@pytest.mark.skip(
    reason="The step_through API was removed (but should be brought back)"
)
def test_parser_space_attachment_leading(en_vocab, en_parser):
    words = ["\t", "\n", "This", "is", "a", "sentence", "."]
    heads = [1, 2, 2, 4, 2, 2]
    doc = Doc(en_vocab, words=words, heads=heads)
    assert doc[0].is_space
    assert doc[1].is_space
    assert doc[2].text == "This"
    with en_parser.step_through(doc) as stepwise:
        pass
    assert doc[0].head.i == 2
    assert doc[1].head.i == 2
    assert stepwise.stack == set([2])


@pytest.mark.skip(
    reason="The step_through API was removed (but should be brought back)"
)
def test_parser_space_attachment_intermediate_trailing(en_vocab, en_parser):
    words = ["This", "is", "\t", "a", "\t\n", "\n", "sentence", ".", "\n\n", "\n"]
    heads = [1, 1, 1, 5, 3, 1, 1, 6]
    transition = ["L-nsubj", "S", "L-det", "R-attr", "D", "R-punct"]
    doc = Doc(en_vocab, words=words, heads=heads)
    assert doc[2].is_space
    assert doc[4].is_space
    assert doc[5].is_space
    assert doc[8].is_space
    assert doc[9].is_space
    apply_transition_sequence(en_parser, doc, transition)
    for token in doc:
        assert token.dep != 0 or token.is_space
    assert [token.head.i for token in doc] == [1, 1, 1, 6, 3, 3, 1, 1, 7, 7]


@pytest.mark.parametrize("text,length", [(["\n"], 1), (["\n", "\t", "\n\n", "\t"], 4)])
@pytest.mark.skip(
    reason="The step_through API was removed (but should be brought back)"
)
def test_parser_space_attachment_space(en_parser, text, length):
    doc = Doc(en_parser.vocab, words=text)
    assert len(doc) == length
    with en_parser.step_through(doc) as _:  # noqa: F841
        pass
    assert doc[0].is_space
    for token in doc:
        assert token.head.i == length - 1
