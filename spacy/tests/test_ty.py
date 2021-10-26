import spacy
from spacy import ty


def test_component_types():
    nlp = spacy.blank("en")
    tok2vec = nlp.create_pipe("tok2vec")
    tagger = nlp.create_pipe("tagger")
    entity_ruler = nlp.create_pipe("entity_ruler")
    assert isinstance(tok2vec, ty.TrainableComponent)
    assert isinstance(tagger, ty.TrainableComponent)
    assert not isinstance(entity_ruler, ty.TrainableComponent)
    assert isinstance(tok2vec, ty.InitializableComponent)
    assert isinstance(tagger, ty.InitializableComponent)
    assert isinstance(entity_ruler, ty.InitializableComponent)
    assert isinstance(tok2vec, ty.ListenedToComponent)
    assert not isinstance(tagger, ty.ListenedToComponent)
    assert not isinstance(entity_ruler, ty.ListenedToComponent)
