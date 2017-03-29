# coding: utf8
from __future__ import unicode_literals

import json
import shutil
import requests
from pathlib import Path

from .. import about
from .. import util


def package(input_dir, output_dir, force):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    check_dirs(input_path, output_path)

    template_setup = get_template('setup.py')
    template_manifest = get_template('MANIFEST.in')
    template_init = get_template('en_model_name/__init__.py')
    meta = generate_meta()

    model_name = meta['lang'] + '_' + meta['name']
    model_name_v = model_name + '-' + meta['version']
    main_path = output_path / model_name_v
    package_path = main_path / model_name

    create_dirs(package_path, force)
    shutil.copytree(input_path.as_posix(), (package_path / model_name_v).as_posix())
    create_file(main_path / 'meta.json', json.dumps(meta, indent=2))
    create_file(main_path / 'setup.py', template_setup)
    create_file(main_path / 'MANIFEST.in', template_manifest)
    create_file(package_path / '__init__.py', template_init)

    util.print_msg(
        main_path.as_posix(),
        "To build the package, run `python setup.py sdist` in that directory.",
        title="Successfully created package {p}".format(p=model_name_v))


def check_dirs(input_path, output_path):
    if not input_path.exists():
        util.sys_exit(input_path.as_poisx(), title="Model directory not found")
    if not output_path.exists():
        util.sys_exit(output_path.as_posix(), title="Output directory not found")


def create_dirs(package_path, force):
    if package_path.exists():
        if force:
            shutil.rmtree(package_path.as_posix())
        else:
            util.sys_exit(package_path.as_posix(),
                "Please delete the directory and try again.",
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


def get_template(filepath):
    url = 'https://raw.githubusercontent.com/explosion/spacy-dev-resources/master/templates/model/'
    r = requests.get(url + filepath)
    if r.status_code != 200:
        util.sys_exit(
            "Couldn't fetch template files from GitHub.",
            title="Server error ({c})".format(c=r.status_code))
    return r.text
