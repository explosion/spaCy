# coding: utf-8
from __future__ import unicode_literals

from ..download import download, get_compatibility, get_version, check_error_depr
import pytest


def test_download_fetch_compatibility():
    compatibility = get_compatibility()
    assert type(compatibility) == dict


@pytest.mark.slow
@pytest.mark.parametrize('model', ['en_core_web_md-1.2.0'])
def test_download_direct_download(model):
    download(model, direct=True)


@pytest.mark.parametrize('model', ['en_core_web_md'])
def test_download_get_matching_version_succeeds(model):
    comp = { model: ['1.7.0', '0.100.0'] }
    assert get_version(model, comp)


@pytest.mark.parametrize('model', ['en_core_web_md'])
def test_download_get_matching_version_fails(model):
    diff_model = 'test_' + model
    comp = { diff_model: ['1.7.0', '0.100.0'] }
    with pytest.raises(SystemExit):
        assert get_version(model, comp)


@pytest.mark.parametrize('model', [False, None, '', 'all'])
def test_download_no_model_depr_error(model):
    with pytest.raises(SystemExit):
        check_error_depr(model)
