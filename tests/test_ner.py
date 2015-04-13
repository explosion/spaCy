from spacy.en import English


nlp = English()

def test_simple_types():
    tokens = nlp(u'Mr. Best flew to New York on Saturday morning.')
    ents = list(tokens.ents)
    assert ents[0].start == 1
    assert ents[0].end == 2
    assert ents[0].label_ == 'PERSON'
    assert ents[1].start == 4
    assert ents[1].end == 6
    assert ents[1].label_ == 'GPE'
    assert ents[2].start == 7
    assert ents[2].end == 8
    assert ents[2].label_ == 'DATE'
    assert ents[3].start == 8
    assert ents[3].end == 9
    assert ents[3].label_ == 'TIME'
