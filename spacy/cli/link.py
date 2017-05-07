# coding: utf8
from __future__ import unicode_literals

from pathlib import Path
from ..compat import symlink_to, path2str
from ..util import prints
from .. import util


def link(origin, link_name, force=False):
    if util.is_package(origin):
        model_path = util.get_model_package_path(origin)
    else:
        model_path = Path(origin)
    if not model_path.exists():
        prints("The data should be located in %s" % path2str(model_path),
               title="Can't locate model data", exits=True)
    link_path = util.get_data_path() / link_name
    if link_path.exists() and not force:
        prints("To overwrite an existing link, use the --force flag.",
               title="Link %s already exists" % link_name, exits=True)
    elif link_path.exists():
        link_path.unlink()
    try:
        symlink_to(link_path, model_path)
    except:
        # This is quite dirty, but just making sure other errors are caught.
        prints("Creating a symlink in spacy/data failed. Make sure you have "
               "the required permissions and try re-running the command as "
               "admin, or use a virtualenv. You can still import the model as a "
               "module and call its load() method, or create the symlink manually.",
               "%s --> %s" % (path2str(model_path), path2str(link_path)),
               title="Error: Couldn't link model to '%s'" % link_name)
        raise
    prints("%s --> %s" % (path2str(model_path), path2str(link_path)),
           "You can now load the model via spacy.load('%s')." % link_name,
           title="Linking successful")
