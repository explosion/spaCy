from inspect import isclass

import pytest

from spacy.errors import add_codes


@add_codes
class Errors(object):
    E001 = "error description"


def test_add_codes():
    assert Errors.E001 == "[E001] error description"
    with pytest.raises(AttributeError):
        Errors.E002
    assert isclass(Errors.__class__)
