import pytest
from spacy.gold.new_example import NewExample as Example
from spacy.tokens import Doc
from spacy.vocab import Vocab


def test_Example_init_requires_doc_objects():
    vocab = Vocab()
    with pytest.raises(TypeError):
        eg = Example(None, None)
    with pytest.raises(TypeError):
        eg = Example(Doc(vocab, words=["hi"]), None)
    with pytest.raises(TypeError):
        eg = Example(None, Doc(vocab, words=["hi"]))



def test_Example_from_dict_basic():
    eg = Example.from_dict(
        Doc(Vocab(), words=["hello", "world"]),
        {
            "words": ["hello", "world"]
        }
    )
    assert isinstance(eg.x, Doc)
    assert isinstance(eg.y, Doc)


@pytest.mark.parametrize("annots", [
    {"words": ["ice", "cream"], "tags": ["NN", "NN"]},
])
def test_Example_from_dict_with_tags(annots):
    vocab = Vocab()
    predicted = Doc(vocab, words=annots["words"])
    eg = Example.from_dict(predicted, annots)
    for i, token in enumerate(eg.reference):
        assert token.tag_ == annots["tags"][i]


"""
def test_Example_from_dict_with_entities(vocab):
    # TODO
    pass

def test_Example_from_dict_with_parse(vocab):
    # TODO
    pass

def test_Example_from_dict_with_morphology(vocab):
    # TODO
    pass

def test_Example_from_dict_with_sent_start(vocab):
    # TODO
    pass

def test_Example_from_dict_with_cats(vocab):
    # TODO
    pass

def test_Example_from_dict_with_links(vocab):
    # TODO
    pass
"""
