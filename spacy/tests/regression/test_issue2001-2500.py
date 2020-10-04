import pytest
import numpy
from spacy.tokens import Doc
from spacy.matcher import Matcher
from spacy.displacy import render
from spacy.training import iob_to_biluo
from spacy.lang.it import Italian
from spacy.lang.en import English

from ..util import add_vecs_to_vocab


@pytest.mark.skip(
    reason="Can not be fixed without iterative looping between prefix/suffix and infix"
)
def test_issue2070():
    """Test that checks that a dot followed by a quote is handled
    appropriately.
    """
    # Problem: The dot is now properly split off, but the prefix/suffix rules
    # are not applied again afterwards. This means that the quote will still be
    # attached to the remaining token.
    nlp = English()
    doc = nlp('First sentence."A quoted sentence" he said ...')
    assert len(doc) == 11


def test_issue2179():
    """Test that spurious 'extra_labels' aren't created when initializing NER."""
    nlp = Italian()
    ner = nlp.add_pipe("ner")
    ner.add_label("CITIZENSHIP")
    nlp.initialize()
    nlp2 = Italian()
    nlp2.add_pipe("ner")
    assert len(nlp2.get_pipe("ner").labels) == 0
    model = nlp2.get_pipe("ner").model
    model.attrs["resize_output"](model, nlp.get_pipe("ner").moves.n_moves)
    nlp2.from_bytes(nlp.to_bytes())
    assert "extra_labels" not in nlp2.get_pipe("ner").cfg
    assert nlp2.get_pipe("ner").labels == ("CITIZENSHIP",)


def test_issue2203(en_vocab):
    """Test that lemmas are set correctly in doc.from_array."""
    words = ["I", "'ll", "survive"]
    tags = ["PRP", "MD", "VB"]
    lemmas = ["-PRON-", "will", "survive"]
    tag_ids = [en_vocab.strings.add(tag) for tag in tags]
    lemma_ids = [en_vocab.strings.add(lemma) for lemma in lemmas]
    doc = Doc(en_vocab, words=words)
    # Work around lemma corruption problem and set lemmas after tags
    doc.from_array("TAG", numpy.array(tag_ids, dtype="uint64"))
    doc.from_array("LEMMA", numpy.array(lemma_ids, dtype="uint64"))
    assert [t.tag_ for t in doc] == tags
    assert [t.lemma_ for t in doc] == lemmas
    # We need to serialize both tag and lemma, since this is what causes the bug
    doc_array = doc.to_array(["TAG", "LEMMA"])
    new_doc = Doc(doc.vocab, words=words).from_array(["TAG", "LEMMA"], doc_array)
    assert [t.tag_ for t in new_doc] == tags
    assert [t.lemma_ for t in new_doc] == lemmas


def test_issue2219(en_vocab):
    vectors = [("a", [1, 2, 3]), ("letter", [4, 5, 6])]
    add_vecs_to_vocab(en_vocab, vectors)
    [(word1, vec1), (word2, vec2)] = vectors
    doc = Doc(en_vocab, words=[word1, word2])
    assert doc[0].similarity(doc[1]) == doc[1].similarity(doc[0])


def test_issue2361(de_vocab):
    chars = ("&lt;", "&gt;", "&amp;", "&quot;")
    words = ["<", ">", "&", '"']
    doc = Doc(de_vocab, words=words, deps=["dep"] * len(words))
    html = render(doc)
    for char in chars:
        assert char in html


def test_issue2385():
    """Test that IOB tags are correctly converted to BILUO tags."""
    # fix bug in labels with a 'b' character
    tags1 = ("B-BRAWLER", "I-BRAWLER", "I-BRAWLER")
    assert iob_to_biluo(tags1) == ["B-BRAWLER", "I-BRAWLER", "L-BRAWLER"]
    # maintain support for iob1 format
    tags2 = ("I-ORG", "I-ORG", "B-ORG")
    assert iob_to_biluo(tags2) == ["B-ORG", "L-ORG", "U-ORG"]
    # maintain support for iob2 format
    tags3 = ("B-PERSON", "I-PERSON", "B-PERSON")
    assert iob_to_biluo(tags3) == ["B-PERSON", "L-PERSON", "U-PERSON"]


@pytest.mark.parametrize(
    "tags",
    [
        ("B-ORG", "L-ORG"),
        ("B-PERSON", "I-PERSON", "L-PERSON"),
        ("U-BRAWLER", "U-BRAWLER"),
    ],
)
def test_issue2385_biluo(tags):
    """Test that BILUO-compatible tags aren't modified."""
    assert iob_to_biluo(tags) == list(tags)


def test_issue2396(en_vocab):
    words = ["She", "created", "a", "test", "for", "spacy"]
    heads = [1, 1, 3, 1, 3, 4]
    deps = ["dep"] * len(heads)
    matrix = numpy.array(
        [
            [0, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1],
            [1, 1, 2, 3, 3, 3],
            [1, 1, 3, 3, 3, 3],
            [1, 1, 3, 3, 4, 4],
            [1, 1, 3, 3, 4, 5],
        ],
        dtype=numpy.int32,
    )
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    span = doc[:]
    assert (doc.get_lca_matrix() == matrix).all()
    assert (span.get_lca_matrix() == matrix).all()


def test_issue2464(en_vocab):
    """Test problem with successive ?. This is the same bug, so putting it here."""
    matcher = Matcher(en_vocab)
    doc = Doc(en_vocab, words=["a", "b"])
    matcher.add("4", [[{"OP": "?"}, {"OP": "?"}]])
    matches = matcher(doc)
    assert len(matches) == 3


def test_issue2482():
    """Test we can serialize and deserialize a blank NER or parser model."""
    nlp = Italian()
    nlp.add_pipe("ner")
    b = nlp.to_bytes()
    Italian().from_bytes(b)
