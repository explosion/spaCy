import pickle

from spacy.lang.ko import Korean

from ...util import make_tempdir


def test_ko_tokenizer_serialize(ko_tokenizer):
    tokenizer_bytes = ko_tokenizer.to_bytes()
    nlp = Korean()
    nlp.tokenizer.from_bytes(tokenizer_bytes)
    assert tokenizer_bytes == nlp.tokenizer.to_bytes()

    with make_tempdir() as d:
        file_path = d / "tokenizer"
        ko_tokenizer.to_disk(file_path)
        nlp = Korean()
        nlp.tokenizer.from_disk(file_path)
        assert tokenizer_bytes == nlp.tokenizer.to_bytes()


def test_ko_tokenizer_pickle(ko_tokenizer):
    b = pickle.dumps(ko_tokenizer)
    ko_tokenizer_re = pickle.loads(b)
    assert ko_tokenizer.to_bytes() == ko_tokenizer_re.to_bytes()


def test_ko_tokenizer_natto_serialize(ko_tokenizer_natto):
    tokenizer_bytes = ko_tokenizer_natto.to_bytes()
    nlp = Korean()
    nlp.tokenizer.from_bytes(tokenizer_bytes)
    assert tokenizer_bytes == nlp.tokenizer.to_bytes()

    with make_tempdir() as d:
        file_path = d / "tokenizer"
        ko_tokenizer_natto.to_disk(file_path)
        nlp = Korean()
        nlp.tokenizer.from_disk(file_path)
        assert tokenizer_bytes == nlp.tokenizer.to_bytes()


def test_ko_tokenizer_natto_pickle(ko_tokenizer_natto):
    b = pickle.dumps(ko_tokenizer_natto)
    ko_tokenizer_natto_re = pickle.loads(b)
    assert ko_tokenizer_natto.to_bytes() == ko_tokenizer_natto_re.to_bytes()
