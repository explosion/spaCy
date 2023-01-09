from typing import List

import numpy
import pytest
from numpy.testing import assert_almost_equal
from spacy.vocab import Vocab
from thinc.api import Model, data_validation, get_current_ops
from thinc.types import Array2d, Ragged

from spacy.lang.en import English
from spacy.ml import FeatureExtractor, StaticVectors
from spacy.ml._character_embed import CharacterEmbed
from spacy.tokens import Doc


OPS = get_current_ops()

texts = ["These are 4 words", "Here just three"]
l0 = [[1, 2], [3, 4], [5, 6], [7, 8]]
l1 = [[9, 8], [7, 6], [5, 4]]
list_floats = [OPS.xp.asarray(l0, dtype="f"), OPS.xp.asarray(l1, dtype="f")]
list_ints = [OPS.xp.asarray(l0, dtype="i"), OPS.xp.asarray(l1, dtype="i")]
array = OPS.xp.asarray(l1, dtype="f")
ragged = Ragged(array, OPS.xp.asarray([2, 1], dtype="i"))


def get_docs():
    vocab = Vocab()
    for t in texts:
        for word in t.split():
            hash_id = vocab.strings.add(word)
            vector = numpy.random.uniform(-1, 1, (7,))
            vocab.set_vector(hash_id, vector)
    docs = [English(vocab)(t) for t in texts]
    return docs


# Test components with a model of type Model[List[Doc], List[Floats2d]]
@pytest.mark.parametrize("name", ["tagger", "tok2vec", "morphologizer", "senter"])
def test_components_batching_list(name):
    nlp = English()
    proc = nlp.create_pipe(name)
    util_batch_unbatch_docs_list(proc.model, get_docs(), list_floats)


# Test components with a model of type Model[List[Doc], Floats2d]
@pytest.mark.parametrize("name", ["textcat"])
def test_components_batching_array(name):
    nlp = English()
    proc = nlp.create_pipe(name)
    util_batch_unbatch_docs_array(proc.model, get_docs(), array)


LAYERS = [
    (CharacterEmbed(nM=5, nC=3), get_docs(), list_floats),
    (FeatureExtractor([100, 200]), get_docs(), list_ints),
    (StaticVectors(), get_docs(), ragged),
]


@pytest.mark.parametrize("model,in_data,out_data", LAYERS)
def test_layers_batching_all(model, in_data, out_data):
    # In = List[Doc]
    if isinstance(in_data, list) and isinstance(in_data[0], Doc):
        if isinstance(out_data, OPS.xp.ndarray) and out_data.ndim == 2:
            util_batch_unbatch_docs_array(model, in_data, out_data)
        elif (
            isinstance(out_data, list)
            and isinstance(out_data[0], OPS.xp.ndarray)
            and out_data[0].ndim == 2
        ):
            util_batch_unbatch_docs_list(model, in_data, out_data)
        elif isinstance(out_data, Ragged):
            util_batch_unbatch_docs_ragged(model, in_data, out_data)


def util_batch_unbatch_docs_list(
    model: Model[List[Doc], List[Array2d]], in_data: List[Doc], out_data: List[Array2d]
):
    with data_validation(True):
        model.initialize(in_data, out_data)
        Y_batched = model.predict(in_data)
        Y_not_batched = [model.predict([u])[0] for u in in_data]
        for i in range(len(Y_batched)):
            assert_almost_equal(
                OPS.to_numpy(Y_batched[i]), OPS.to_numpy(Y_not_batched[i]), decimal=4
            )


def util_batch_unbatch_docs_array(
    model: Model[List[Doc], Array2d], in_data: List[Doc], out_data: Array2d
):
    with data_validation(True):
        model.initialize(in_data, out_data)
        Y_batched = model.predict(in_data).tolist()
        Y_not_batched = [model.predict([u])[0].tolist() for u in in_data]
        assert_almost_equal(Y_batched, Y_not_batched, decimal=4)


def util_batch_unbatch_docs_ragged(
    model: Model[List[Doc], Ragged], in_data: List[Doc], out_data: Ragged
):
    with data_validation(True):
        model.initialize(in_data, out_data)
        Y_batched = model.predict(in_data).data.tolist()
        Y_not_batched = []
        for u in in_data:
            Y_not_batched.extend(model.predict([u]).data.tolist())
        assert_almost_equal(Y_batched, Y_not_batched, decimal=4)
