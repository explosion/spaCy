#!/usr/bin/env python
from __future__ import print_function
import json
import re
import sys
from bisect import bisect
from datetime import datetime
from datetime import timedelta
import ssl

try:
    from urllib.request import Request, build_opener, HTTPSHandler, URLError
except ImportError:
    from urllib2 import Request, build_opener, HTTPSHandler, URLError

from pip.commands.uninstall import UninstallCommand
from pip.commands.install import InstallCommand
from pip import get_installed_distributions


def get_releases(package_name):
    url = 'https://pypi.python.org/pypi/%s/json' % package_name

    ssl_context = HTTPSHandler(
        context=ssl.SSLContext(ssl.PROTOCOL_TLSv1))
    opener = build_opener(ssl_context)

    retries = 10
    while retries > 0:
        try:
            r = opener.open(Request(url))
            break
        except URLError:
            retries -= 1

    return json.loads(r.read().decode('utf8'))['releases']


def parse_iso8601(s):
    return datetime(*map(int, re.split('[^\d]', s)))


def select_version(select_date, package_name):
    versions = []
    for version, dists in get_releases(package_name).items():
        date = [parse_iso8601(d['upload_time']) for d in dists]
        if date:
            versions.append((sorted(date)[0], version))

    versions = sorted(versions)
    min_date = versions[0][0]
    if select_date < min_date:
        raise Exception('invalid select_date: %s, must be '
                        '%s or newer.' % (select_date, min_date))

    return versions[bisect([x[0] for x in versions], select_date) - 1][1]


installed_packages = [
    package.project_name
    for package in
    get_installed_distributions()
    if (not package.location.endswith('dist-packages') and
        package.project_name not in ('pip', 'setuptools'))
]

if installed_packages:
    pip = UninstallCommand()
    options, args = pip.parse_args(installed_packages)
    options.yes = True

    try:
        pip.run(options, args)
    except OSError as e:
        if e.errno != 13:
            raise e
        print("You lack permissions to uninstall this package. Perhaps run with sudo? Exiting.")
        exit(13)


date = parse_iso8601(sys.argv[1])
packages = {p: select_version(date, p) for p in sys.argv[2:]}
args = ['=='.join(a) for a in packages.items()]

cmd = InstallCommand()
options, args = cmd.parse_args(args)
options.ignore_installed = True
options.force_reinstall = True

try:
    print(cmd.run(options, args))
except OSError as e:
    if e.errno != 13:
        raise e
    print("You lack permissions to uninstall this package. Perhaps run with sudo? Exiting.")
    exit(13)
