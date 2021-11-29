import pytest


@pytest.mark.parametrize(
    "text",
    [
        "aujourd'hui",
        "Aujourd'hui",
        "prud'hommes",
        "prud’hommal",
        "audio-numérique",
        "Audio-numérique",
        "entr'amis",
        "entr'abat",
        "rentr'ouvertes",
        "grand'hamien",
        "Châteauneuf-la-Forêt",
        "Château-Guibert",
        "refox-trottâmes",
        # u"K-POP",
        # u"K-Pop",
        # u"K-pop",
        "z'yeutes",
        "black-outeront",
        "états-unienne",
        "courtes-pattes",
        "court-pattes",
        "saut-de-ski",
        "Écourt-Saint-Quentin",
        "Bout-de-l'Îlien",
        "pet-en-l'air",
    ],
)
def test_fr_tokenizer_infix_exceptions(fr_tokenizer, text):
    tokens = fr_tokenizer(text)
    assert len(tokens) == 1


@pytest.mark.parametrize("text", ["janv.", "juill.", "Dr.", "av.", "sept."])
def test_fr_tokenizer_handles_abbr(fr_tokenizer, text):
    tokens = fr_tokenizer(text)
    assert len(tokens) == 1


def test_fr_tokenizer_handles_exc_in_text(fr_tokenizer):
    text = "Je suis allé au mois de janv. aux prud’hommes."
    tokens = fr_tokenizer(text)
    assert len(tokens) == 10
    assert tokens[6].text == "janv."
    assert tokens[8].text == "prud’hommes"


def test_fr_tokenizer_handles_exc_in_text_2(fr_tokenizer):
    text = "Cette après-midi, je suis allé dans un restaurant italo-mexicain."
    tokens = fr_tokenizer(text)
    assert len(tokens) == 11
    assert tokens[1].text == "après-midi"
    assert tokens[9].text == "italo-mexicain"


def test_fr_tokenizer_handles_title(fr_tokenizer):
    text = "N'est-ce pas génial?"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 6
    assert tokens[0].text == "N'"
    assert tokens[1].text == "est"
    assert tokens[2].text == "-ce"


def test_fr_tokenizer_handles_title_2(fr_tokenizer):
    text = "Est-ce pas génial?"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 5
    assert tokens[0].text == "Est"
    assert tokens[1].text == "-ce"


def test_fr_tokenizer_handles_title_3(fr_tokenizer):
    text = "Qu'est-ce que tu fais?"
    tokens = fr_tokenizer(text)
    assert len(tokens) == 7
    assert tokens[0].text == "Qu'"
