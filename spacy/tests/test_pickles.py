import numpy
import pytest
import srsly

from spacy.attrs import NORM
from spacy.lang.en import English
from spacy.strings import StringStore
from spacy.tokens import Doc
from spacy.vocab import Vocab


@pytest.mark.parametrize("text1,text2", [("hello", "bye")])
def test_pickle_string_store(text1, text2):
    stringstore = StringStore()
    store1 = stringstore[text1]
    store2 = stringstore[text2]
    data = srsly.pickle_dumps(stringstore, protocol=-1)
    unpickled = srsly.pickle_loads(data)
    assert unpickled[text1] == store1
    assert unpickled[text2] == store2
    assert len(stringstore) == len(unpickled)


@pytest.mark.parametrize("text1,text2", [("dog", "cat")])
def test_pickle_vocab(text1, text2):
    vocab = Vocab(
        lex_attr_getters={int(NORM): lambda string: string[:-1]},
        get_noun_chunks=English.Defaults.syntax_iterators.get("noun_chunks"),
    )
    vocab.set_vector("dog", numpy.ones((5,), dtype="f"))
    lex1 = vocab[text1]
    lex2 = vocab[text2]
    assert lex1.norm_ == text1[:-1]
    assert lex2.norm_ == text2[:-1]
    data = srsly.pickle_dumps(vocab)
    unpickled = srsly.pickle_loads(data)
    assert unpickled[text1].orth == lex1.orth
    assert unpickled[text2].orth == lex2.orth
    assert unpickled[text1].norm == lex1.norm
    assert unpickled[text2].norm == lex2.norm
    assert unpickled[text1].norm != unpickled[text2].norm
    assert unpickled.vectors is not None
    assert unpickled.get_noun_chunks is not None
    assert list(vocab["dog"].vector) == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_pickle_doc(en_vocab):
    words = ["a", "b", "c"]
    deps = ["dep"] * len(words)
    heads = [0] * len(words)
    doc = Doc(
        en_vocab,
        words=words,
        deps=deps,
        heads=heads,
    )
    data = srsly.pickle_dumps(doc)
    unpickled = srsly.pickle_loads(data)
    assert [t.text for t in unpickled] == words
    assert [t.dep_ for t in unpickled] == deps
    assert [t.head.i for t in unpickled] == heads
    assert list(doc.noun_chunks) == []
