# coding: utf8
from __future__ import unicode_literals

import platform
from pathlib import Path

from ..compat import path2str
from .. import about
from .. import util


def info(model=None, markdown=False):
    if model:
        model_path = util.resolve_model_path(model)
        meta = util.parse_package_meta(model_path)
        if model_path.resolve() != model_path:
            meta['link'] = path2str(model_path)
            meta['source'] = path2str(model_path.resolve())
        else:
            meta['source'] = path2str(model_path)
        print_info(meta, 'model %s' % model, markdown)
    else:
        data = {'spaCy version': about.__version__,
                'Location': path2str(Path(__file__).parent.parent),
                'Platform': platform.platform(),
                'Python version': platform.python_version(),
                'Models': list_models()}
        print_info(data, 'spaCy', markdown)


def print_info(data, title, markdown):
    title = 'Info about %s' % title
    if markdown:
        util.print_markdown(data, title=title)
    else:
        util.print_table(data, title=title)


def list_models():
    def exclude_dir(dir_name):
        # exclude common cache directories and hidden directories
        exclude = ['cache', 'pycache', '__pycache__']
        return dir_name in exclude or dir_name.startswith('.')
    data_path = util.get_data_path()
    if data_path:
        models = [f.parts[-1] for f in data_path.iterdir() if f.is_dir()]
        return ', '.join([m for m in models if not exclude_dir(m)])
    return '-'
