from __future__ import print_function

import sys

import sputnik
from sputnik.package_list import (PackageNotFoundException,
                                  CompatiblePackageNotFoundException)

from . import about


def download(lang, force=False):
    if force:
        sputnik.purge(about.__title__, about.__version__)

    try:
        sputnik.package(about.__title__, about.__version__, about.__models__[lang])
        print("Model already installed. Please run 'python -m "
              "spacy.%s.download --force' to reinstall." % lang, file=sys.stderr)
        sys.exit(1)
    except (PackageNotFoundException, CompatiblePackageNotFoundException):
        pass

    package = sputnik.install(about.__title__, about.__version__, about.__models__[lang])

    try:
        sputnik.package(about.__title__, about.__version__, about.__models__[lang])
    except (PackageNotFoundException, CompatiblePackageNotFoundException):
        print("Model failed to install. Please run 'python -m "
              "spacy.%s.download --force'." % lang, file=sys.stderr)
        sys.exit(1)

    print("Model successfully installed.", file=sys.stderr)
