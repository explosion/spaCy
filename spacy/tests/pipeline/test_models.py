from typing import List
import pytest
from numpy.testing import assert_equal
from thinc.api import get_current_ops, Model, data_validation
from thinc.types import Array2d

from spacy.lang.en import English
from spacy.tokens import Doc

OPS = get_current_ops()

texts = ["These are 4 words", "These just three"]
l0 = [[1, 2], [3, 4], [5, 6], [7, 8]]
l1 = [[9, 8], [7, 6], [5, 4]]
out_list = [OPS.xp.asarray(l0, dtype="f"), OPS.xp.asarray(l1, dtype="f")]
a1 = OPS.xp.asarray(l1, dtype="f")

# Test components with a model of type Model[List[Doc], List[Floats2d]]
@pytest.mark.parametrize("name", ["tagger", "tok2vec", "morphologizer", "senter"])
def test_layers_batching_all_list(name):
    nlp = English()
    in_data = [nlp(text) for text in texts]
    proc = nlp.create_pipe(name)
    util_batch_unbatch_List(proc.model, in_data, out_list)

def util_batch_unbatch_List(model: Model[List[Doc], List[Array2d]], in_data: List[Doc], out_data: List[Array2d]):
    with data_validation(True):
        model.initialize(in_data, out_data)
        Y_batched = model.predict(in_data)
        Y_not_batched = [model.predict([u])[0] for u in in_data]
        assert_equal(Y_batched, Y_not_batched)

# Test components with a model of type Model[List[Doc], Floats2d]
@pytest.mark.parametrize("name", ["textcat"])
def test_layers_batching_all_array(name):
    nlp = English()
    in_data = [nlp(text) for text in texts]
    proc = nlp.create_pipe(name)
    util_batch_unbatch_Array(proc.model, in_data, a1)

def util_batch_unbatch_Array(model: Model[List[Doc], Array2d], in_data: List[Doc], out_data: Array2d):
    with data_validation(True):
        model.initialize(in_data, out_data)
        Y_batched = model.predict(in_data)
        Y_not_batched = [model.predict([u])[0] for u in in_data]
        assert_equal(Y_batched, Y_not_batched)