from spacy.util import decaying

def test_decaying():
    sizes = decaying(10., 1., .5)
    size = next(sizes)
    assert size == 10.
    size = next(sizes)
    assert size == 10. - 0.5
    size = next(sizes)
    assert size == 10. - 0.5 - 0.5
