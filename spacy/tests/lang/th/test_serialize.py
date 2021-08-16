import pickle

from spacy.lang.th import Thai
from ...util import make_tempdir


def test_th_tokenizer_serialize(th_tokenizer):
    tokenizer_bytes = th_tokenizer.to_bytes()
    nlp = Thai()
    nlp.tokenizer.from_bytes(tokenizer_bytes)
    assert tokenizer_bytes == nlp.tokenizer.to_bytes()

    with make_tempdir() as d:
        file_path = d / "tokenizer"
        th_tokenizer.to_disk(file_path)
        nlp = Thai()
        nlp.tokenizer.from_disk(file_path)
        assert tokenizer_bytes == nlp.tokenizer.to_bytes()


def test_th_tokenizer_pickle(th_tokenizer):
    b = pickle.dumps(th_tokenizer)
    th_tokenizer_re = pickle.loads(b)
    assert th_tokenizer.to_bytes() == th_tokenizer_re.to_bytes()
