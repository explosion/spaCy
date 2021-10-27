from spacy.tokens import Doc
import pytest


# fmt: off
@pytest.mark.parametrize(
    "words,heads,deps,pos,chunk_offsets",
    [
        # un gato -> "un gato"
        (
            ["un", "gato"],
            [1, 1],
            ["det", "ROOT"],
            ["DET", "NOUN"],
            [(0, 2)],
        ),
        # la camisa negra -> "la camisa negra"
        (
            ["la", "camisa", "negra"],
            [1, 1, 1],
            ["det", "ROOT", "amod"],
            ["DET", "NOUN", "ADJ"],
            [(0, 3)],
        ),
        # un lindo gatito -> "un lindo gatito"
        (
            ["Un", "lindo", "gatito"]
            [2, 2, 2],
            ["det", "amod", "ROOT"],
            ["DET", "ADJ", "NOUN"],
            [(0,3)]
        ),
        # una chica hermosa e inteligente -> una chica hermosa e inteligente
        (
            ["Una", "chica", "hermosa", "e", "inteligente"],
            [1, 1, 1, 4, 2],
            ["det", "ROOT", "amod", "cc", "conj"],
            ["DET", "NOUN", "ADJ", "CCONJ", "ADJ"],
            [(0,5)]
        ),
        # Tengo un gato y un perro -> un gato, un perro
        ( 
            ["Tengo", "un", "gato", "y", "un", "perro"],
            [0, 2, 0, 5, 5, 0],
            ["ROOT", "det", "obj", "cc", "det", "conj"],
            ["VERB", "DET", "NOUN", "CCONJ", "DET", "NOUN"],
            [(1,3), (4,6)]
         
        ),
        # Dom Pedro II -> Dom Pedro II
        (
            ["Dom", "Pedro", "II"],
            [0, 0, 0],
            ["ROOT", "flat", "flat"],
            ["PROPN", "PROPN", "PROPN"],
            [(0,3)]
        ),
        # los Estados Unidos -> los Estados Unidos
        (
            ["los", "Estados", "Unidos"],
            [1, 1, 1],
            ["det", "ROOT", "flat"],
            ["DET", "PROPN", "PROPN"],
            [(0,3)]
        ),
        # Miguel de Cervantes -> Miguel de Cervantes
        (
            ["Miguel", "de", "Cervantes"],
            [0, 2, 0],
            ["ROOT", "case", "flat"],
            ["PROPN", "ADP", "PROPN"],
            [(0,3)]
        ),
        (
            ["Rio", "de", "Janeiro"],
            [0, 2, 0],
            ["ROOT", "case", "flat"],
            ["PROPN", "ADP", "PROPN"],
            [(0,3)]
        ),
        # la destrucción de la ciudad -> la destrucción, la ciudad
        (
            ["la", "destrucción", "de", "la", "ciudad"],
            [1, 1, 4, 4, 1],
            ['det', 'ROOT', 'case', 'det', 'nmod'],
            ['DET', 'NOUN', 'ADP', 'DET', 'NOUN'],
            [(0,2), (3,5)]
        ),
        # la traducción de Susana del informe -> la traducción, Susana, informe
        (
            ['la', 'traducción', 'de', 'Susana', 'del', 'informe'],
            [1, 1, 3, 1, 5, 1],
            ['det', 'ROOT', 'case', 'nmod', 'case', 'nmod'],
            ['DET', 'NOUN', 'ADP', 'PROPN', 'ADP', 'NOUN'],
            [(0,2), (3,4), (5,6)]  
       
        ),
        # El gato regordete de Susana y su amigo -> el gato regordete, Susana, su amigo
        (  
            ['El', 'gato', 'regordete', 'de', 'Susana', 'y', 'su', 'amigo'],
            [1, 1, 1, 4, 1, 7, 7, 1],
            ['det', 'ROOT', 'amod', 'case', 'nmod', 'cc', 'det', 'conj'],
            ['DET', 'NOUN', 'ADJ', 'ADP', 'PROPN', 'CCONJ', 'DET', 'NOUN'],
            [(0,3), (4,5), (6,8)]
        )
    ],
)
# fmt: on
def test_es_noun_chunks(es_vocab, words, heads, deps, pos, chunk_offsets):
    doc = Doc(es_vocab, words=words, heads=heads, deps=deps, pos=pos)
    assert [(c.start, c.end) for c in doc.noun_chunks] == chunk_offsets


def test_noun_chunks_is_parsed_es(es_tokenizer):
    """Test that noun_chunks raises Value Error for 'es' language if Doc is not parsed."""
    doc = es_tokenizer("en Oxford este verano")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
