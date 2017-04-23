# coding: utf-8
from __future__ import unicode_literals

from ..util import ensure_path

from pathlib import Path
import pytest


@pytest.mark.parametrize('text', ['hello/world', 'hello world'])
def test_util_ensure_path_succeeds(text):
    path = ensure_path(text)
    assert isinstance(path, Path)
