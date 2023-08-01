from spacy.compat import pickle
from spacy.language import Language


def test_pickle_single_doc():
    nlp = Language()
    doc = nlp("pickle roundtrip")
    data = pickle.dumps(doc, 1)
    doc2 = pickle.loads(data)
    assert doc2.text == "pickle roundtrip"


def test_list_of_docs_pickles_efficiently():
    nlp = Language()
    for i in range(10000):
        _ = nlp.vocab[str(i)]  # noqa: F841
    one_pickled = pickle.dumps(nlp("0"), -1)
    docs = list(nlp.pipe(str(i) for i in range(100)))
    many_pickled = pickle.dumps(docs, -1)
    assert len(many_pickled) < (len(one_pickled) * 2)
    many_unpickled = pickle.loads(many_pickled)
    assert many_unpickled[0].text == "0"
    assert many_unpickled[-1].text == "99"
    assert len(many_unpickled) == 100


def test_user_data_from_disk():
    nlp = Language()
    doc = nlp("Hello")
    doc.user_data[(0, 1)] = False
    b = doc.to_bytes()
    doc2 = doc.__class__(doc.vocab).from_bytes(b)
    assert doc2.user_data[(0, 1)] is False


def test_user_data_unpickles():
    nlp = Language()
    doc = nlp("Hello")
    doc.user_data[(0, 1)] = False
    b = pickle.dumps(doc)
    doc2 = pickle.loads(b)
    assert doc2.user_data[(0, 1)] is False


def test_hooks_unpickle():
    def inner_func(d1, d2):
        return "hello!"

    nlp = Language()
    doc = nlp("Hello")
    doc.user_hooks["similarity"] = inner_func
    b = pickle.dumps(doc)
    doc2 = pickle.loads(b)
    assert doc2.similarity(None) == "hello!"
