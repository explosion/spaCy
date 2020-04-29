# coding: utf8
from __future__ import unicode_literals

import numpy as np
from spacy.lang.en import English
from spacy.pipeline import EntityRuler


def test_issue5082():
    # Ensure the 'merge_entities' pipeline does something sensible for the vectors of the merged tokens
    nlp = English()
    vocab = nlp.vocab
    array1 = np.asarray([0.1, 0.5, 0.8], dtype=np.float32)
    array2 = np.asarray([-0.2, -0.6, -0.9], dtype=np.float32)
    array3 = np.asarray([0.3, -0.1, 0.7], dtype=np.float32)
    array4 = np.asarray([0.5, 0, 0.3], dtype=np.float32)
    array34 = np.asarray([0.4, -0.05, 0.5], dtype=np.float32)

    vocab.set_vector("I", array1)
    vocab.set_vector("like", array2)
    vocab.set_vector("David", array3)
    vocab.set_vector("Bowie", array4)

    text = "I like David Bowie"
    ruler = EntityRuler(nlp)
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "david"}, {"LOWER": "bowie"}]}
    ]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)

    parsed_vectors_1 = [t.vector for t in nlp(text)]
    assert len(parsed_vectors_1) == 4
    np.testing.assert_array_equal(parsed_vectors_1[0], array1)
    np.testing.assert_array_equal(parsed_vectors_1[1], array2)
    np.testing.assert_array_equal(parsed_vectors_1[2], array3)
    np.testing.assert_array_equal(parsed_vectors_1[3], array4)

    merge_ents = nlp.create_pipe("merge_entities")
    nlp.add_pipe(merge_ents)

    parsed_vectors_2 = [t.vector for t in nlp(text)]
    assert len(parsed_vectors_2) == 3
    np.testing.assert_array_equal(parsed_vectors_2[0], array1)
    np.testing.assert_array_equal(parsed_vectors_2[1], array2)
    np.testing.assert_array_equal(parsed_vectors_2[2], array34)
