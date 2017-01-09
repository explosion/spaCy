# coding: utf-8
from __future__ import unicode_literals

import pytest

from ...en import English
from ...de import German
from ...es import Spanish
from ...it import Italian
from ...fr import French
from ...pt import Portuguese
from ...nl import Dutch
from ...sv import Swedish
from ...hu import Hungarian


LANGUAGES = [English, German, Spanish, Italian, French, Dutch, Swedish, Hungarian]


@pytest.fixture(params=LANGUAGES)
def tokenizer(request):
    lang = request.param
    return lang.Defaults.create_tokenizer()
