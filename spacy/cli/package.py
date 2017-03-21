# coding: utf8
from __future__ import unicode_literals

import json
from shutil import copytree
from pathlib import Path

from .. import about
from .. import util


def package(input_dir, output_dir, force):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    check_dirs(input_path, output_path)

    meta = generate_meta()
    model_name = meta['lang'] + '_' + meta['name']
    model_name_v = model_name + '-' + meta['version']
    main_path = output_path / model_name_v
    package_path = main_path / model_name

    Path.mkdir(package_path, parents=True)
    copytree(input_path, package_path / model_name_v)
    create_file(main_path / 'meta.json', json.dumps(meta, indent=2))
    create_file(main_path / 'setup.py', TEMPLATE_SETUP.strip())
    create_file(main_path / 'MANIFEST.in', TEMPLATE_MANIFEST.strip())
    create_file(package_path / '__init__.py', TEMPLATE_INIT.strip())

    util.print_msg(
        main_path.as_posix(),
        "To build the package, run python setup.py sdist in that directory.",
        title="Successfully reated package {p}".format(p=model_name_v))


def check_dirs(input_path, output_path):
    if not input_path.exists():
        util.sys_exit(input_path.as_poisx(), title="Model directory not found")
    if not output_path.exists():
        util.sys_exit(output_path.as_posix(), title="Output directory not found")


def create_file(file_path, contents):
    file_path.touch()
    file_path.write_text(contents, encoding='utf-8')


def generate_meta():
    settings = [('lang', 'Model language', 'en'),
                ('name', 'Model name', 'model'),
                ('version', 'Model version', '0.0.0'),
                ('spacy_version', 'Required spaCy version', '>=2.0.0,<3.0.0'),
                ('description', 'Model description', False),
                ('author', 'Author', False),
                ('email', 'Author email', False),
                ('url', 'Author website', False),
                ('license', 'License', 'MIT')]

    util.print_msg("Enter the package settings for your model.", title="Generating meta.json")

    meta = {}
    for setting, desc, default in settings:
        response = util.get_raw_input(desc, default)
        meta[setting] = default if response == '' and default else response
    return meta


TEMPLATE_MANIFEST = """
include meta.json
"""


TEMPLATE_SETUP = """
#!/usr/bin/env python
# coding: utf8
from __future__ import unicode_literals

import io
import json
from os import path, walk
from shutil import copy
from setuptools import setup


def load_meta(fp):
    with io.open(fp, encoding='utf8') as f:
        return json.load(f)


def list_files(data_dir):
    output = []
    for root, _, filenames in walk(data_dir):
        for filename in filenames:
            if not filename.startswith('.'):
                output.append(path.join(root, filename))
    output = [path.relpath(p, path.dirname(data_dir)) for p in output]
    output.append('meta.json')
    return output


def setup_package():
    root = path.abspath(path.dirname(__file__))
    meta_path = path.join(root, 'meta.json')
    meta = load_meta(meta_path)
    model_name = str(meta['lang'] + '_' + meta['name'])
    model_dir = path.join(model_name, model_name + '-' + meta['version'])

    copy(meta_path, path.join(root, model_name))
    copy(meta_path, path.join(root, model_dir))

    setup(
        name=model_name,
        description=meta['description'],
        author=meta['author'],
        author_email=meta['email'],
        url=meta['url'],
        version=meta['version'],
        license=meta['license'],
        packages=[model_name],
        package_data={model_name: list_files(model_dir)},
        install_requires=['spacy' + meta['spacy_version']],
        zip_safe=False,
    )


if __name__ == '__main__':
    setup_package()
"""


TEMPLATE_INIT = """
from pathlib import Path
from spacy.util import get_lang_class
import pkg_resources
import json


def load_meta():
    with (Path(__file__).parent / 'meta.json').open() as f:
        return json.load(f)


def load(**kwargs):
    meta = load_meta()
    version = meta['version']
    data_dir = pkg_resources.resource_filename(__name__, __name__ + '-' + version)
    lang = get_lang_class(meta['lang'])
    return lang(path=Path(data_dir), **kwargs)
"""
