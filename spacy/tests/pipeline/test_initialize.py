import pytest
from spacy.language import Language
from spacy.lang.en import English
from spacy.training import Example
from thinc.api import ConfigValidationError
from pydantic import StrictBool


def test_initialize_arguments():
    name = "test_initialize_arguments"

    class Component:
        def __init__(self):
            ...

        def initialize(
            self, get_examples, nlp, custom1: str, custom2: StrictBool = False
        ):
            ...

    Language.factory(name, func=lambda nlp, name: Component())

    nlp = English()
    example = Example.from_dict(nlp("x"), {})
    get_examples = lambda: [example]
    nlp.add_pipe(name)
    # The settings here will typically come from the [initialize] block
    with pytest.raises(ConfigValidationError) as e:
        # Empty settings, no required custom1 argument
        nlp.initialize(get_examples, settings={"components": {name: {}}})
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0]["loc"] == ("custom1",)
    assert errors[0]["type"] == "value_error.missing"
    with pytest.raises(ConfigValidationError) as e:
        # Wrong type
        settings = {"components": {name: {"custom1": "x", "custom2": 1}}}
        nlp.initialize(get_examples, settings=settings)
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0]["loc"] == ("custom2",)
    assert errors[0]["type"] == "value_error.strictbool"
