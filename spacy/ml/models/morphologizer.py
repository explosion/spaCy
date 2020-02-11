from pathlib import Path

from spacy import util


def default_morphologizer_config():
    loc = Path(__file__).parent / "defaults" / "morphologizer_defaults.cfg"
    return util.load_from_config(loc, create_objects=False)
