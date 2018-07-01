# coding: utf8
from __future__ import unicode_literals

import plac
from pathlib import Path

from ._messages import Messages
from ..compat import symlink_to, path2str
from ..util import prints
from .. import util


@plac.annotations(
    origin=("package name or local path to model", "positional", None, str),
    link_name=("name of shortuct link to create", "positional", None, str),
    force=("force overwriting of existing link", "flag", "f", bool))
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
        prints(Messages.M009.format(path=path2str(model_path)),
               title=Messages.M008, exits=1)
    data_path = util.get_data_path()
    if not data_path or not data_path.exists():
        spacy_loc = Path(__file__).parent.parent
        prints(Messages.M011, spacy_loc, title=Messages.M010, exits=1)
    link_path = util.get_data_path() / link_name
    if link_path.is_symlink() and not force:
        prints(Messages.M013, title=Messages.M012.format(name=link_name),
               exits=1)
    elif link_path.is_symlink():  # does a symlink exist?
        # NB: It's important to check for is_symlink here and not for exists,
        # because invalid/outdated symlinks would return False otherwise.
        link_path.unlink()
    elif link_path.exists(): # does it exist otherwise?
        # NB: Check this last because valid symlinks also "exist".
        prints(Messages.M015, link_path,
               title=Messages.M014.format(name=link_name), exits=1)
    msg = "%s --> %s" % (path2str(model_path), path2str(link_path))
    try:
        symlink_to(link_path, model_path)
    except:
        # This is quite dirty, but just making sure other errors are caught.
        prints(Messages.M017, msg, title=Messages.M016.format(name=link_name))
        raise
    prints(msg, Messages.M019.format(name=link_name), title=Messages.M018)
