import pytest
from spacy.tokens import Doc


pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def test_ru_doc_lemmatization(ru_lemmatizer):
    words = ["мама", "мыла", "раму"]
    pos = ["NOUN", "VERB", "NOUN"]
    morphs = [
        "Animacy=Anim|Case=Nom|Gender=Fem|Number=Sing",
        "Aspect=Imp|Gender=Fem|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Act",
        "Animacy=Anim|Case=Acc|Gender=Fem|Number=Sing",
    ]
    doc = Doc(ru_lemmatizer.vocab, words=words, pos=pos, morphs=morphs)
    doc = ru_lemmatizer(doc)
    lemmas = [token.lemma_ for token in doc]
    assert lemmas == ["мама", "мыть", "рама"]


@pytest.mark.parametrize(
    "text,lemmas",
    [
        ("гвоздики", ["гвоздик", "гвоздика"]),
        ("люди", ["человек"]),
        ("реки", ["река"]),
        ("кольцо", ["кольцо"]),
        ("пепперони", ["пепперони"]),
    ],
)
def test_ru_lemmatizer_noun_lemmas(ru_lemmatizer, text, lemmas):
    doc = Doc(ru_lemmatizer.vocab, words=[text], pos=["NOUN"])
    result_lemmas = ru_lemmatizer.pymorphy2_lemmatize(doc[0])
    assert sorted(result_lemmas) == lemmas


@pytest.mark.parametrize(
    "text,pos,morph,lemma",
    [
        ("рой", "NOUN", "", "рой"),
        ("рой", "VERB", "", "рыть"),
        ("клей", "NOUN", "", "клей"),
        ("клей", "VERB", "", "клеить"),
        ("три", "NUM", "", "три"),
        ("кос", "NOUN", "Number=Sing", "кос"),
        ("кос", "NOUN", "Number=Plur", "коса"),
        ("кос", "ADJ", "", "косой"),
        ("потом", "NOUN", "", "пот"),
        ("потом", "ADV", "", "потом"),
    ],
)
def test_ru_lemmatizer_works_with_different_pos_homonyms(
    ru_lemmatizer, text, pos, morph, lemma
):
    doc = Doc(ru_lemmatizer.vocab, words=[text], pos=[pos], morphs=[morph])
    result_lemmas = ru_lemmatizer.pymorphy2_lemmatize(doc[0])
    assert result_lemmas == [lemma]


@pytest.mark.parametrize(
    "text,morph,lemma",
    [
        ("гвоздики", "Gender=Fem", "гвоздика"),
        ("гвоздики", "Gender=Masc", "гвоздик"),
        ("вина", "Gender=Fem", "вина"),
        ("вина", "Gender=Neut", "вино"),
    ],
)
def test_ru_lemmatizer_works_with_noun_homonyms(ru_lemmatizer, text, morph, lemma):
    doc = Doc(ru_lemmatizer.vocab, words=[text], pos=["NOUN"], morphs=[morph])
    result_lemmas = ru_lemmatizer.pymorphy2_lemmatize(doc[0])
    assert result_lemmas == [lemma]


def test_ru_lemmatizer_punct(ru_lemmatizer):
    doc = Doc(ru_lemmatizer.vocab, words=["«"], pos=["PUNCT"])
    assert ru_lemmatizer.pymorphy2_lemmatize(doc[0]) == ['"']
    doc = Doc(ru_lemmatizer.vocab, words=["»"], pos=["PUNCT"])
    assert ru_lemmatizer.pymorphy2_lemmatize(doc[0]) == ['"']


def test_ru_doc_lookup_lemmatization(ru_lookup_lemmatizer):
    words = ["мама", "мыла", "раму"]
    pos = ["NOUN", "VERB", "NOUN"]
    morphs = [
        "Animacy=Anim|Case=Nom|Gender=Fem|Number=Sing",
        "Aspect=Imp|Gender=Fem|Mood=Ind|Number=Sing|Tense=Past|VerbForm=Fin|Voice=Act",
        "Animacy=Anim|Case=Acc|Gender=Fem|Number=Sing",
    ]
    doc = Doc(ru_lookup_lemmatizer.vocab, words=words, pos=pos, morphs=morphs)
    doc = ru_lookup_lemmatizer(doc)
    lemmas = [token.lemma_ for token in doc]
    assert lemmas == ["мама", "мыла", "раму"]
