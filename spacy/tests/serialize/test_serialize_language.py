# coding: utf-8
from __future__ import unicode_literals

from ..util import make_tempdir
from ...language import Language

import pytest


@pytest.fixture
def meta_data():
    return {
        'name': 'name-in-fixture',
        'version': 'version-in-fixture',
        'description': 'description-in-fixture',
        'author': 'author-in-fixture',
        'email': 'email-in-fixture',
        'url': 'url-in-fixture',
        'license': 'license-in-fixture',
        'vectors': {'width': 0, 'vectors': 0, 'keys': 0, 'name': None}
    }


def test_serialize_language_meta_disk(meta_data):
    language = Language(meta=meta_data)
    with make_tempdir() as d:
        language.to_disk(d)
        new_language = Language().from_disk(d)
    assert new_language.meta == language.meta
