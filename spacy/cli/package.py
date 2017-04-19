# coding: utf8
from __future__ import unicode_literals

import shutil
import requests
from pathlib import Path

from ..compat import unicode_, json_dumps
from .. import util


def package(input_dir, output_dir, meta_path, force):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    meta_path = util.ensure_path(meta_path)
    check_dirs(input_path, output_path, meta_path)

    template_setup = get_template('setup.py')
    template_manifest = get_template('MANIFEST.in')
    template_init = get_template('en_model_name/__init__.py')

    meta_path = meta_path or input_path / 'meta.json'
    if meta_path.is_file():
        util.print_msg(unicode_(meta_path), title="Reading meta.json from file")
        meta = util.read_json(meta_path)
    else:
        meta = generate_meta()

    validate_meta(meta, ['lang', 'name', 'version'])
    model_name = meta['lang'] + '_' + meta['name']
    model_name_v = model_name + '-' + meta['version']
    main_path = output_path / model_name_v
    package_path = main_path / model_name

    create_dirs(package_path, force)
    shutil.copytree(unicode_(input_path), unicode_(package_path / model_name_v))
    create_file(main_path / 'meta.json', json_dumps(meta))
    create_file(main_path / 'setup.py', template_setup)
    create_file(main_path / 'MANIFEST.in', template_manifest)
    create_file(package_path / '__init__.py', template_init)

    util.print_msg(
        unicode_(main_path),
        "To build the package, run `python setup.py sdist` in that directory.",
        title="Successfully created package {p}".format(p=model_name_v))


def check_dirs(input_path, output_path, meta_path):
    if not input_path.exists():
        util.sys_exit(unicode_(input_path.as_poisx), title="Model directory not found")
    if not output_path.exists():
        util.sys_exit(unicode_(output_path), title="Output directory not found")
    if meta_path and not meta_path.exists():
        util.sys_exit(unicode_(meta_path), title="meta.json not found")


def create_dirs(package_path, force):
    if package_path.exists():
        if force:
            shutil.rmtree(unicode_(package_path))
        else:
            util.sys_exit(unicode_(package_path),
                "Please delete the directory and try again, or use the --force "
                "flag to overwrite existing directories.",
                title="Package directory already exists")
    Path.mkdir(package_path, parents=True)


def create_file(file_path, contents):
    file_path.touch()
    file_path.open('w', encoding='utf-8').write(contents)


def generate_meta():
    settings = [('lang', 'Model language', 'en'),
                ('name', 'Model name', 'model'),
                ('version', 'Model version', '0.0.0'),
                ('spacy_version', 'Required spaCy version', '>=1.7.0,<2.0.0'),
                ('description', 'Model description', False),
                ('author', 'Author', False),
                ('email', 'Author email', False),
                ('url', 'Author website', False),
                ('license', 'License', 'CC BY-NC 3.0')]

    util.print_msg("Enter the package settings for your model.", title="Generating meta.json")

    meta = {}
    for setting, desc, default in settings:
        response = util.get_raw_input(desc, default)
        meta[setting] = default if response == '' and default else response
    return meta


def validate_meta(meta, keys):
    for key in keys:
        if key not in meta or meta[key] == '':
            util.sys_exit(
                "This setting is required to build your package.",
                title='No "{k}" setting found in meta.json'.format(k=key))


def get_template(filepath):
    url = 'https://raw.githubusercontent.com/explosion/spacy-dev-resources/master/templates/model/'
    r = requests.get(url + filepath)
    if r.status_code != 200:
        util.sys_exit(
            "Couldn't fetch template files from GitHub.",
            title="Server error ({c})".format(c=r.status_code))
    return r.text
