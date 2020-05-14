from inspect import isclass

from spacy.errors import add_codes


@add_codes
class Errors(object):
    E001 = "error description"


def test_add_codes():
    assert Errors.E001 == "[E001] error description"
    assert isclass(Errors.__class__)
