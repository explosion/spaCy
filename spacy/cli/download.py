# coding: utf8
from __future__ import unicode_literals

import plac
import requests
import os
import subprocess
import sys
import pkg_resources
from wasabi import Printer

from .link import link
from ..util import get_package_path
from .. import about


msg = Printer()


@plac.annotations(
    model=("Model to download (shortcut or name)", "positional", None, str),
    direct=("Force direct download of name + version", "flag", "d", bool),
    pip_args=("Additional arguments to be passed to `pip install` on model install"),
)
def download(model, direct=False, *pip_args):
    """
    Download compatible model from default download path using pip. Model
    can be shortcut, model name or, if --direct flag is set, full model name
    with version. For direct downloads, the compatibility check will be skipped.
    """
    dl_tpl = "{m}-{v}/{m}-{v}.tar.gz#egg={m}=={v}"
    if direct:
        components = model.split("-")
        model_name = "".join(components[:-1])
        version = components[-1]
        dl = download_model(dl_tpl.format(m=model_name, v=version), pip_args)
    else:
        shortcuts = get_json(about.__shortcuts__, "available shortcuts")
        model_name = shortcuts.get(model, model)
        compatibility = get_compatibility()
        version = get_version(model_name, compatibility)
        dl = download_model(dl_tpl.format(m=model_name, v=version), pip_args)
        if dl != 0:  # if download subprocess doesn't return 0, exit
            sys.exit(dl)
        msg.good(
            "Download and installation successful",
            "You can now load the model via spacy.load('{}')".format(model_name),
        )
        # Only create symlink if the model is installed via a shortcut like 'en'.
        # There's no real advantage over an additional symlink for en_core_web_sm
        # and if anything, it's more error prone and causes more confusion.
        if model in shortcuts:
            try:
                # Get package path here because link uses
                # pip.get_installed_distributions() to check if model is a
                # package, which fails if model was just installed via
                # subprocess
                package_path = get_package_path(model_name)
                link(model_name, model, force=True, model_path=package_path)
            except:  # noqa: E722
                # Dirty, but since spacy.download and the auto-linking is
                # mostly a convenience wrapper, it's best to show a success
                # message and loading instructions, even if linking fails.
                msg.warn(
                    "Download successful but linking failed",
                    "Creating a shortcut link for '{}' didn't work (maybe you "
                    "don't have admin permissions?), but you can still load "
                    "the model via its full package name: "
                    "nlp = spacy.load('{}')".format(model, model_name),
                )
        # If a model is downloaded and then loaded within the same process, our
        # is_package check currently fails, because pkg_resources.working_set
        # is not refreshed automatically (see #3923). We're trying to work
        # around this here be requiring the package explicitly.
        try:
            pkg_resources.working_set.require(model_name)
        except:  # noqa: E722
            # Maybe it's possible to remove this – mostly worried about cross-
            # platform and cross-Python copmpatibility here
            pass


def get_json(url, desc):
    r = requests.get(url)
    if r.status_code != 200:
        msg.fail(
            "Server error ({})".format(r.status_code),
            "Couldn't fetch {}. Please find a model for your spaCy "
            "installation (v{}), and download it manually. For more "
            "details, see the documentation: "
            "https://spacy.io/usage/models".format(desc, about.__version__),
            exits=1,
        )
    return r.json()


def get_compatibility():
    version = about.__version__
    version = version.rsplit(".dev", 1)[0]
    comp_table = get_json(about.__compatibility__, "compatibility table")
    comp = comp_table["spacy"]
    if version not in comp:
        msg.fail("No compatible models found for v{} of spaCy".format(version), exits=1)
    return comp[version]


def get_version(model, comp):
    model = model.rsplit(".dev", 1)[0]
    if model not in comp:
        msg.fail(
            "No compatible model found for '{}' "
            "(spaCy v{}).".format(model, about.__version__),
            exits=1,
        )
    return comp[model][0]


def download_model(filename, user_pip_args=None):
    download_url = about.__download_url__ + "/" + filename
    pip_args = ["--no-cache-dir", "--no-deps"]
    if user_pip_args:
        pip_args.extend(user_pip_args)
    cmd = [sys.executable, "-m", "pip", "install"] + pip_args + [download_url]
    return subprocess.call(cmd, env=os.environ.copy())
