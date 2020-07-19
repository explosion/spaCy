from spacy.lang.ja import Japanese
from ...util import make_tempdir


def test_ja_tokenizer_serialize(ja_tokenizer):
    tokenizer_bytes = ja_tokenizer.to_bytes()
    nlp = Japanese()
    nlp.tokenizer.from_bytes(tokenizer_bytes)
    assert tokenizer_bytes == nlp.tokenizer.to_bytes()
    assert nlp.tokenizer.split_mode is None

    with make_tempdir() as d:
        file_path = d / "tokenizer"
        ja_tokenizer.to_disk(file_path)
        nlp = Japanese()
        nlp.tokenizer.from_disk(file_path)
        assert tokenizer_bytes == nlp.tokenizer.to_bytes()
        assert nlp.tokenizer.split_mode is None

    # split mode is (de)serialized correctly
    nlp = Japanese.from_config({"nlp": {"tokenizer": {"split_mode": "B"}}})
    nlp_r = Japanese()
    nlp_bytes = nlp.to_bytes()
    nlp_r.from_bytes(nlp_bytes)
    assert nlp_bytes == nlp_r.to_bytes()
    assert nlp_r.tokenizer.split_mode == "B"

    with make_tempdir() as d:
        nlp.to_disk(d)
        nlp_r = Japanese()
        nlp_r.from_disk(d)
        assert nlp_bytes == nlp_r.to_bytes()
        assert nlp_r.tokenizer.split_mode == "B"
