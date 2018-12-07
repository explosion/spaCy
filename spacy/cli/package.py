# coding: utf8
from __future__ import unicode_literals

import plac
import shutil
from pathlib import Path
from wasabi import Printer, get_raw_input
import srsly

from ._messages import Messages
from ..compat import path2str
from .. import util
from .. import about


@plac.annotations(
    input_dir=("Directory with model data", "positional", None, str),
    output_dir=("Output parent directory", "positional", None, str),
    meta_path=("Path to meta.json", "option", "m", str),
    create_meta=("Create meta.json, even if one exists", "flag", "c", bool),
    force=("Force overwriting existing model in output directory", "flag", "f", bool),
)
def package(input_dir, output_dir, meta_path=None, create_meta=False, force=False):
    """
    Generate Python package for model data, including meta and required
    installation files. A new directory will be created in the specified
    output directory, and model data will be copied over. If --create-meta is
    set and a meta.json already exists in the output directory, the existing
    values will be used as the defaults in the command-line prompt.
    """
    msg = Printer()
    input_path = util.ensure_path(input_dir)
    output_path = util.ensure_path(output_dir)
    meta_path = util.ensure_path(meta_path)
    if not input_path or not input_path.exists():
        msg.fail(Messages.M008, input_path, exits=1)
    if not output_path or not output_path.exists():
        msg.fail(Messages.M040, output_path, exits=1)
    if meta_path and not meta_path.exists():
        msg.fail(Messages.M020, meta_path, exits=1)

    meta_path = meta_path or input_path / "meta.json"
    if meta_path.is_file():
        meta = srsly.read_json(meta_path)
        if not create_meta:  # only print if user doesn't want to overwrite
            msg.good(Messages.M041, meta_path)
        else:
            meta = generate_meta(input_dir, meta, msg)
    for key in ("lang", "name", "version"):
        if key not in meta or meta[key] == "":
            msg.fail(Messages.M048.format(key=key), Messages.M049, exits=1)
    model_name = meta["lang"] + "_" + meta["name"]
    model_name_v = model_name + "-" + meta["version"]
    main_path = output_path / model_name_v
    package_path = main_path / model_name

    if package_path.exists():
        if force:
            shutil.rmtree(path2str(package_path))
        else:
            msg.fail(
                Messages.M044,
                Messages.M045.format(path=path2str(package_path)),
                exits=1,
            )
    Path.mkdir(package_path, parents=True)
    shutil.copytree(path2str(input_path), path2str(package_path / model_name_v))
    create_file(main_path / "meta.json", srsly.json_dumps(meta))
    create_file(main_path / "setup.py", TEMPLATE_SETUP)
    create_file(main_path / "MANIFEST.in", TEMPLATE_MANIFEST)
    create_file(package_path / "__init__.py", TEMPLATE_INIT)
    msg.good(Messages.M042.format(name=model_name_v), main_path)
    msg.text(Messages.M043)


def create_file(file_path, contents):
    file_path.touch()
    file_path.open("w", encoding="utf-8").write(contents)


def generate_meta(model_path, existing_meta, msg):
    meta = existing_meta or {}
    settings = [
        ("lang", "Model language", meta.get("lang", "en")),
        ("name", "Model name", meta.get("name", "model")),
        ("version", "Model version", meta.get("version", "0.0.0")),
        ("spacy_version", "Required spaCy version", ">=%s,<3.0.0" % about.__version__),
        ("description", "Model description", meta.get("description", False)),
        ("author", "Author", meta.get("author", False)),
        ("email", "Author email", meta.get("email", False)),
        ("url", "Author website", meta.get("url", False)),
        ("license", "License", meta.get("license", "CC BY-SA 3.0")),
    ]
    nlp = util.load_model_from_path(Path(model_path))
    meta["pipeline"] = nlp.pipe_names
    meta["vectors"] = {
        "width": nlp.vocab.vectors_length,
        "vectors": len(nlp.vocab.vectors),
        "keys": nlp.vocab.vectors.n_keys,
    }
    msg.divider(Messages.M046)
    msg.text(Messages.M047)
    for setting, desc, default in settings:
        response = get_raw_input(desc, default)
        meta[setting] = default if response == "" and default else response
    if about.__title__ != "spacy":
        meta["parent_package"] = about.__title__
    return meta


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


def list_requirements(meta):
    parent_package = meta.get('parent_package', 'spacy')
    requirements = [parent_package + meta['spacy_version']]
    if 'setup_requires' in meta:
        requirements += meta['setup_requires']
    return requirements


def setup_package():
    root = path.abspath(path.dirname(__file__))
    meta_path = path.join(root, 'meta.json')
    meta = load_meta(meta_path)
    model_name = str(meta['lang'] + '_' + meta['name'])
    model_dir = path.join(model_name, model_name + '-' + meta['version'])

    copy(meta_path, path.join(model_name))
    copy(meta_path, model_dir)

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
        install_requires=list_requirements(meta),
        zip_safe=False,
    )


if __name__ == '__main__':
    setup_package()
""".strip()


TEMPLATE_MANIFEST = """
include meta.json
""".strip()


TEMPLATE_INIT = """
# coding: utf8
from __future__ import unicode_literals

from pathlib import Path
from spacy.util import load_model_from_init_py, get_model_meta


__version__ = get_model_meta(Path(__file__).parent)['version']


def load(**overrides):
    return load_model_from_init_py(__file__, **overrides)
""".strip()
