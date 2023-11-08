"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.nn.examples import sentences
>>> docs = nlp.pipe(sentences)
"""


# sentences taken from Omsetjingsminne frå Nynorsk pressekontor 2022 (https://www.nb.no/sprakbanken/en/resource-catalogue/oai-nb-no-sbr-80/)
sentences = [
    "Konseptet går ut på at alle tre omgangar tel, alle hopparar må stille i kvalifiseringa og poengsummen skal telje.",
    "Det er ein meir enn i same periode i fjor.",
    "Det har lava ned enorme snømengder i store delar av Europa den siste tida.",
    "Akhtar Chaudhry er ikkje innstilt på Oslo-lista til SV, men utfordrar Heikki Holmås om førsteplassen.",
]
