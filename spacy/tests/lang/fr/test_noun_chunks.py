from spacy.tokens import Doc
import pytest


# fmt: off
@pytest.mark.parametrize(
    "words,heads,deps,pos,chunk_offsets",
    [
        # determiner + noun
        # un nom -> un nom
        (
            ["un", "nom"],
            [1, 1],
            ["det", "ROOT"],
            ["DET", "NOUN"],
            [(0, 2)],
        ),
        # determiner + noun starting with vowel
        # l'heure -> l'heure
        (
            ["l'", "heure"],
            [1, 1],
            ["det", "ROOT"],
            ["DET", "NOUN"],
            [(0, 2)],
        ),
        # determiner + plural noun
        # les romans -> les romans
        (
            ["les", "romans"],
            [1, 1],
            ["det", "ROOT"],
            ["DET", "NOUN"],
            [(0, 2)],
        ),
        # det + adj + noun
        # Le vieux Londres  -> Le vieux Londres 
        (
            ['Les', 'vieux', 'Londres'],
            [2, 2, 2],
            ["det", "amod", "ROOT"],
            ["DET", "ADJ", "NOUN"],
            [(0,3)]
        ),
        # det + noun + adj
        # le nom propre  -> le nom propre   a proper noun
        (
            ["le", "nom", "propre"],
            [1, 1, 1],
            ["det", "ROOT", "amod"],
            ["DET", "NOUN", "ADJ"],
            [(0, 3)],
        ),
        # det + noun + adj plural
        # Les chiens bruns  -> les chiens bruns
        (
            ["Les", "chiens", "bruns"],
            [1, 1, 1],
            ["det", "ROOT", "amod"],
            ["DET", "NOUN", "ADJ"],
            [(0, 3)],
        ),
        # multiple adjectives: one adj before the noun, one adj after the noun
        # un nouveau film intéressant -> un nouveau film intéressant
        (
            ["un", "nouveau", "film", "intéressant"],
            [2, 2, 2, 2],
            ["det", "amod", "ROOT", "amod"],
            ["DET", "ADJ", "NOUN", "ADJ"],
            [(0,4)]
        ),
        # multiple adjectives, both adjs after the noun
        # une personne intelligente et drôle -> une personne intelligente et drôle
        (
            ["une", "personne", "intelligente", "et", "drôle"],
            [1, 1, 1, 4, 2],
            ["det", "ROOT", "amod", "cc", "conj"],
            ["DET", "NOUN", "ADJ", "CCONJ", "ADJ"],
            [(0,5)]
        ),
        # relative pronoun
        # un bus qui va au ville -> un bus, qui, ville
        (
            ['un', 'bus', 'qui', 'va', 'au', 'ville'],
            [1, 1, 3, 1, 5, 3],
            ['det', 'ROOT', 'nsubj', 'acl:relcl', 'case', 'obl:arg'],
            ['DET', 'NOUN', 'PRON', 'VERB', 'ADP', 'NOUN'],
            [(0,2), (2,3), (5,6)]
        ),
        # relative subclause
        # Voilà la maison que nous voulons acheter -> la maison, nous         That's the house that we want to buy.
        (
            ['Voilà', 'la', 'maison', 'que', 'nous', 'voulons', 'acheter'],
            [0, 2, 0, 5, 5, 2, 5],
            ['ROOT', 'det', 'obj', 'mark', 'nsubj', 'acl:relcl', 'xcomp'],
            ['VERB', 'DET', 'NOUN', 'SCONJ', 'PRON', 'VERB', 'VERB'],
            [(1,3), (4,5)]
        ),
        # Person name and title by flat
        # Louis XIV -> Louis XIV
        (
            ["Louis", "XIV"],
            [0, 0],
            ["ROOT", "flat:name"],
            ["PROPN", "PROPN"],
            [(0,2)]
        ),
        # Organization name by flat
        # Nations Unies -> Nations Unies
        (
            ["Nations", "Unies"],
            [0, 0],
            ["ROOT", "flat:name"],
            ["PROPN", "PROPN"],
            [(0,2)]
        ),
        # Noun compound, person name created by two flats
        # Louise de Bratagne -> Louise de Bratagne
        (
            ["Louise", "de", "Bratagne"],
            [0, 0, 0],
            ["ROOT", "flat:name", "flat:name"],
            ["PROPN", "PROPN", "PROPN"],
            [(0,3)]
        ),
        # Noun compound, person name created by two flats
        # Louis François Joseph -> Louis François Joseph
        (
            ["Louis", "François", "Joseph"],
            [0, 0, 0],
            ["ROOT", "flat:name", "flat:name"],
            ["PROPN", "PROPN", "PROPN"],
            [(0,3)]
        ),
        # one determiner + one noun + one adjective qualified by an adverb
        # quelques agriculteurs très riches -> quelques agriculteurs très riches
        (
            ["quelques", "agriculteurs", "très", "riches"],
            [1, 1, 3, 1],
            ['det', 'ROOT', 'advmod', 'amod'],
            ['DET', 'NOUN', 'ADV', 'ADJ'],
            [(0,4)]
        ),
        # Two NPs conjuncted
        # Il a un chien et un chat -> Il, un chien, un chat
        ( 
            ['Il', 'a', 'un', 'chien', 'et', 'un', 'chat'],
            [1, 1, 3, 1, 6, 6, 3],
            ['nsubj', 'ROOT', 'det', 'obj', 'cc', 'det', 'conj'],
            ['PRON', 'VERB', 'DET', 'NOUN', 'CCONJ', 'DET', 'NOUN'],
            [(0,1), (2,4), (5,7)]
         
        ),
        # Two NPs together
        # l'écrivain brésilien Aníbal Machado -> l'écrivain brésilien, Aníbal Machado
        (
            ["l'", 'écrivain', 'brésilien', 'Aníbal', 'Machado'],
            [1, 1, 1, 1, 3],
            ['det', 'ROOT', 'amod', 'appos', 'flat:name'],
            ['DET', 'NOUN', 'ADJ', 'PROPN', 'PROPN'],
            [(0, 3), (3, 5)]
        ),
        # nmod relation between NPs
        # la destruction de la ville -> la destruction, la ville
        (
            ['la', 'destruction', 'de', 'la', 'ville'],
            [1, 1, 4, 4, 1],
            ['det', 'ROOT', 'case', 'det', 'nmod'],
            ['DET', 'NOUN', 'ADP', 'DET', 'NOUN'],
            [(0,2), (3,5)]
        ),
        # nmod relation between NPs
        # Archiduchesse d’Autriche -> Archiduchesse, Autriche
        (
            ['Archiduchesse', 'd’', 'Autriche'],
            [0, 2, 0],
            ['ROOT', 'case', 'nmod'],
            ['NOUN', 'ADP', 'PROPN'],
            [(0,1), (2,3)]
        ),
        # Compounding by nmod, several NPs chained together
        # la première usine de drogue du gouvernement -> la première usine, drogue, gouvernement
        (
            ["la", "première", "usine", "de", "drogue", "du", "gouvernement"],
            [2, 2, 2, 4, 2, 6, 2],
            ['det', 'amod', 'ROOT', 'case', 'nmod', 'case', 'nmod'],
            ['DET', 'ADJ', 'NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN'],
            [(0, 3), (4, 5), (6, 7)]
        ),
        # several NPs
        # Traduction du rapport de Susana -> Traduction, rapport, Susana
        (
            ['Traduction', 'du', 'raport', 'de', 'Susana'],
            [0, 2, 0, 4, 2],
            ['ROOT', 'case', 'nmod', 'case', 'nmod'],
            ['NOUN', 'ADP', 'NOUN', 'ADP', 'PROPN'],
            [(0,1), (2,3), (4,5)]  
       
        ),
        # Several NPs
        # Le gros chat de Susana et son amie -> Le gros chat, Susana, son amie
        (  
            ['Le', 'gros', 'chat', 'de', 'Susana', 'et', 'son', 'amie'],
            [2, 2, 2, 4, 2, 7, 7, 2],
            ['det', 'amod', 'ROOT', 'case', 'nmod', 'cc', 'det', 'conj'],
            ['DET', 'ADJ', 'NOUN', 'ADP', 'PROPN', 'CCONJ', 'DET', 'NOUN'],
            [(0,3), (4,5), (6,8)]
        ),
        # Passive subject
        # Les nouvelles dépenses sont alimentées par le grand compte bancaire de Clinton -> Les nouvelles dépenses, le grand compte bancaire, Clinton
        (
            ['Les', 'nouvelles', 'dépenses', 'sont', 'alimentées', 'par', 'le', 'grand', 'compte', 'bancaire', 'de', 'Clinton'],
            [2, 2, 4, 4, 4, 8, 8, 8, 4, 8, 11, 8],
            ['det', 'amod', 'nsubj:pass', 'aux:pass', 'ROOT', 'case', 'det', 'amod', 'obl:agent', 'amod', 'case', 'nmod'],
            ['DET', 'ADJ', 'NOUN', 'AUX', 'VERB', 'ADP', 'DET', 'ADJ', 'NOUN', 'ADJ', 'ADP', 'PROPN'],
            [(0, 3), (6, 10), (11, 12)]
        )
    ],
)
# fmt: on
def test_fr_noun_chunks(fr_vocab, words, heads, deps, pos, chunk_offsets):
    doc = Doc(fr_vocab, words=words, heads=heads, deps=deps, pos=pos)
    assert [(c.start, c.end) for c in doc.noun_chunks] == chunk_offsets


def test_noun_chunks_is_parsed_fr(fr_tokenizer):
    """Test that noun_chunks raises Value Error for 'fr' language if Doc is not parsed."""
    doc = fr_tokenizer("Je suis allé à l'école")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
