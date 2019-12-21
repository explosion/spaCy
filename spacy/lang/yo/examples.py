# coding: utf8
from __future__ import unicode_literals


"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.yo.examples import sentences
>>> docs = nlp.pipe(sentences)
"""

# 1. https://yo.wikipedia.org/wiki/Wikipedia:%C3%80y%E1%BB%8Dk%C3%A0_p%C3%A0t%C3%A0k%C3%AC
# 2.https://yo.wikipedia.org/wiki/Oj%C3%BAew%C3%A9_%C3%80k%E1%BB%8D%CC%81k%E1%BB%8D%CC%81
# 3. https://www.bbc.com/yoruba

sentences = [
    "Ìjọba Tanzania fi Ajìjàgbara Ọmọ Orílẹ̀-èdèe Uganda sí àtìmọ́lé",
    "Olúṣẹ́gun Ọbásanjọ́, tí ó jẹ́ Ààrẹ ìjọba ológun àná (láti ọdún 1976 sí 1979), tí ó sì tún ṣe  Ààrẹ ìjọba alágbádá tí ìbò gbé wọlé (ní ọdún 1999 sí 2007), kúndùn láti máa bu ẹnu àtẹ́ lu àwọn "
    "ètò ìjọba Ààrẹ orílẹ̀-èdè Nàìjíríà tí ó jẹ tẹ̀lé e.",
    "Akin Alabi rán ẹnu mọ́ agbárá Adárí Òsìsẹ̀, àwọn ọmọ Nàìjíríà dẹnu bò ó",
    "Ta ló leè dúró s'ẹ́gbẹ̀ẹ́ Okunnu láì rẹ́rìín?",
    "Dídarapọ̀ mọ́n ìpolongo",
    "Bi a se n so, omobinrin ni oruko ni ojo kejo bee naa ni omokunrin ni oruko ni ojo kesan.",
    "Oríṣìíríṣìí nǹkan ló le yọrí sí orúkọ tí a sọ ọmọ",
    "Gbogbo won ni won ni oriki ti won",
]
