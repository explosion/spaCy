# coding: utf8
from __future__ import unicode_literals

import plac
import requests
import os
import subprocess
import sys

from .link import link
from ..util import prints, get_package_path
from .. import about


@plac.annotations(
    model=("model to download, shortcut or name)", "positional", None, str),
    direct=("force direct download. Needs model name with version and won't "
            "perform compatibility check", "flag", "d", bool))
def download(cmd, model, direct=False):
    """
    Download compatible model from default download path using pip. Model
    can be shortcut, model name or, if --direct flag is set, full model name
    with version.
    """
    if direct:
        dl = download_model('{m}/{m}.tar.gz'.format(m=model))
    else:
        shortcuts = get_json(about.__shortcuts__, "available shortcuts")
        model_name = shortcuts.get(model, model)
        compatibility = get_compatibility()
        version = get_version(model_name, compatibility)
        dl = download_model('{m}-{v}/{m}-{v}.tar.gz'.format(m=model_name,
                                                            v=version))
        if dl == 0:
            try:
                # Get package path here because link uses
                # pip.get_installed_distributions() to check if model is a
                # package, which fails if model was just installed via
                # subprocess
                package_path = get_package_path(model_name)
                link(None, model_name, model, force=True,
                     model_path=package_path)
            except:
                # Dirty, but since spacy.download and the auto-linking is
                # mostly a convenience wrapper, it's best to show a success
                # message and loading instructions, even if linking fails.
                prints(
                    "Creating a shortcut link for 'en' didn't work (maybe "
                    "you don't have admin permissions?), but you can still "
                    "load the model via its full package name:",
                    "nlp = spacy.load('%s')" % model_name,
                    title="Download successful")


def get_json(url, desc):
    r = requests.get(url)
    if r.status_code != 200:
        msg = ("Couldn't fetch %s. Please find a model for your spaCy "
               "installation (v%s), and download it manually.")
        prints(msg % (desc, about.__version__), about.__docs_models__,
               title="Server error (%d)" % r.status_code, exits=1)
    return r.json()


def get_compatibility():
    version = about.__version__
    version = version.rsplit('.dev', 1)[0]
    comp_table = get_json(about.__compatibility__, "compatibility table")
    comp = comp_table['spacy']
    if version not in comp:
        prints("No compatible models found for v%s of spaCy." % version,
               title="Compatibility error", exits=1)
    return comp[version]


def get_version(model, comp):
    model = model.rsplit('.dev', 1)[0]
    if model not in comp:
        version = about.__version__
        msg = "No compatible model found for '%s' (spaCy v%s)."
        prints(msg % (model, version), title="Compatibility error", exits=1)
    return comp[model][0]


def download_model(filename):
    download_url = about.__download_url__ + '/' + filename
    return subprocess.call(
        [sys.executable, '-m', 'pip', 'install', '--no-cache-dir',
         download_url], env=os.environ.copy())
