import spacy
import spacy.lang.en
from spacy.pipeline import TextCategorizer

def test_bytes_serialize_issue_1105():
    nlp = spacy.lang.en.English()
    tokenizer = nlp.tokenizer
    textcat = TextCategorizer(tokenizer.vocab, labels=['ENTITY', 'ACTION', 'MODIFIER'])
    textcat_bytes = textcat.to_bytes()
