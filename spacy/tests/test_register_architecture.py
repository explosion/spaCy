# coding: utf8
from __future__ import unicode_literals

import pytest
from spacy import register_architecture
from spacy import get_architecture
from thinc.v2v import Affine


@register_architecture("my_test_function")
def create_model(nr_in, nr_out):
    return Affine(nr_in, nr_out)


def test_get_architecture():
    arch = get_architecture("my_test_function")
    assert arch is create_model
    with pytest.raises(KeyError):
        get_architecture("not_an_existing_key")
