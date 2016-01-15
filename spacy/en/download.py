import sys
import os
import shutil

import plac
import sputnik

from .. import about


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
    path = os.path.dirname(os.path.abspath(__file__))

    data_path = os.path.abspath(os.path.join(path, '..', 'data'))
    if not os.path.isdir(data_path):
        os.mkdir(data_path)

    if force:
        sputnik.purge('spacy', about.short_version, data_path=data_path)

    package = sputnik.install('spacy', about.short_version, 'en_default==1.0.4',
                              data_path=data_path)

    # FIXME clean up old-style packages
    migrate(path)


if __name__ == '__main__':
    plac.call(main)
