# coding: utf8
from __future__ import unicode_literals

import plac
from pathlib import Path
from wasabi import msg

from ..compat import symlink_to, path2str
from .. import util


@plac.annotations(
    origin=("package name or local path to model", "positional", None, str),
    link_name=("name of shortuct link to create", "positional", None, str),
    force=("force overwriting of existing link", "flag", "f", bool),
)
def link(origin, link_name, force=False, model_path=None):
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
        msg.fail(
            "Can't locate model data",
            "The data should be located in {}".format(path2str(model_path)),
            exits=1,
        )
    data_path = util.get_data_path()
    if not data_path or not data_path.exists():
        spacy_loc = Path(__file__).parent.parent
        msg.fail(
            "Can't find the spaCy data path to create model symlink",
            "Make sure a directory `/data` exists within your spaCy "
            "installation and try again. The data directory should be located "
            "here:".format(path=spacy_loc),
            exits=1,
        )
    link_path = util.get_data_path() / link_name
    if link_path.is_symlink() and not force:
        msg.fail(
            "Link '{}' already exists".format(link_name),
            "To overwrite an existing link, use the --force flag",
            exits=1,
        )
    elif link_path.is_symlink():  # does a symlink exist?
        # NB: It's important to check for is_symlink here and not for exists,
        # because invalid/outdated symlinks would return False otherwise.
        link_path.unlink()
    elif link_path.exists():  # does it exist otherwise?
        # NB: Check this last because valid symlinks also "exist".
        msg.fail(
            "Can't overwrite symlink '{}'".format(link_name),
            "This can happen if your data directory contains a directory or "
            "file of the same name.",
            exits=1,
        )
    details = "%s --> %s" % (path2str(model_path), path2str(link_path))
    try:
        symlink_to(link_path, model_path)
    except:  # noqa: E722
        # This is quite dirty, but just making sure other errors are caught.
        msg.fail(
            "Couldn't link model to '{}'".format(link_name),
            "Creating a symlink in spacy/data failed. Make sure you have the "
            "required permissions and try re-running the command as admin, or "
            "use a virtualenv. You can still import the model as a module and "
            "call its load() method, or create the symlink manually.",
        )
        msg.text(details)
        raise
    msg.good("Linking successful", details)
    msg.text("You can now load the model via spacy.load('{}')".format(link_name))
