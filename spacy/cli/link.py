# coding: utf8
from __future__ import unicode_literals

import plac
from pathlib import Path

from ..compat import symlink_to, path2str
from ..util import prints
from .. import util


@plac.annotations(
    origin=("package name or local path to model", "positional", None, str),
    link_name=("name of shortuct link to create", "positional", None, str),
    force=("force overwriting of existing link", "flag", "f", bool))
def link(cmd, origin, link_name, force=False, model_path=None):
    """
    Create a symlink for models within the spacy/data directory. Accepts
    either the name of a pip package, or the local path to the model data
    directory. Linking models allows loading them via spacy.load(link_name).
    """
    if util.is_package(origin):
        model_path = util.get_package_path(origin)
    else:
        model_path = Path(origin) if model_path is None else Path(model_path)
    if not model_path.exists():
        prints("The data should be located in %s" % path2str(model_path),
               title="Can't locate model data", exits=1)
    data_path = util.get_data_path()
    if not data_path or not data_path.exists():
        spacy_loc = Path(__file__).parent.parent
        prints("Make sure a directory `/data` exists within your spaCy "
               "installation and try again. The data directory should be "
               "located here:", path2str(spacy_loc), exits=1,
               title="Can't find the spaCy data path to create model symlink")
    link_path = util.get_data_path() / link_name
    if link_path.exists() and not force:
        prints("To overwrite an existing link, use the --force flag.",
               title="Link %s already exists" % link_name, exits=1)
    elif link_path.exists():
        link_path.unlink()
    try:
        symlink_to(link_path, model_path)
    except:
        # This is quite dirty, but just making sure other errors are caught.
        prints("Creating a symlink in spacy/data failed. Make sure you have "
               "the required permissions and try re-running the command as "
               "admin, or use a virtualenv. You can still import the model as "
               "a module and call its load() method, or create the symlink "
               "manually.",
               "%s --> %s" % (path2str(model_path), path2str(link_path)),
               title="Error: Couldn't link model to '%s'" % link_name)
        raise
    prints("%s --> %s" % (path2str(model_path), path2str(link_path)),
           "You can now load the model via spacy.load('%s')" % link_name,
           title="Linking successful")
