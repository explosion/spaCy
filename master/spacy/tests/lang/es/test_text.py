import pytest
from spacy.lang.es.lex_attrs import like_num
from spacy.lang.es import Spanish


@pytest.mark.issue(3803)
def test_issue3803():
    """Test that spanish num-like tokens have True for like_num attribute."""
    nlp = Spanish()
    text = "2 dos 1000 mil 12 doce"
    doc = nlp(text)

    assert [t.like_num for t in doc] == [True, True, True, True, True, True]


def test_es_tokenizer_handles_long_text(es_tokenizer):
    text = """Cuando a José Mujica lo invitaron a dar una conferencia

en Oxford este verano, su cabeza hizo "crac". La "más antigua" universidad de habla

inglesa, esa que cobra decenas de miles de euros de matrícula a sus alumnos

y en cuyos salones han disertado desde Margaret Thatcher hasta Stephen Hawking,

reclamaba los servicios de este viejo de 81 años, formado en un colegio público

en Montevideo y que pregona las bondades de la vida austera."""
    tokens = es_tokenizer(text)
    assert len(tokens) == 90


@pytest.mark.parametrize(
    "text,length",
    [
        ("¿Por qué José Mujica?", 6),
        ("“¿Oh no?”", 6),
        ("""¡Sí! "Vámonos", contestó José Arcadio Buendía""", 11),
        ("Corrieron aprox. 10km.", 5),
        ("Y entonces por qué...", 5),
    ],
)
def test_es_tokenizer_handles_cnts(es_tokenizer, text, length):
    tokens = es_tokenizer(text)
    assert len(tokens) == length


@pytest.mark.parametrize(
    "text,match",
    [
        ("10", True),
        ("1", True),
        ("10.000", True),
        ("1000", True),
        ("999,0", True),
        ("uno", True),
        ("dos", True),
        ("billón", True),
        ("veintiséis", True),
        ("perro", False),
        (",", False),
        ("1/2", True),
    ],
)
def test_lex_attrs_like_number(es_tokenizer, text, match):
    tokens = es_tokenizer(text)
    assert len(tokens) == 1
    assert tokens[0].like_num == match


@pytest.mark.parametrize("word", ["once"])
def test_es_lex_attrs_capitals(word):
    assert like_num(word)
    assert like_num(word.upper())
