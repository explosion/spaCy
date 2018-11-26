# coding: utf-8
from __future__ import unicode_literals

import pytest
import os
from pathlib import Path

from ..compat import symlink_to, symlink_remove, path2str


def target_local_path():
    return "./foo-target"


def link_local_path():
    return "./foo-symlink"


@pytest.fixture(scope="function")
def setup_target(request):
    target = Path(target_local_path())
    if not target.exists():
        os.mkdir(path2str(target))

    # yield -- need to cleanup even if assertion fails
    # https://github.com/pytest-dev/pytest/issues/2508#issuecomment-309934240
    def cleanup():
        symlink_remove(Path(link_local_path()))
        os.rmdir(target_local_path())

    request.addfinalizer(cleanup)


def test_create_symlink_windows(setup_target):
    target = Path(target_local_path())
    link = Path(link_local_path())
    assert target.exists()

    symlink_to(link, target)
    assert link.exists()
