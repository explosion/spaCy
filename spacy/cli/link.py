# coding: utf8
from __future__ import unicode_literals

import pip
from pathlib import Path
from distutils.sysconfig import get_python_lib
from .. import util


def link(origin, link_name, force=False):
    if is_package(origin):
        link_package(origin, link_name, force)
    else:
        symlink(origin, link_name, force)


def link_package(origin, link_name, force=False):
    package_path = get_python_lib()
    meta = get_meta(package_path, origin)
    data_dir = origin + '-' + meta['version']
    model_path = Path(package_path) / origin / data_dir
    symlink(model_path, link_name, force)


def symlink(model_path, link_name, force):
    if not Path(model_path).exists():
        util.sys_exit(
            "The data should be located in {p}".format(p=model_path),
            title="Can't locate model data")

    link_path = util.get_data_path() / link_name

    if link_path.exists() and not force:
        util.sys_exit(
            "To overwrite an existing link, use the --force flag.",
            title="Link {l} already exists".format(l=link_name))
    elif link_path.exists():
        link_path.unlink()

    link_path.symlink_to(model_path)
    util.print_msg(
        "{a} --> {b}".format(a=model_path.as_posix(), b=link_path.as_posix()),
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
