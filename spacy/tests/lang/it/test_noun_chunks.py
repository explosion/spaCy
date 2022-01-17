from spacy.tokens import Doc
import pytest


# fmt: off
@pytest.mark.parametrize(
    "words,heads,deps,pos,chunk_offsets",
    [
        # determiner + noun
        # un pollo -> un pollo
        (
            ["un", "pollo"],
            [1, 1],
            ["det", "ROOT"],
            ["DET", "NOUN"],
            [(0,2)],
        ),
        # two determiners + noun
        # il mio cane -> il mio cane
        (
            ["il", "mio", "cane"],
            [2, 2, 2],
            ["det", "det:poss", "ROOT"],
            ["DET", "DET", "NOUN"],
            [(0,3)],
        ),
        # two determiners, one is after noun. rare usage but still testing
        # il cane mio-> il cane mio
        (
            ["il", "cane", "mio"],
            [1, 1, 1],
            ["det", "ROOT", "det:poss"],
            ["DET", "NOUN", "DET"],
            [(0,3)],
        ),
        # relative pronoun
        # È molto bello il vestito che hai acquistat -> il vestito, che   the dress that you bought is very pretty.
        (
            ["È", "molto", "bello", "il", "vestito", "che", "hai", "acquistato"],
            [2, 2, 2, 4, 2, 7, 7, 4],
            ['cop', 'advmod', 'ROOT', 'det', 'nsubj', 'obj', 'aux', 'acl:relcl'],
            ['AUX', 'ADV', 'ADJ', 'DET', 'NOUN', 'PRON', 'AUX', 'VERB'],
            [(3,5), (5,6)]
        ),
        # relative subclause
        # il computer che hai comprato -> il computer, che     the computer that you bought
        (
            ['il', 'computer', 'che', 'hai', 'comprato'],
            [1, 1, 4, 4, 1],
            ['det', 'ROOT', 'nsubj', 'aux', 'acl:relcl'],
            ['DET', 'NOUN', 'PRON', 'AUX', 'VERB'],
            [(0,2), (2,3)]
        ),
        # det + noun + adj
        # Una macchina grande  -> Una macchina grande
        (
            ["Una", "macchina", "grande"],
            [1, 1, 1],
            ["det", "ROOT", "amod"],
            ["DET", "NOUN", "ADJ"],
            [(0,3)],
        ),
        # noun + adj plural
        # mucche bianche 
        (
            ["mucche", "bianche"],
            [0, 0],
            ["ROOT", "amod"],
            ["NOUN", "ADJ"],
            [(0,2)],
        ),
        # det + adj + noun
        # Una grande macchina -> Una grande macchina
        (
            ['Una', 'grande', 'macchina'],
            [2, 2, 2],
            ["det", "amod", "ROOT"],
            ["DET", "ADJ", "NOUN"],
            [(0,3)]
        ),
        # det + adj + noun, det with apostrophe
        # un'importante associazione -> un'importante associazione
        (
            ["Un'", 'importante', 'associazione'],
            [2, 2, 2],
            ["det", "amod", "ROOT"],
            ["DET", "ADJ", "NOUN"],
            [(0,3)]
        ),
        # multiple adjectives
        # Un cane piccolo e marrone -> Un cane piccolo e marrone
        (
            ["Un", "cane", "piccolo", "e", "marrone"],
            [1, 1, 1, 4, 2],
            ["det", "ROOT", "amod", "cc", "conj"],
            ["DET", "NOUN", "ADJ", "CCONJ", "ADJ"],
            [(0,5)]
        ),
        # determiner, adjective, compound created by flat
        # le Nazioni Unite -> le Nazioni Unite
        (
            ["le", "Nazioni", "Unite"],
            [1, 1, 1],
            ["det", "ROOT", "flat:name"],
            ["DET", "PROPN", "PROPN"],
            [(0,3)]
        ),
        # one determiner + one noun + one adjective qualified by an adverb
        # alcuni contadini molto ricchi -> alcuni contadini molto ricchi     some very rich farmers
        (
            ['alcuni', 'contadini', 'molto', 'ricchi'],
            [1, 1, 3, 1],
            ['det', 'ROOT', 'advmod', 'amod'],
            ['DET', 'NOUN', 'ADV', 'ADJ'],
            [(0,4)]
        ),
        # Two NPs conjuncted
        # Ho un cane e un gatto -> un cane, un gatto
        ( 
            ['Ho', 'un', 'cane', 'e', 'un', 'gatto'],
            [0, 2, 0, 5, 5, 0],
            ['ROOT', 'det', 'obj', 'cc', 'det', 'conj'],
            ['VERB', 'DET', 'NOUN', 'CCONJ', 'DET', 'NOUN'],
            [(1,3), (4,6)]
         
        ),
        # Two NPs together
        # lo scrittore brasiliano Aníbal Machado -> lo scrittore brasiliano, Aníbal Machado
        (
            ['lo', 'scrittore', 'brasiliano', 'Aníbal', 'Machado'],
            [1, 1, 1, 1, 3],
            ['det', 'ROOT', 'amod', 'nmod', 'flat:name'],
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
        # gli Stati Uniti
        (
            ["gli", "Stati", "Uniti"],
            [1, 1, 1],
            ["det", "ROOT", "flat:name"],
            ["DET", "PROPN", "PROPN"],
            [(0,3)]
        ),
        # nmod relation between NPs
        # la distruzione della città -> la distruzione, città
        (
            ['la', 'distruzione', 'della', 'città'],
            [1, 1, 3, 1],
            ['det', 'ROOT', 'case', 'nmod'],
            ['DET', 'NOUN', 'ADP', 'NOUN'],
            [(0,2), (3,4)]
        ),
        # Compounding by nmod, several NPs chained together
        # la prima fabbrica di droga del governo -> la prima fabbrica, droga, governo
        (
            ["la", "prima", "fabbrica", "di", "droga", "del", "governo"],
            [2, 2, 2, 4, 2, 6, 2],
            ['det', 'amod', 'ROOT', 'case', 'nmod', 'case', 'nmod'],
            ['DET', 'ADJ', 'NOUN', 'ADP', 'NOUN', 'ADP', 'NOUN'],
            [(0, 3), (4, 5), (6, 7)]
        ),
        # several NPs
        # Traduzione del rapporto di Susana -> Traduzione, rapporto, Susana
        (
            ['Traduzione', 'del', 'rapporto', 'di', 'Susana'],
            [0, 2, 0, 4, 2],
            ['ROOT', 'case', 'nmod', 'case', 'nmod'],
            ['NOUN', 'ADP', 'NOUN', 'ADP', 'PROPN'],
            [(0,1), (2,3), (4,5)]  
       
        ),
        # Several NPs
        # Il gatto grasso di Susana e la sua amica -> Il gatto grasso, Susana, sua amica
        (  
            ['Il', 'gatto', 'grasso', 'di', 'Susana', 'e', 'la', 'sua', 'amica'],
            [1, 1, 1, 4, 1, 8, 8, 8, 1],
            ['det', 'ROOT', 'amod', 'case', 'nmod', 'cc', 'det', 'det:poss', 'conj'],
            ['DET', 'NOUN', 'ADJ', 'ADP', 'PROPN', 'CCONJ', 'DET', 'DET', 'NOUN'],
            [(0,3), (4,5), (6,9)]
        ),
        # Passive subject
        # La nuova spesa è alimentata dal grande conto in banca di Clinton  -> Le nuova spesa, grande conto, banca, Clinton
        (
            ['La', 'nuova', 'spesa', 'è', 'alimentata', 'dal', 'grande', 'conto', 'in', 'banca', 'di', 'Clinton'],
            [2, 2, 4, 4, 4, 7, 7, 4, 9, 7, 11, 9],
            ['det', 'amod', 'nsubj:pass', 'aux:pass', 'ROOT', 'case', 'amod', 'obl:agent', 'case', 'nmod', 'case', 'nmod'],
            ['DET', 'ADJ', 'NOUN', 'AUX', 'VERB', 'ADP', 'ADJ', 'NOUN', 'ADP', 'NOUN', 'ADP', 'PROPN'],
            [(0, 3), (6, 8), (9, 10), (11,12)]
        ),
        # Misc
        # Ma mentre questo prestito possa ora sembrare gestibile, un improvviso cambiamento delle circostanze potrebbe portare a problemi di debiti -> questo prestiti, un provisso cambiento, circostanze, problemi, debiti
        (
            ['Ma', 'mentre', 'questo', 'prestito', 'possa', 'ora', 'sembrare', 'gestibile', ',', 'un', 'improvviso', 'cambiamento', 'delle', 'circostanze', 'potrebbe', 'portare', 'a', 'problemi', 'di', 'debitii'],
            [15, 6, 3, 6, 6, 6, 15, 6, 6, 11, 11, 15, 13, 11, 15, 15, 17, 15, 19, 17],
            ['cc', 'mark', 'det', 'nsubj', 'aux', 'advmod', 'advcl', 'xcomp', 'punct', 'det', 'amod', 'nsubj', 'case', 'nmod', 'aux', 'ROOT', 'case', 'obl', 'case', 'nmod'],
            ['CCONJ', 'SCONJ', 'DET', 'NOUN', 'AUX', 'ADV', 'VERB', 'ADJ', 'PUNCT', 'DET', 'ADJ', 'NOUN', 'ADP', 'NOUN', 'AUX', 'VERB', 'ADP', 'NOUN', 'ADP', 'NOUN'],
            [(2,4), (9,12), (13,14), (17,18), (19,20)]
        )
    ],
)
# fmt: on
def test_it_noun_chunks(it_vocab, words, heads, deps, pos, chunk_offsets):
    doc = Doc(it_vocab, words=words, heads=heads, deps=deps, pos=pos)
    assert [(c.start, c.end) for c in doc.noun_chunks] == chunk_offsets


def test_noun_chunks_is_parsed_it(it_tokenizer):
    """Test that noun_chunks raises Value Error for 'it' language if Doc is not parsed."""
    doc = it_tokenizer("Sei andato a Oxford")
    with pytest.raises(ValueError):
        list(doc.noun_chunks)
