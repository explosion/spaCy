from spacy.cli.init_config import fill_config
from spacy.util import load_config
from spacy.lang.en import English
from thinc.api import Config

from ..util import make_tempdir


def test_issue7055():
    """Test that fill-config doesn't turn sourced components into factories."""
    source_cfg = {
        "nlp": {"lang": "en", "pipeline": ["tok2vec", "tagger"]},
        "components": {
            "tok2vec": {"factory": "tok2vec"},
            "tagger": {"factory": "tagger"},
        },
    }
    source_nlp = English.from_config(source_cfg)
    with make_tempdir() as dir_path:
        # We need to create a loadable source pipeline
        source_path = dir_path / "test_model"
        source_nlp.to_disk(source_path)
        base_cfg = {
            "nlp": {"lang": "en", "pipeline": ["tok2vec", "tagger", "ner"]},
            "components": {
                "tok2vec": {"source": str(source_path)},
                "tagger": {"source": str(source_path)},
                "ner": {"factory": "ner"},
            },
        }
        base_cfg = Config(base_cfg)
        base_path = dir_path / "base.cfg"
        base_cfg.to_disk(base_path)
        output_path = dir_path / "config.cfg"
        fill_config(output_path, base_path, silent=True)
        filled_cfg = load_config(output_path)
    assert filled_cfg["components"]["tok2vec"]["source"] == str(source_path)
    assert filled_cfg["components"]["tagger"]["source"] == str(source_path)
    assert filled_cfg["components"]["ner"]["factory"] == "ner"
    assert "model" in filled_cfg["components"]["ner"]
