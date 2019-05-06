# coding: utf-8
from __future__ import unicode_literals

import spacy

# requires: pip install neuralcoref --no-binary neuralcoref
# import neuralcoref


# TODO
def add_coref():
    """ Add coreference resolution to our model """
    nlp = spacy.load('en_core_web_sm')
    # nlp = spacy.load('en')

    # TODO: this doesn't work yet
    # neuralcoref.add_to_pipe(nlp)
    print("done adding to pipe")

    doc = nlp(u'My sister has a dog. She loves him.')
    print("done doc")

    print(doc._.has_coref)
    print(doc._.coref_clusters)


# TODO
def _run_ner_depr(nlp, clean_text, article_dict):
    doc = nlp(clean_text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":           # TODO: expand to non-persons
            ent_id = article_dict.get(ent.text)
            if ent_id:
                print(" -", ent.text, ent.label_, ent_id)
            else:
                print(" -", ent.text, ent.label_, '???')  # TODO: investigate these cases
