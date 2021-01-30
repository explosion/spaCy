import pytest
from spacy import registry
from thinc.api import Linear
from catalogue import RegistryError


@registry.architectures.register("my_test_function")
def create_model(nr_in, nr_out):
    return Linear(nr_in, nr_out)


def test_get_architecture():
    arch = registry.architectures.get("my_test_function")
    assert arch is create_model
    with pytest.raises(RegistryError):
        registry.architectures.get("not_an_existing_key")
