# coding: utf-8

"""Test that longer and mixed texts are tokenized correctly."""


from __future__ import unicode_literals

import pytest


def test_tokenizer_handles_long_text(es_tokenizer):
    text = """Cuando a José Mujica lo invitaron a dar una conferencia

en Oxford este verano, su cabeza hizo "crac". La "más antigua" universidad de habla

inglesa, esa que cobra decenas de miles de euros de matrícula a sus alumnos

y en cuyos salones han disertado desde Margaret Thatcher hasta Stephen Hawking,

reclamaba los servicios de este viejo de 81 años, formado en un colegio público

en Montevideo y que pregona las bondades de la vida austera."""
    tokens = es_tokenizer(text)
    assert len(tokens) == 90


@pytest.mark.parametrize('text,length', [
    ("¿Por qué José Mujica?", 6),
    ("“¿Oh no?”", 6),
    ("""¡Sí! "Vámonos", contestó José Arcadio Buendía""", 11),
    ("Corrieron aprox. 10km.", 5),
    ("Y entonces por qué...", 5)])
def test_tokenizer_handles_cnts(es_tokenizer, text, length):
    tokens = es_tokenizer(text)
    assert len(tokens) == length
