import pytest
from spacy import registry
from thinc.api import Linear
from catalogue import RegistryError


def test_get_architecture():
    @registry.architectures("my_test_function")
    def create_model(nr_in, nr_out):
        return Linear(nr_in, nr_out)

    arch = registry.architectures.get("my_test_function")
    assert arch is create_model
    with pytest.raises(RegistryError):
        registry.architectures.get("not_an_existing_key")
