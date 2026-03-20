import pytest

try:
    from pydantic.v1 import StrictBool
except ImportError:
    from pydantic import StrictBool  # type: ignore

from thinc.api import ConfigValidationError

from spacy.lang.en import English
from spacy.language import Language
from spacy.training import Example


def test_initialize_arguments():
    name = "test_initialize_arguments"

    class CustomTokenizer:
        def __init__(self, tokenizer):
            self.tokenizer = tokenizer
            self.from_initialize = None

        def __call__(self, text):
            return self.tokenizer(text)

        def initialize(self, get_examples, nlp, custom: int):
            self.from_initialize = custom

    class Component:
        def __init__(self):
            self.from_initialize = None

        def initialize(
            self, get_examples, nlp, custom1: str, custom2: StrictBool = False
        ):
            self.from_initialize = (custom1, custom2)

    Language.factory(name, func=lambda nlp, name: Component())

    nlp = English()
    nlp.tokenizer = CustomTokenizer(nlp.tokenizer)
    example = Example.from_dict(nlp("x"), {})
    get_examples = lambda: [example]
    nlp.add_pipe(name)
    # The settings here will typically come from the [initialize] block
    init_cfg = {"tokenizer": {"custom": 1}, "components": {name: {}}}
    nlp.config["initialize"].update(init_cfg)
    with pytest.raises(ConfigValidationError) as e:
        # Empty config for component, no required custom1 argument
        nlp.initialize(get_examples)
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0]["loc"] == ("custom1",)
    assert errors[0]["type"] == "value_error.missing"
    init_cfg = {
        "tokenizer": {"custom": 1},
        "components": {name: {"custom1": "x", "custom2": 1}},
    }
    nlp.config["initialize"].update(init_cfg)
    with pytest.raises(ConfigValidationError) as e:
        # Wrong type of custom 2
        nlp.initialize(get_examples)
    errors = e.value.errors
    assert len(errors) == 1
    assert errors[0]["loc"] == ("custom2",)
    assert errors[0]["type"] == "value_error.strictbool"
    init_cfg = {
        "tokenizer": {"custom": 1},
        "components": {name: {"custom1": "x"}},
    }
    nlp.config["initialize"].update(init_cfg)
    nlp.initialize(get_examples)
    assert nlp.tokenizer.from_initialize == 1
    pipe = nlp.get_pipe(name)
    assert pipe.from_initialize == ("x", False)
