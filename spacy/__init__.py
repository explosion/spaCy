# coding: utf8
from __future__ import unicode_literals

from .cli.info import info as cli_info
from .glossary import explain
from .deprecated import resolve_load_name
from .about import __version__
from . import util


def load(name, **overrides):
    name = resolve_load_name(name, **overrides)
    return util.load_model(name, **overrides)


def info(model=None, markdown=False):
    return cli_info(None, model, markdown)
