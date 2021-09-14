from spacy.lang.ja import Japanese


def test_ja_morphologizer_factory():
    nlp = Japanese()
    morphologizer = nlp.add_pipe("morphologizer")
    assert morphologizer.cfg["extend"] is True
