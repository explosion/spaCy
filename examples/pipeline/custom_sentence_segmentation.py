'''Example of adding a pipeline component to prohibit sentence boundaries
before certain tokens.

What we do is write to the token.is_sent_start attribute, which
takes values in {True, False, None}. The default value None allows the parser
to predict sentence segments. The value False prohibits the parser from inserting
a sentence boundary before that token. Note that fixing the sentence segmentation
should also improve the parse quality.

The specific example here is drawn from https://github.com/explosion/spaCy/issues/2627
Other versions of the model may not make the original mistake, so the specific
example might not be apt for future versions.
'''
import plac
import spacy

def prevent_sentence_boundaries(doc):
    for token in doc:
        if not can_be_sentence_start(token):
            token.is_sent_start = False
    return doc

def can_be_sentence_start(token):
    if token.i == 0:
        return True
    elif token.is_title:
        return True
    elif token.nbor(-1).is_punct:
        return True
    elif token.nbor(-1).is_space:
        return True
    else:
        return False

def main():
    nlp = spacy.load('en_core_web_lg')
    raw_text = "Been here and I'm loving it."
    doc = nlp(raw_text)
    sentences = [sent.string.strip() for sent in doc.sents]
    print(sentences)
    nlp.add_pipe(prevent_sentence_boundaries, before='parser')
    doc = nlp(raw_text)
    sentences = [sent.string.strip() for sent in doc.sents]
    print(sentences)
 
    
if __name__ == '__main__':
    plac.call(main)
