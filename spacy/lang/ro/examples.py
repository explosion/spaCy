"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.ro import Romanian
>>> from spacy.lang.ro.examples import sentences
>>> nlp = Romanian()
>>> docs = nlp.pipe(sentences)
"""

sentences = [
    "Apple plănuiește să cumpere o companie britanică pentru un miliard de dolari",
    "Municipalitatea din San Francisco ia în calcul interzicerea roboților curieri pe trotuar",
    "Londra este un oraș mare în Regatul Unit",
    "Unde ești?",
    "Cine este președintele Franței?",
    "Care este capitala Statelor Unite?",
    "Când s-a născut Barack Obama?",
]
