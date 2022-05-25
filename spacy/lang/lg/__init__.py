'''

__init__.py:This defines the defaults and Language subclass
Further we need the following
Punctuation: Punctuation chars(?) for Luganda
Stopwords: Frequent words that appear often in Luganda
Syntax iterators: Functions that compute views of a Doc object based on its syntax, e.g. Noun chunks
Tokenizer exception: Special-case rules for the tokenizer, for example, contractions like “ebye'mizannyo” and abbreviations with punctuation, like “Owek.”.

'''
import spacy
from spacy.language import Language
from stop_words import STOP_WORDS

class LugandaDefaults(Language.Defaults):
    stop_words = STOP_WORDS

@spacy.registry.languages("lg")
class Luganda(Language):
    """docstring for ."""
    lang="lg"
    Defaults=LugandaDefaults
# nlp2 = Luganda()
# print(nlp2.lang, [token.is_stop for token in nlp2("wa ne lwa")])
__all__=["Luganda"]
