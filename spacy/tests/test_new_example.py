import pytest
from spacy.gold.new_example import NewExample as Example
from spacy.tokens import Doc
from spacy.vocab import Vocab


@pytest.fixture
def vocab():
    return Vocab()


def test_Example_init_requires_doc_objects(vocab):
    with pytest.raises(TypeError):
        eg = Example(None, None)
    with pytest.raises(TypeError):
        eg = Example(Doc(vocab, words=["hi"]), None)
    with pytest.raises(TypeError):
        eg = Example(None, Doc(vocab, words=["hi"]))



def test_Example_from_dict(vocab):
    eg = Example.from_dict(
        Doc(vocab, words=["hello", "world"]),
        {
            "words": ["hello", "world"]
        }
    )
    assert isinstance(eg.x, Doc)
    assert isinstance(eg.y, Doc)
