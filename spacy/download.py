from __future__ import print_function

import sys

import sputnik
from sputnik.package_list import (PackageNotFoundException,
                                  CompatiblePackageNotFoundException)

from . import about
from . import util


def download(lang, force=False, fail_on_exist=True, data_path=None):
    if not data_path:
        data_path = util.get_data_path()

    # spaCy uses pathlib, and util.get_data_path returns a pathlib.Path object,
    # but sputnik (which we're using below) doesn't use pathlib and requires
    # its data_path parameters to be strings, so we coerce the data_path to a
    # str here.
    data_path = str(data_path)

    try:
        pkg = sputnik.package(about.__title__, about.__version__,
                        about.__models__.get(lang, lang), data_path)
        if force:
            shutil.rmtree(pkg.path)
        elif fail_on_exist:
            print("Model already installed. Please run 'python -m "
                  "spacy.%s.download --force' to reinstall." % lang, file=sys.stderr)
            sys.exit(0)
    except (PackageNotFoundException, CompatiblePackageNotFoundException):
        pass

    package = sputnik.install(about.__title__, about.__version__,
                              about.__models__.get(lang, lang), data_path)

    try:
        sputnik.package(about.__title__, about.__version__,
                        about.__models__.get(lang, lang), data_path)
    except (PackageNotFoundException, CompatiblePackageNotFoundException):
        print("Model failed to install. Please run 'python -m "
              "spacy.%s.download --force'." % lang, file=sys.stderr)
        sys.exit(1)

    print("Model successfully installed to %s" % data_path, file=sys.stderr)
