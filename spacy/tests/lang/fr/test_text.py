# coding: utf8
from __future__ import unicode_literals
import pytest

from .... import util

@pytest.fixture(scope='module')
def fr_tokenizer():
    return util.get_lang_class('fr').Defaults.create_tokenizer()



def test_tokenizer_handles_long_text(fr_tokenizer):
    text = """L'histoire du TAL commence dans les années 1950, bien que l'on puisse \
trouver des travaux antérieurs. En 1950, Alan Turing éditait un article \
célèbre sous le titre « Computing machinery and intelligence » qui propose ce \
qu'on appelle à présent le test de Turing comme critère d'intelligence. \
Ce critère dépend de la capacité d'un programme informatique de personnifier \
un humain dans une conversation écrite en temps réel, de façon suffisamment \
convaincante que l'interlocuteur humain ne peut distinguer sûrement — sur la \
base du seul contenu de la conversation — s'il interagit avec un programme \
ou avec un autre vrai humain."""

    tokens = fr_tokenizer(text)
    assert len(tokens) == 113
