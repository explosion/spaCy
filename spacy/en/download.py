import sys
import os
import shutil

import plac
from sputnik import Sputnik


def migrate(path):
    data_path = os.path.join(path, 'data')
    if os.path.isdir(data_path):
        if os.path.islink(data_path):
            os.unlink(data_path)
        else:
            shutil.rmtree(data_path)
    for filename in os.listdir(path):
        if filename.endswith('.tgz'):
            os.unlink(os.path.join(path, filename))


def link(package, path):
    if os.path.exists(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)

    if not hasattr(os, 'symlink'):  # not supported by win+py27
        shutil.copytree(package.dir_path('data'), path)
    else:
        os.symlink(package.dir_path('data'), path)


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
)
def main(data_size='all', force=False):
    # TODO read version from the same source as the setup
    sputnik = Sputnik('spacy', '0.100.0', console=sys.stdout)

    path = os.path.dirname(os.path.abspath(__file__))

    data_path = os.path.abspath(os.path.join(path, '..', 'data'))
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    command = sputnik.command(
        data_path=data_path,
        repository_url='https://index.spacy.io')

    if force:
        command.purge()

    package = command.install('en_default')

    # FIXME clean up old-style packages
    migrate(path)


if __name__ == '__main__':
    plac.call(main)
