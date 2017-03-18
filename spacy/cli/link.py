# coding: utf8
from __future__ import unicode_literals

import io
import os
import pip
import site
from pathlib import Path
from .. import util


def link(origin, link_name, force=False):
    if is_package(origin):
        link_package(origin, link_name, force)
    else:
        symlink(origin, link_name, force)


def link_package(origin, link_name, force=False):
    package_path = site.getsitepackages()[0]
    meta = get_meta(package_path, origin)
    data_dir = origin + '-' + meta['version']
    model_path = Path(package_path) / origin / data_dir
    symlink(model_path, link_name, force)


def symlink(model_path, link_name, force):
    if not model_path.exists():
        util.sys_exit(
            "The data should be located in {p}".format(p=model_path),
            title="Can't locate model data")

    data_path = str(util.get_data_path())
    link_path = Path(__file__).parent.parent / data_path / link_name

    if link_path.exists():
        if force:
            os.unlink(str(link_path))
        else:
            util.sys_exit(
                "To overwrite an existing link, use the --force flag.",
                title="Link {l} already exists".format(l=link_name))

    os.symlink(str(model_path), str(link_path))
    util.print_msg(
        "{a} --> {b}".format(a=str(model_path), b=str(link_path)),
        "You can now load the model via spacy.load('{l}').".format(l=link_name),
        title="Linking successful")


def get_meta(package_path, package):
    meta = util.parse_package_meta(package_path, package)
    return meta


def is_package(origin):
    packages = pip.get_installed_distributions()
    for package in packages:
        if package.project_name.replace('-', '_') == origin:
            return True
    return False
