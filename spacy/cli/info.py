# coding: utf8
from __future__ import unicode_literals

import plac
import platform
from pathlib import Path

from ._messages import Messages
from ..compat import path2str
from .. import util
from .. import about


@plac.annotations(
    model=("optional: shortcut link of model", "positional", None, str),
    markdown=("generate Markdown for GitHub issues", "flag", "md", str),
    silent=("don't print anything (just return)", "flag", "s"))
def info(model=None, markdown=False, silent=False):
    """Print info about spaCy installation. If a model shortcut link is
    speficied as an argument, print model information. Flag --markdown
    prints details in Markdown for easy copy-pasting to GitHub issues.
    """
    if model:
        if util.is_package(model):
            model_path = util.get_package_path(model)
        else:
            model_path = util.get_data_path() / model
        meta_path = model_path / 'meta.json'
        if not meta_path.is_file():
            util.prints(meta_path, title=Messages.M020, exits=1)
        meta = util.read_json(meta_path)
        if model_path.resolve() != model_path:
            meta['link'] = path2str(model_path)
            meta['source'] = path2str(model_path.resolve())
        else:
            meta['source'] = path2str(model_path)
        if not silent:
            print_info(meta, 'model %s' % model, markdown)
        return meta
    data = {'spaCy version': about.__version__,
            'Location': path2str(Path(__file__).parent.parent),
            'Platform': platform.platform(),
            'Python version': platform.python_version(),
            'Models': list_models()}
    if not silent:
        print_info(data, 'spaCy', markdown)
    return data


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
