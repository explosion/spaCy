import pickle
import numpy

from spacy.lang.en import English
from spacy.vocab import Vocab

from spacy.tests.util import make_tempdir


def test_pickle_ner():
    """ Ensure the pickling of the NER goes well"""
    vocab = Vocab(vectors_name="test_vocab_add_vector")
    nlp = English(vocab=vocab)
    ner = nlp.create_pipe("ner", config={"min_action_freq": 342})
    with make_tempdir() as tmp_path:
        with (tmp_path / "ner.pkl").open("wb") as file_:
            pickle.dump(ner, file_)
            assert ner.cfg["min_action_freq"] == 342

        with (tmp_path / "ner.pkl").open("rb") as file_:
            ner2 = pickle.load(file_)
            assert ner2.cfg["min_action_freq"] == 342


def test_issue4725():
    # ensures that this runs correctly and doesn't hang or crash because of the global vectors
    # if it does crash, it's usually because of calling 'spawn' for multiprocessing (e.g. on Windows)
    vocab = Vocab(vectors_name="test_vocab_add_vector")
    data = numpy.ndarray((5, 3), dtype="f")
    data[0] = 1.0
    data[1] = 2.0
    vocab.set_vector("cat", data[0])
    vocab.set_vector("dog", data[1])

    nlp = English(vocab=vocab)
    ner = nlp.create_pipe("ner")
    nlp.add_pipe(ner)
    nlp.begin_training()
    docs = ["Kurt is in London."] * 10
    for _ in nlp.pipe(docs, batch_size=2, n_process=2):
        pass
