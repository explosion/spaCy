import sys
import os
import shutil

import plac
from sputnik import Sputnik


def migrate(path):
    data_path = os.path.join(path, 'data')
    if os.path.isdir(data_path) and not os.path.islink(data_path):
        shutil.rmtree(data_path)
    for filename in os.listdir(path):
        if filename.endswith('tgz'):
            os.unlink(os.path.join(path, filename))


def link(package, path):
    if os.path.exists(path):
        os.unlink(path)
    os.symlink(os.path.join(package.path, 'data'),
               os.path.join(path))


@plac.annotations(
    force=("Force overwrite", "flag", "f", bool),
)
def main(force=False):
    # TODO read version from the same source as the setup
    sputnik = Sputnik('spacy', '0.99.0', console=sys.stdout)

    path = os.path.dirname(os.path.abspath(__file__))

    command = sputnik.make_command(
        data_path=path,
        repository_url=os.environ.get('REPOSITORY_URL'))

    if force:
        command.purge()

    package = command.install('en_default')

    # FIXME clean up old-style packages
    migrate(path)

    # FIXME supply spacy with an old-style data dir
    link(package, os.path.join(path, 'data'))


if __name__ == '__main__':
    plac.call(main)
