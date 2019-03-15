# coding: utf-8
from __future__ import unicode_literals

import pytest
import os
from pathlib import Path
from spacy import util
from spacy import prefer_gpu, require_gpu
from spacy.compat import symlink_to, symlink_remove, path2str
from spacy._ml import PrecomputableAffine


@pytest.fixture
def symlink_target():
    return Path("./foo-target")


@pytest.fixture
def symlink():
    return Path("./foo-symlink")


@pytest.fixture(scope="function")
def symlink_setup_target(request, symlink_target, symlink):
    if not symlink_target.exists():
        os.mkdir(path2str(symlink_target))
    # yield -- need to cleanup even if assertion fails
    # https://github.com/pytest-dev/pytest/issues/2508#issuecomment-309934240
    def cleanup():
        symlink_remove(symlink)
        os.rmdir(path2str(symlink_target))

    request.addfinalizer(cleanup)


@pytest.mark.parametrize("text", ["hello/world", "hello world"])
def test_util_ensure_path_succeeds(text):
    path = util.ensure_path(text)
    assert isinstance(path, Path)


@pytest.mark.parametrize("package", ["numpy"])
def test_util_is_package(package):
    """Test that an installed package via pip is recognised by util.is_package."""
    assert util.is_package(package)


@pytest.mark.parametrize("package", ["thinc"])
def test_util_get_package_path(package):
    """Test that a Path object is returned for a package name."""
    path = util.get_package_path(package)
    assert isinstance(path, Path)


def test_PrecomputableAffine(nO=4, nI=5, nF=3, nP=2):
    model = PrecomputableAffine(nO=nO, nI=nI, nF=nF, nP=nP)
    assert model.W.shape == (nF, nO, nP, nI)
    tensor = model.ops.allocate((10, nI))
    Y, get_dX = model.begin_update(tensor)
    assert Y.shape == (tensor.shape[0] + 1, nF, nO, nP)
    assert model.d_pad.shape == (1, nF, nO, nP)
    dY = model.ops.allocate((15, nO, nP))
    ids = model.ops.allocate((15, nF))
    ids[1, 2] = -1
    dY[1] = 1
    assert model.d_pad[0, 2, 0, 0] == 0.0
    model._backprop_padding(dY, ids)
    assert model.d_pad[0, 2, 0, 0] == 1.0
    model.d_pad.fill(0.0)
    ids.fill(0.0)
    dY.fill(0.0)
    ids[1, 2] = -1
    ids[1, 1] = -1
    ids[1, 0] = -1
    dY[1] = 1
    assert model.d_pad[0, 2, 0, 0] == 0.0
    model._backprop_padding(dY, ids)
    assert model.d_pad[0, 2, 0, 0] == 3.0


def test_prefer_gpu():
    assert not prefer_gpu()


def test_require_gpu():
    with pytest.raises(ValueError):
        require_gpu()


def test_create_symlink_windows(symlink_setup_target, symlink_target, symlink):
    assert symlink_target.exists()
    symlink_to(symlink, symlink_target)
    assert symlink.exists()
