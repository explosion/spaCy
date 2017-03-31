# coding: utf8
from __future__ import unicode_literals

import pip
from pathlib import Path
import importlib
from .. import util


def link(origin, link_name, force=False):
    if is_package(origin):
        link_package(origin, link_name, force)
    else:
        symlink(origin, link_name, force)


def link_package(package_name, link_name, force=False):
    # Here we're importing the module just to find it. This is worryingly
    # indirect, but it's otherwise very difficult to find the package.
    # Python's installation and import rules are very complicated.
    pkg = importlib.import_module(package_name)
    package_path = Path(pkg.__file__).parent.parent

    meta = get_meta(package_path, package_name)
    model_name = package_name + '-' + meta['version']
    model_path = package_path / package_name / model_name
    symlink(model_path, link_name, force)


def symlink(model_path, link_name, force):
    model_path = Path(model_path)
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

    # Add workaround for Python 2 on Windows (see issue #909)
    if util.is_python2() and util.is_windows():
        import subprocess
        command = ['mklink', '/d', link_path, model_path]
        subprocess.call(command, shell=True)
    else:
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
