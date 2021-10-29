import numpy
from spacy.tokens import Doc, DocBin
from spacy.attrs import DEP, POS, TAG
from spacy.lang.en import English
from spacy.language import Language
from spacy.lang.en.syntax_iterators import noun_chunks
from spacy.vocab import Vocab
import spacy
from thinc.api import get_current_ops
import pytest

from ...util import make_tempdir


def test_issue5048(en_vocab):
    words = ["This", "is", "a", "sentence"]
    pos_s = ["DET", "VERB", "DET", "NOUN"]
    spaces = [" ", " ", " ", ""]
    deps_s = ["dep", "adj", "nn", "atm"]
    tags_s = ["DT", "VBZ", "DT", "NN"]
    strings = en_vocab.strings
    for w in words:
        strings.add(w)
    deps = [strings.add(d) for d in deps_s]
    pos = [strings.add(p) for p in pos_s]
    tags = [strings.add(t) for t in tags_s]
    attrs = [POS, DEP, TAG]
    array = numpy.array(list(zip(pos, deps, tags)), dtype="uint64")
    doc = Doc(en_vocab, words=words, spaces=spaces)
    doc.from_array(attrs, array)
    v1 = [(token.text, token.pos_, token.tag_) for token in doc]
    doc2 = Doc(en_vocab, words=words, pos=pos_s, deps=deps_s, tags=tags_s)
    v2 = [(token.text, token.pos_, token.tag_) for token in doc2]
    assert v1 == v2


def test_issue5082():
    # Ensure the 'merge_entities' pipeline does something sensible for the vectors of the merged tokens
    nlp = English()
    vocab = nlp.vocab
    array1 = numpy.asarray([0.1, 0.5, 0.8], dtype=numpy.float32)
    array2 = numpy.asarray([-0.2, -0.6, -0.9], dtype=numpy.float32)
    array3 = numpy.asarray([0.3, -0.1, 0.7], dtype=numpy.float32)
    array4 = numpy.asarray([0.5, 0, 0.3], dtype=numpy.float32)
    array34 = numpy.asarray([0.4, -0.05, 0.5], dtype=numpy.float32)
    vocab.set_vector("I", array1)
    vocab.set_vector("like", array2)
    vocab.set_vector("David", array3)
    vocab.set_vector("Bowie", array4)
    text = "I like David Bowie"
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "david"}, {"LOWER": "bowie"}]}
    ]
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns(patterns)
    parsed_vectors_1 = [t.vector for t in nlp(text)]
    assert len(parsed_vectors_1) == 4
    ops = get_current_ops()
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_1[0]), array1)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_1[1]), array2)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_1[2]), array3)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_1[3]), array4)
    nlp.add_pipe("merge_entities")
    parsed_vectors_2 = [t.vector for t in nlp(text)]
    assert len(parsed_vectors_2) == 3
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_2[0]), array1)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_2[1]), array2)
    numpy.testing.assert_array_equal(ops.to_numpy(parsed_vectors_2[2]), array34)


def test_issue5137():
    factory_name = "test_issue5137"
    pipe_name = "my_component"

    @Language.factory(factory_name)
    class MyComponent:
        def __init__(self, nlp, name=pipe_name, categories="all_categories"):
            self.nlp = nlp
            self.categories = categories
            self.name = name

        def __call__(self, doc):
            pass

        def to_disk(self, path, **kwargs):
            pass

        def from_disk(self, path, **cfg):
            pass

    nlp = English()
    my_component = nlp.add_pipe(factory_name, name=pipe_name)
    assert my_component.categories == "all_categories"
    with make_tempdir() as tmpdir:
        nlp.to_disk(tmpdir)
        overrides = {"components": {pipe_name: {"categories": "my_categories"}}}
        nlp2 = spacy.load(tmpdir, config=overrides)
        assert nlp2.get_pipe(pipe_name).categories == "my_categories"


def test_issue5141(en_vocab):
    """Ensure an empty DocBin does not crash on serialization"""
    doc_bin = DocBin(attrs=["DEP", "HEAD"])
    assert list(doc_bin.get_docs(en_vocab)) == []
    doc_bin_bytes = doc_bin.to_bytes()
    doc_bin_2 = DocBin().from_bytes(doc_bin_bytes)
    assert list(doc_bin_2.get_docs(en_vocab)) == []


def test_issue5152():
    # Test that the comparison between a Span and a Token, goes well
    # There was a bug when the number of tokens in the span equaled the number of characters in the token (!)
    nlp = English()
    text = nlp("Talk about being boring!")
    text_var = nlp("Talk of being boring!")
    y = nlp("Let")
    span = text[0:3]  # Talk about being
    span_2 = text[0:3]  # Talk about being
    span_3 = text_var[0:3]  # Talk of being
    token = y[0]  # Let
    with pytest.warns(UserWarning):
        assert span.similarity(token) == 0.0
    assert span.similarity(span_2) == 1.0
    with pytest.warns(UserWarning):
        assert span_2.similarity(span_3) < 1.0


def test_issue5458():
    # Test that the noun chuncker does not generate overlapping spans
    # fmt: off
    words = ["In", "an", "era", "where", "markets", "have", "brought", "prosperity", "and", "empowerment", "."]
    vocab = Vocab(strings=words)
    deps = ["ROOT", "det", "pobj", "advmod", "nsubj", "aux", "relcl", "dobj", "cc", "conj", "punct"]
    pos = ["ADP", "DET", "NOUN", "ADV", "NOUN", "AUX", "VERB", "NOUN", "CCONJ", "NOUN", "PUNCT"]
    heads = [0, 2, 0, 9, 6, 6, 2, 6, 7, 7, 0]
    # fmt: on
    en_doc = Doc(vocab, words=words, pos=pos, heads=heads, deps=deps)
    en_doc.noun_chunks_iterator = noun_chunks

    # if there are overlapping spans, this will fail with an E102 error "Can't merge non-disjoint spans"
    nlp = English()
    merge_nps = nlp.create_pipe("merge_noun_chunks")
    merge_nps(en_doc)
