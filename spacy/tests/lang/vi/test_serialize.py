import pickle

from spacy.lang.vi import Vietnamese

from ...util import make_tempdir


def test_vi_tokenizer_serialize(vi_tokenizer):
    tokenizer_bytes = vi_tokenizer.to_bytes()
    nlp = Vietnamese()
    nlp.tokenizer.from_bytes(tokenizer_bytes)
    assert tokenizer_bytes == nlp.tokenizer.to_bytes()
    assert nlp.tokenizer.use_pyvi is True

    with make_tempdir() as d:
        file_path = d / "tokenizer"
        vi_tokenizer.to_disk(file_path)
        nlp = Vietnamese()
        nlp.tokenizer.from_disk(file_path)
        assert tokenizer_bytes == nlp.tokenizer.to_bytes()
        assert nlp.tokenizer.use_pyvi is True

    # mode is (de)serialized correctly
    nlp = Vietnamese.from_config({"nlp": {"tokenizer": {"use_pyvi": False}}})
    nlp_bytes = nlp.to_bytes()
    nlp_r = Vietnamese()
    nlp_r.from_bytes(nlp_bytes)
    assert nlp_bytes == nlp_r.to_bytes()
    assert nlp_r.tokenizer.use_pyvi is False

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp_r = Vietnamese()
        nlp_r.from_disk(d)
        assert nlp_bytes == nlp_r.to_bytes()
        assert nlp_r.tokenizer.use_pyvi is False


def test_vi_tokenizer_pickle(vi_tokenizer):
    b = pickle.dumps(vi_tokenizer)
    vi_tokenizer_re = pickle.loads(b)
    assert vi_tokenizer.to_bytes() == vi_tokenizer_re.to_bytes()
