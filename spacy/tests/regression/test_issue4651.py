import spacy
from spacy.lang.en import English
from spacy.pipeline import EntityRuler

def test_issue4651_with_phrase_matcher_attr():
    """Test that the EntityRuler PhraseMatcher is deserialize correctly using
    the method from_disk when the EntityRuler argument phrase_matcher_attr is
    specified.
    """
    nlp = English()
    ruler = EntityRuler(nlp, phrase_matcher_attr='LOWER')
    patterns = [{"label": "PYTHON_LIB", "pattern": "spacy", "id": "spaCy"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)
    nlp.to_disk('test_issue4651_model')

    text = "Spacy is a python library for nlp"
    doc = nlp(text)
    res_before = [(ent.text, ent.label_, ent.ent_id_) for ent in doc.ents]


    nlp_loaded = spacy.load('test_issue4651_model')
    loaded_doc = nlp_loaded(text)
    res_after = [(ent.text, ent.label_, ent.ent_id_) for ent in loaded_doc.ents]

    assert res_before == res_after

def test_issue4651_without_phrase_matcher_attr():
    """Test that the EntityRuler PhraseMatcher is deserialize correctly using
    the method from_disk when the EntityRuler argument phrase_matcher_attr is
    not specified.
    """
    nlp = English()
    ruler = EntityRuler(nlp)
    patterns = [{"label": "PYTHON_LIB", "pattern": "spacy", "id": "spaCy"}]
    ruler.add_patterns(patterns)
    nlp.add_pipe(ruler)
    nlp.to_disk('test_issue4651_model')

    text = "Spacy is a python library for nlp"
    doc = nlp(text)
    res_before = [(ent.text, ent.label_, ent.ent_id_) for ent in doc.ents]


    nlp_loaded = spacy.load('test_issue4651_model')
    loaded_doc = nlp_loaded(text)
    res_after = [(ent.text, ent.label_, ent.ent_id_) for ent in loaded_doc.ents]

    assert res_before == res_after