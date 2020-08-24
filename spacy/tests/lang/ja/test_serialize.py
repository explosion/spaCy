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
    tokenizer = Japanese.from_config({"nlp": {"tokenizer": {"split_mode": "B"}}}).tokenizer
    tokenizer_r = Japanese().tokenizer
    tokenizer_bytes = tokenizer.to_bytes()
    tokenizer_r.from_bytes(tokenizer_bytes)
    assert tokenizer_bytes == tokenizer_r.to_bytes()
    assert tokenizer_r.split_mode == "B"

    with make_tempdir() as d:
        tokenizer.to_disk(d)
        tokenizer_r = Japanese().tokenizer
        tokenizer_r.from_disk(d)
        assert tokenizer_bytes == tokenizer_r.to_bytes()
        assert tokenizer_r.split_mode == "B"
