# coding: utf8
from __future__ import unicode_literals

import plac
import platform
from pathlib import Path
from wasabi import Printer

from ._messages import Messages
from ..compat import path2str
from .. import util
from .. import about


@plac.annotations(
    model=("Optional shortcut link of model", "positional", None, str),
    markdown=("Generate Markdown for GitHub issues", "flag", "md", str),
    silent=("Don't print anything (just return)", "flag", "s"),
)
def info(model=None, markdown=False, silent=False):
    """
    Print info about spaCy installation. If a model shortcut link is
    speficied as an argument, print model information. Flag --markdown
    prints details in Markdown for easy copy-pasting to GitHub issues.
    """
    msg = Printer()
    if model:
        if util.is_package(model):
            model_path = util.get_package_path(model)
        else:
            model_path = util.get_data_path() / model
        meta_path = model_path / "meta.json"
        if not meta_path.is_file():
            msg.fail(Messages.M020, meta_path, exits=1)
        meta = util.read_json(meta_path)
        if model_path.resolve() != model_path:
            meta["link"] = path2str(model_path)
            meta["source"] = path2str(model_path.resolve())
        else:
            meta["source"] = path2str(model_path)
        if not silent:
            title = "Info about model '{}'".format(model)
            model_meta = {
                k: v for k, v in meta.items() if k not in ("accuracy", "speed")
            }
            if markdown:
                util.print_markdown(model_meta, title=title)
            else:
                msg.table(model_meta, title=title)
        return meta
    data = {
        "spaCy version": about.__version__,
        "Location": path2str(Path(__file__).parent.parent),
        "Platform": platform.platform(),
        "Python version": platform.python_version(),
        "Models": list_models(),
    }
    if not silent:
        title = "Info about spaCy"
        if markdown:
            util.print_markdown(data, title=title)
        else:
            msg.table(data, title=title)
    return data


def list_models():
    def exclude_dir(dir_name):
        # exclude common cache directories and hidden directories
        exclude = ("cache", "pycache", "__pycache__")
        return dir_name in exclude or dir_name.startswith(".")

    data_path = util.get_data_path()
    if data_path:
        models = [f.parts[-1] for f in data_path.iterdir() if f.is_dir()]
        return ", ".join([m for m in models if not exclude_dir(m)])
    return "-"
