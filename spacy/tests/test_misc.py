# coding: utf-8
from __future__ import unicode_literals

from ..util import ensure_path
from ..util import model_to_bytes, model_from_bytes

from pathlib import Path
import pytest
from thinc.neural import Maxout, Softmax
from thinc.api import chain


@pytest.mark.parametrize('text', ['hello/world', 'hello world'])
def test_util_ensure_path_succeeds(text):
    path = ensure_path(text)
    assert isinstance(path, Path)


def test_simple_model_roundtrip_bytes():
    model = Maxout(5, 10, pieces=2)
    model.b += 1
    data = model_to_bytes(model)
    model.b -= 1
    model_from_bytes(model, data)
    assert model.b[0, 0] == 1


def test_multi_model_roundtrip_bytes():
    model = chain(Maxout(5, 10, pieces=2), Maxout(2, 3))
    model._layers[0].b += 1
    model._layers[1].b += 2
    data = model_to_bytes(model)
    model._layers[0].b -= 1
    model._layers[1].b -= 2
    model_from_bytes(model, data)
    assert model._layers[0].b[0, 0] == 1
    assert model._layers[1].b[0, 0] == 2


def test_multi_model_load_missing_dims():
    model = chain(Maxout(5, 10, pieces=2), Maxout(2, 3))
    model._layers[0].b += 1
    model._layers[1].b += 2
    data = model_to_bytes(model)

    model2 = chain(Maxout(5), Maxout())
    model_from_bytes(model2, data)
    assert model2._layers[0].b[0, 0] == 1
    assert model2._layers[1].b[0, 0] == 2
