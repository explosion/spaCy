"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.sr.examples import sentences
>>> docs = nlp.pipe(sentences)
"""

sentences = [
    # Translations from English
    "Apple планира куповину америчког стартапа за $1 милијарду.",
    "Беспилотни аутомобили пребацују одговорност осигурања на произвођаче.",
    "Лондон је велики град у Уједињеном Краљевству.",
    "Где си ти?",
    "Ко је председник Француске?",
    # Serbian common and slang
    "Moj ћале је инжењер!",
    "Новак Ђоковић је најбољи тенисер света.",
    "У Пироту има добрих кафана!",
    "Музеј Николе Тесле се налази у Београду.",
]
