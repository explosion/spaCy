from spacy.en import English

def test_tag_names():
    nlp = English()
    tokens = nlp(u'I ate pizzas with anchovies.', parse=True, tag=True)
    pizza = tokens[2]
    assert type(pizza.pos) == int
    assert type(pizza.pos_) == str
    assert type(pizza.dep) == int
    assert type(pizza.dep_) == str
    assert pizza.tag_ == u'NNS'
