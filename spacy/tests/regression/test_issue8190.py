import spacy
from spacy.lang.en import English
from ..util import make_tempdir


def test_issue8190():
    """Test that config overrides are not lost after load is complete."""
    source_cfg = {
        "nlp": {
            "lang": "en",
        },
        "custom": {"key": "value"},
    }
    source_nlp = English.from_config(source_cfg)
    with make_tempdir() as dir_path:
        # We need to create a loadable source pipeline
        source_path = dir_path / "test_model"
        source_nlp.to_disk(source_path)
        nlp = spacy.load(source_path, config={"custom": {"key": "updated_value"}})

        assert nlp.config["custom"]["key"] == "updated_value"
