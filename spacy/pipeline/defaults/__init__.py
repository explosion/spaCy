from pathlib import Path

from ... import util

# For the default configs, we're setting validate to False by default to
# prevent errors on load if certain functions aren't imported yet. This is
# otherwise difficult to prevent while avoiding circular imports. The config
# will be validated again by default when it's used.


def default_nel_config():
    loc = Path(__file__).parent / "entity_linker_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_nel():
    loc = Path(__file__).parent / "entity_linker_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]


def default_morphologizer_config():
    loc = Path(__file__).parent / "morphologizer_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_morphologizer():
    loc = Path(__file__).parent / "morphologizer_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]


def default_parser_config():
    loc = Path(__file__).parent / "parser_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_parser():
    loc = Path(__file__).parent / "parser_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]


def default_ner_config():
    loc = Path(__file__).parent / "ner_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_ner():
    loc = Path(__file__).parent / "ner_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]


def default_senter_config():
    loc = Path(__file__).parent / "senter_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_senter():
    loc = Path(__file__).parent / "senter_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]


def default_tagger_config():
    loc = Path(__file__).parent / "tagger_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_tagger():
    loc = Path(__file__).parent / "tagger_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]


def default_textcat_config():
    loc = Path(__file__).parent / "textcat_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_textcat():
    loc = Path(__file__).parent / "textcat_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]


def default_tok2vec_config():
    loc = Path(__file__).parent / "tok2vec_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_tok2vec():
    loc = Path(__file__).parent / "tok2vec_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]


def default_simple_ner_config():
    loc = Path(__file__).parent / "simple_ner_defaults.cfg"
    return util.load_config(loc, create_objects=False, validate=False)


def default_simple_ner():
    loc = Path(__file__).parent / "simple_ner_defaults.cfg"
    return util.load_config(loc, create_objects=True)["model"]
