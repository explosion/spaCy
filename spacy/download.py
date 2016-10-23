from __future__ import print_function

import sys

import sputnik
from sputnik.package_list import (PackageNotFoundException,
                                  CompatiblePackageNotFoundException)

from . import about
from . import util


def download(lang, force=False, fail_on_exist=True):
    if force:
        sputnik.purge(about.__title__, about.__version__)

    try:
        sputnik.package(about.__title__, about.__version__,
                        about.__models__.get(lang, lang))
        if fail_on_exist:
            print("Model already installed. Please run 'python -m "
                  "spacy.%s.download --force' to reinstall." % lang, file=sys.stderr)
            sys.exit(0)
    except (PackageNotFoundException, CompatiblePackageNotFoundException):
        pass

    package = sputnik.install(about.__title__, about.__version__,
                              about.__models__.get(lang, lang))

    try:
        sputnik.package(about.__title__, about.__version__,
                        about.__models__.get(lang, lang))
    except (PackageNotFoundException, CompatiblePackageNotFoundException):
        print("Model failed to install. Please run 'python -m "
              "spacy.%s.download --force'." % lang, file=sys.stderr)
        sys.exit(1)

    data_path = util.get_data_path()
    print("Model successfully installed to %s" % data_path, file=sys.stderr)
