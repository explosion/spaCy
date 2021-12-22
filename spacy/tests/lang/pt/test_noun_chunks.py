from spacy.tokens import Doc
import pytest


# fmt: off
@pytest.mark.parametrize(
    "words,heads,deps,pos,chunk_offsets",
    [
        # determiner + noun
        # um cachorro -> um cachorro
        (
            ["um", "cachorro"],
            [1, 1],
            ["det", "ROOT"],
            ["DET", "NOUN"],
            [(0, 2)],
        ),
        # two determiners + noun
        # meu o pai -> meu o pai
        (
            ["meu", "o", "pai"],
            [2, 2, 2],
            ["det", "det", "ROOT"],
            ["DET", "DET", "NOUN"],
            [(0, 3)],
        ),
        # two determiners + noun
        # todos essos caros -> todos essos caros
        (
            ["todos", "essos", "caros"],
            [2, 2, 2],
            ["det", "det", "ROOT"],
            ["DET", "DET", "NOUN"],
            [(0, 3)],
        ),
        # two determiners, one is after noun
        # um irmão meu -> um irmão meu
        (
            ["um", "irmão", "meu"],
            [1, 1, 1],
            ["det", "ROOT", "det"],
            ["DET", "NOUN", "DET"],
            [(0, 3)],
        ),
        # two determiners + noun
        # o meu pai -> o meu pai
        (
            ["o", "meu", "pai"],
            [2, 2, 2],
            ["det","det", "ROOT"],
            ["DET", "DET", "NOUN"],
            [(0, 3)],
        ),
        # relative pronoun
        # A bicicleta essa está estragada -> A bicicleta
        (
            ['A', 'bicicleta', 'essa', 'está', 'estragada'],
            [1, 4, 1, 4, 4],
            ['det', 'nsubj', 'det', 'cop', 'ROOT'],
            ['DET', 'NOUN', 'PRON', 'AUX', 'ADJ'],
            [(0,2)]
        ),
        # relative subclause
        #  o computador que comprou -> o computador
        (
            ['o', 'computador', 'que', 'comprou'],
            [1, 1, 3, 1],
            ['det', 'ROOT', 'nsubj', 'acl:relcl'],
            ['DET', 'NOUN', 'PRON', 'VERB'],
            [(0, 2), (2, 3)]
        ),
        # det + noun + adj
        # O cachorro marrom  -> O cachorro marrom
        (
            ["O", "cachorro", "marrom"],
            [1, 1, 1],
            ["det", "ROOT", "amod"],
            ["DET", "NOUN", "ADJ"],
            [(0, 3)],
        ),
        # det + noun + adj plural
        # As calças baratas  -> As calças baratas
        (
            ["As", "calças", "baratas"],
            [1, 1, 1],
            ["det", "ROOT", "amod"],
            ["DET", "NOUN", "ADJ"],
            [(0, 3)],
        ),
        # det + adj + noun
        # Uma boa ideia -> Uma boa ideia
        (
            ['uma', 'boa', 'ideia'],
            [2, 2, 2],
            ["det", "amod", "ROOT"],
            ["DET", "ADJ", "NOUN"],
            [(0,3)]
        ),
        # multiple adjectives
        # Uma garota esperta e inteligente -> Uma garota esperta e inteligente
        (
            ["Uma", "garota", "esperta", "e", "inteligente"],
            [1, 1, 1, 4, 2],
            ["det", "ROOT", "amod", "cc", "conj"],
            ["DET", "NOUN", "ADJ", "CCONJ", "ADJ"],
            [(0,5)]
        ),
        # determiner, adjective, compound created by flat
        # a grande São Paolo -> a grande São Paolo
        (
            ["a", "grande", "São", "Paolo"],
            [2, 2, 2, 2],
            ["det", "amod", "ROOT", "flat:name"],
            ["DET", "ADJ", "PROPN", "PROPN"],
            [(0,4)]
        ),
        # one determiner + one noun + one adjective qualified by an adverb
        # alguns fazendeiros muito ricos -> alguns fazendeiros muito ricos
        (
            ['alguns', 'fazendeiros', 'muito', 'ricos'],
            [1, 1, 3, 1],
            ['det', 'ROOT', 'advmod', 'amod'],
            ['DET', 'NOUN', 'ADV', 'ADJ'],
            [(0,4)]
        ),
        # Two NPs conjuncted
        # Eu tenho um cachorro e um gato -> Eu, um cacharo, um gato
        ( 
            ["Eu", "tenho", "um", "cachorro", "e", "um", "gato"],
            [1, 1, 3, 1, 6, 6, 3],
            ['nsubj', 'ROOT', 'det', 'obj', 'cc', 'det', 'conj'],
            ['PRON', 'VERB', 'DET', 'NOUN', 'CCONJ', 'DET', 'NOUN'],
            [(0,1), (2,4), (5,7)]
         
        ),
        # Two NPs together
        # o escritor brasileiro Aníbal Machado -> o escritor brasileiro, Aníbal Machado
        (
            ['o', 'escritor', 'brasileiro', 'Aníbal', 'Machado'],
            [1, 1, 1, 1, 3],
            ['det', 'ROOT', 'amod', 'appos', 'flat:name'],
            ['DET', 'NOUN', 'ADJ', 'PROPN', 'PROPN'],
            [(0, 3), (3, 5)]
        ),
        # Noun compound, person name and titles
        # Dom Pedro II -> Dom Pedro II
        (
            ["Dom", "Pedro", "II"],
            [0, 0, 0],
            ["ROOT", "flat:name", "flat:name"],
            ["PROPN", "PROPN", "PROPN"],
            [(0,3)]
        ),
        # Noun compound created by flat
        # os Estados Unidos -> os Estados Unidos
        (
            ["os", "Estados", "Unidos"],
            [1, 1, 1],
            ["det", "ROOT", "flat:name"],
            ["DET", "PROPN", "PROPN"],
            [(0,3)]
        ),
        # nmod relation between NPs
        # a destruição da cidade -> a destruição, cidade
        (
            ['a', 'destruição', 'da', 'cidade'],
            [1, 1, 3, 1],
            ['det', 'ROOT', 'case', 'nmod'],
            ['DET', 'NOUN', 'ADP', 'NOUN'],
            [(0,2), (3,4)]
        ),
        # Compounding by nmod, several NPs chained together
        # a primeira fábrica de medicamentos do governo -> a primeira fábrica, medicamentos, governo
        (
            ["a", "primeira", "fábrica", "de", "medicamentos",  "do", "governo"],
            [2, 2, 2, 4, 2, 6, 2],
            ['det', 'amod', 'ROOT', 'case', 'nmod', 'case', 'nmod'],
            ['DET', 'ADJ', 'NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN'],
            [(0, 3), (4, 5), (6, 7)]
        ),
        # several NPs
        # Tradução da reportagem de Susana -> Tradução, reportagem, Susana
        (
            ['Tradução', 'da', 'reportagem', 'de', 'Susana'],
            [0, 2, 0, 4, 2],
            ['ROOT', 'case', 'nmod', 'case', 'nmod'],
            ['NOUN', 'ADP', 'NOUN', 'ADP', 'PROPN'],
            [(0,1), (2,3), (4,5)]  
       
        ),
        # Several NPs
        # O gato gordo da Susana e seu amigo -> O gato gordo, Susana, seu amigo
        (  
            ['O', 'gato', 'gordo', 'da', 'Susana', 'e', 'seu', 'amigo'],
            [1, 1, 1, 4, 1, 7, 7, 1],
            ['det', 'ROOT', 'amod', 'case', 'nmod', 'cc', 'det', 'conj'],
            ['DET', 'NOUN', 'ADJ', 'ADP', 'PROPN', 'CCONJ', 'DET', 'NOUN'],
            [(0,3), (4,5), (6,8)]
        ),
        # Passive subject
        # Os novos gastos são alimentados pela grande conta bancária de Clinton -> Os novos gastos, grande conta bancária, Clinton
        (
            ['Os', 'novos', 'gastos', 'são', 'alimentados', 'pela', 'grande', 'conta', 'bancária', 'de', 'Clinton'],
            [2, 2, 4, 4, 4, 7, 7, 4, 7, 10, 7],
            ['det', 'amod', 'nsubj:pass', 'aux:pass', 'ROOT', 'case', 'amod', 'obl:agent', 'amod', 'case', 'nmod'],
            ['DET', 'ADJ', 'NOUN', 'AUX', 'VERB', 'ADP', 'ADJ', 'NOUN', 'ADJ', 'ADP', 'PROPN'],
            [(0, 3), (6, 9), (10, 11)]
        )
    ],
)
# fmt: on
def test_pt_noun_chunks(pt_vocab, words, heads, deps, pos, chunk_offsets):
    doc = Doc(pt_vocab, words=words, heads=heads, deps=deps, pos=pos)
    assert [(c.start, c.end) for c in doc.noun_chunks] == chunk_offsets


def test_noun_chunks_is_parsed_pt(pt_tokenizer):
    """Test that noun_chunks raises Value Error for 'pt' language if Doc is not parsed."""
    doc = pt_tokenizer("en Oxford este verano")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
