#!/usr/bin/env python
from __future__ import print_function

from pip.commands.uninstall import UninstallCommand
from pip import get_installed_distributions


packages = []
for package in get_installed_distributions():
    if package.location.endswith('dist-packages'):
        continue
    elif package.project_name in ('pip', 'setuptools'):
        continue
    packages.append(package.project_name)


if packages:
    pip = UninstallCommand()
    options, args = pip.parse_args(packages)
    options.yes = True

    try:
        pip.run(options, args)
    except OSError as e:
        if e.errno != 13:
            raise e
        print("You lack permissions to uninstall this package. Perhaps run with sudo? Exiting.")
        exit(13)
