from pathlib import Path

from spacy import util


def default_sentrec_config():
    loc = Path(__file__).parent / "defaults" / "sentrec_defaults.cfg"
    return util.load_from_config(loc, create_objects=False)
