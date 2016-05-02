import numpy as np

from spacy.attrs import HEAD, DEP
from spacy.symbols import nsubj, dobj, punct, amod, nmod, conj, cc, root
from spacy.en import English
from spacy.syntax.iterators import english_noun_chunks


def test_not_nested():
    nlp = English(parser=False, entity=False)
    sent = u'''Peter has chronic command and control issues'''.strip()
    tokens = nlp(sent)
    tokens.from_array(
        [HEAD, DEP],
        np.asarray(
            [
                [1, nsubj],
                [0, root],
                [4, amod],
                [3, nmod],
                [-1, cc],
                [-2, conj],
                [-5, dobj]
            ], dtype='int32'))
    tokens.noun_chunks_iterator = english_noun_chunks
    word_occurred = {}
    for chunk in tokens.noun_chunks:
        for word in chunk:
            word_occurred.setdefault(word.text, 0)
            word_occurred[word.text] += 1
    for word, freq in word_occurred.items():
        assert freq == 1, (word, [chunk.text for chunk in tokens.noun_chunks])

