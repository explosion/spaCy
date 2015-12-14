#!/usr/bin/env python
from __future__ import print_function
import json
import re
import sys
from bisect import bisect
from datetime import datetime
from datetime import timedelta

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen

from pip.commands.install import InstallCommand


def get_releases(package_name):
    url = 'https://pypi.python.org/pypi/%s/json' % package_name
    return json.loads(urlopen(url).read().decode('utf8'))['releases']


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


date = parse_iso8601(sys.argv[1])
args = ['%s==%s' % (p, select_version(date, p)) for p in sys.argv[2:]]

pip = InstallCommand()
options, args = pip.parse_args(args)
options.force_reinstall = True
options.ignore_installed = True

try:
    print(pip.run(options, args))
except OSError as e:
    if e.errno != 13:
        raise e
    print("You lack permissions to uninstall this package. Perhaps run with sudo? Exiting.")
    exit(13)
