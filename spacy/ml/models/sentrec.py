from pathlib import Path

from spacy import util


def default_sentrec():
    loc = Path(__file__).parent / "defaults" / "sentrec_defaults.cfg"
    return util.load_from_config(loc, create_objects=True)["model"]
