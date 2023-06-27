"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.la.examples import sentences
>>> docs = nlp.pipe(sentences)
"""

# > Caes. BG 1.1
# > Cic. De Amic. 1
# > V. Georg. 1.1-5
# > Gen. 1:1
# > Galileo, Sid. Nunc.
# > van Schurman, Opusc. arg. 1

sentences = [
    "Gallia est omnis divisa in partes tres, quarum unam incolunt Belgae, aliam Aquitani, tertiam qui ipsorum lingua Celtae, nostra Galli appellantur.",
    "Q. Mucius augur multa narrare de C. Laelio socero suo memoriter et iucunde solebat nec dubitare illum in omni sermone appellare sapientem.",
    "Quid faciat laetas segetes, quo sidere terram uertere, Maecenas, ulmisque adiungere uitis conueniat, quae cura boum, qui cultus habendo sit pecori, apibus quanta experientia parcis, hinc canere incipiam",
    "In principio creavit Deus caelum et terram.",
    "Quo sumpto, intelligatur lunaris globus, cuius maximus circulus CAF, centrum vero E, dimetiens CF, qui ad Terre diametrum est ut duo ad septem.",
    "Cuicunque natura indita sunt principia, seu potentiae principiorum omnium artium, ac scientiarum, ei conveniunt omnes artes ac scientiae.",
]
