# coding: utf8
from __future__ import unicode_literals

import platform
from pathlib import Path

from .. import about
from .. import util


def info(model=None, markdown=False):
    if model:
        data = util.parse_package_meta(util.get_data_path(), model, require=True)
        model_path = Path(__file__).parent / util.get_data_path() / model
        if model_path.resolve() != model_path:
            data['link'] = str(model_path)
            data['source'] = str(model_path.resolve())
        else:
            data['source'] = str(model_path)
        print_info(data, "model " + model, markdown)

    else:
        data = get_spacy_data()
        print_info(data, "spaCy", markdown)


def print_info(data, title, markdown):
    title = "Info about {title}".format(title=title)

    if markdown:
        util.print_markdown(data, title=title)

    else:
        util.print_table(data, title=title)


def get_spacy_data():
    return {
        'spaCy version': about.__version__,
        'Location': str(Path(__file__).parent.parent),
        'Platform': platform.platform(),
        'Python version': platform.python_version(),
        'Installed models': ', '.join(list_models())
    }


def list_models():
    # exclude common cache directories – this means models called "cache" etc.
    # won't show up in list, but it seems worth it
    exclude = ['cache', 'pycache', '__pycache__']
    data_path = util.get_data_path()
    models = [f.parts[-1] for f in data_path.iterdir() if f.is_dir()]
    return [m for m in models if m not in exclude]
