import spacy
import pytest

@pytest.mark.models
def test_beam_parse():
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(u'Australia is a country', disable=['ner'])
    ents = nlp.entity(doc, beam_width=2)
    print(ents)

