from spacy.en import English
import six

def test_tag_names():
    nlp = English()
    tokens = nlp(u'I ate pizzas with anchovies.', parse=True, tag=True)
    pizza = tokens[2]
    assert type(pizza.pos) == int
    assert isinstance(pizza.pos_, six.text_type)
    assert type(pizza.dep) == int
    assert isinstance(pizza.dep_, six.text_type)
    assert pizza.tag_ == u'NNS'
