# coding: utf8
from __future__ import unicode_literals

import io
import os
import pip
import site
import plac
from . import util


@plac.annotations(
    origin=("Package name or path to model", "positional", None, str),
    link_name=("Name of link", "positional", None, str),
    force=("Force overwriting existing link", "flag", "f", bool)
)
def link(origin, link_name, force=False):
    """Create a symlink for models within the spacy/data directory. Accepts
    either the name of a pip package, or the local path to the model data
    directory. Linking models allows loading them via spacy.load(link_name)."""

    if is_package(origin):
        package_path = site.getsitepackages()[0]
        meta = get_meta(package_path, origin)
        data_dir = origin + '-' + meta['version']
        model_path = os.path.join(package_path, origin, data_dir)
        symlink(model_path, link_name, force)
    else:
        symlink(origin, link_name, force)


def symlink(model_path, link_name, force):
    if not os.path.isdir(model_path):
        util.sys_exit(
            "The data should be located in {p}".format(p=model_path),
            title="Can't locate model data")

    data_path = str(util.get_data_path())
    link_path = os.path.join(os.path.abspath(__file__ + '/../../'), data_path, link_name)

    if os.path.isdir(link_path):
        if force:
            os.unlink(link_path)
        else:
            util.sys_exit(
                "To overwrite an existing link, use the --force flag.",
                title="Link {l} already exists".format(l=link_name))
    model_path = os.path.abspath(model_path)
    os.symlink(model_path, link_path)
    util.print_msg(
        "{a} --> {b}".format(a=model_path, b=link_path),
        "You can now load the model via spacy.load('{l}').".format(l=link_name),
        title="Linking successful")


def get_meta(package_path, package):
    meta = util.parse_package_meta(package_path, package)
    if not meta:
        util.sys_exit()
    return meta


def is_package(origin):
    packages = pip.get_installed_distributions()
    for package in packages:
        if package.project_name.replace('-', '_') == origin:
            return True
    return False


if __name__ == '__main__':
    plac.call(link)
