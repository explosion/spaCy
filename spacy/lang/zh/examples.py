"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.zh.examples import sentences
>>> docs = nlp.pipe(sentences)
"""

# from https://zh.wikipedia.org/wiki/汉语
sentences = [
    "作为语言而言，为世界使用人数最多的语言，目前世界有五分之一人口做为母语。",
    "汉语有多种分支，当中官话最为流行，为中华人民共和国的国家通用语言（又称为普通话）、以及中华民国的国语。",
    "此外，中文还是联合国正式语文，并被上海合作组织等国际组织采用为官方语言。",
    "在中国大陆，汉语通称为“汉语”。",
    "在联合国、台湾、香港及澳门，通称为“中文”。",
    "在新加坡及马来西亚，通称为“华语”。",
]
