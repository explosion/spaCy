from spacy.en import English
import six
import pytest


@pytest.mark.models
def test_tag_names(EN):
    tokens = EN(u'I ate pizzas with anchovies.', parse=False, tag=True)
    pizza = tokens[2]
    assert type(pizza.pos) == int
    assert isinstance(pizza.pos_, six.text_type)
    assert type(pizza.dep) == int
    assert isinstance(pizza.dep_, six.text_type)
    assert pizza.tag_ == u'NNS'
