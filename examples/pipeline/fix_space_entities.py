'''Demonstrate adding a rule-based component that forces some tokens to not
be entities, before the NER tagger is applied. This is used to hotfix the issue
in https://github.com/explosion/spaCy/issues/2870 , present as of spaCy v2.0.16.
'''
import spacy
from spacy.attrs import ENT_IOB

def fix_space_tags(doc):
    ent_iobs = doc.to_array([ENT_IOB])
    for i, token in enumerate(doc):
        if token.is_space:
            # Sets 'O' tag (0 is None, so I is 1, O is 2)
            ent_iobs[i] = 2
    doc.from_array([ENT_IOB], ent_iobs.reshape((len(doc), 1)))
    return doc

def main():
    nlp = spacy.load('en_core_web_sm')
    text = u'''This is some crazy test where I dont need an Apple                Watch to make things bug'''
    doc = nlp(text)
    print('Before', doc.ents)
    nlp.add_pipe(fix_space_tags, name='fix-ner', before='ner')
    doc = nlp(text)
    print('After', doc.ents)

if __name__ == '__main__':
    main()
