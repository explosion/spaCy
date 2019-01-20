# coding: utf-8
from __future__ import unicode_literals

import pytest
import os
from pathlib import Path
from spacy.compat import symlink_to, symlink_remove, path2str


@pytest.fixture
def target_local_path():
    return Path("./foo-target")


@pytest.fixture
def link_local_path():
    return Path("./foo-symlink")


@pytest.fixture(scope="function")
def setup_target(request, target_local_path, link_local_path):
    if not target_local_path.exists():
        os.mkdir(path2str(target_local_path))

    # yield -- need to cleanup even if assertion fails
    # https://github.com/pytest-dev/pytest/issues/2508#issuecomment-309934240
    def cleanup():
        symlink_remove(link_local_path)
        os.rmdir(path2str(target_local_path))

    request.addfinalizer(cleanup)


def test_create_symlink_windows(setup_target, target_local_path, link_local_path):
    assert target_local_path.exists()

    symlink_to(link_local_path, target_local_path)
    assert link_local_path.exists()
