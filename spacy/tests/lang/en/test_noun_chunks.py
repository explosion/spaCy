import numpy
from spacy.attrs import HEAD, DEP
from spacy.symbols import nsubj, dobj, amod, nmod, conj, cc, root
from spacy.lang.en.syntax_iterators import noun_chunks
from spacy.tokens import Doc
import pytest


def test_noun_chunks_is_parsed(en_tokenizer):
    """Test that noun_chunks raises Value Error for 'en' language if Doc is not parsed."""
    doc = en_tokenizer("This is a sentence")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)


def test_en_noun_chunks_not_nested(en_vocab):
    words = ["Peter", "has", "chronic", "command", "and", "control", "issues"]
    heads = [1, 1, 6, 6, 3, 3, 1]
    deps = ["nsubj", "ROOT", "amod", "nmod", "cc", "conj", "dobj"]
    doc = Doc(en_vocab, words=words, heads=heads, deps=deps)
    doc.from_array(
        [HEAD, DEP],
        numpy.asarray(
            [
                [1, nsubj],
                [0, root],
                [4, amod],
                [3, nmod],
                [-1, cc],
                [-2, conj],
                [-5, dobj],
            ],
            dtype="uint64",
        ),
    )
    doc.noun_chunks_iterator = noun_chunks
    word_occurred = {}
    for chunk in doc.noun_chunks:
        for word in chunk:
            word_occurred.setdefault(word.text, 0)
            word_occurred[word.text] += 1
    for word, freq in word_occurred.items():
        assert freq == 1, (word, [chunk.text for chunk in doc.noun_chunks])
