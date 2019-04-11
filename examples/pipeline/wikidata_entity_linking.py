# coding: utf-8
from __future__ import unicode_literals

"""Demonstrate how to build a knowledge base from WikiData and run an Entity Linking algorithm.
"""
import json
import spacy
import bz2
from spacy.kb import KnowledgeBase


def create_kb(vocab):
    kb = KnowledgeBase(vocab=vocab)
    _read_wikidata()

    # adding entities
    # kb.add_entity(entity=entity, prob=prob)

    # adding aliases
    # kb.add_alias(alias=alias, entities=[entity_0, entity_1, entity_2], probabilities=[0.6, 0.1, 0.2])

    print()
    print("kb size:", len(kb), kb.get_size_entities(), kb.get_size_aliases())

    return kb


def _read_wikidata():
    """ Read the JSON wiki data """
    # TODO remove hardcoded path

    languages = {'en', 'de'}

    with bz2.open('C:/Users/Sofie/Documents/data/wikidata/wikidata-20190304-all.json.bz2', mode='rb') as file:
        line = file.readline()
        cnt = 1
        while line and cnt < 10:
            clean_line = line.strip()
            if clean_line.endswith(b","):
                clean_line = clean_line[:-1]
            if len(clean_line) > 1:
                obj = json.loads(clean_line)
                unique_id = obj["id"]
                print(unique_id)

                labels = obj["labels"]
                if labels:
                    for lang in languages:
                        lang_label = labels.get(lang, None)
                        if lang_label:
                            print("label (" + lang + "):", lang_label["value"])

                descriptions = obj["descriptions"]
                if descriptions:
                    for lang in languages:
                        lang_descr = descriptions.get(lang, None)
                        if lang_descr:
                            print("description (" + lang + "):", lang_descr["value"])

                aliases = obj["aliases"]
                if aliases:
                    for lang in languages:
                        lang_aliases = aliases.get(lang, None)
                        if lang_aliases:
                            for item in lang_aliases:
                                print("alias (" + lang + "):", item["value"])

                print()
            line = file.readline()
            cnt += 1


def add_el(kb, nlp):
    el_pipe = nlp.create_pipe(name='entity_linker', config={"kb": kb})
    nlp.add_pipe(el_pipe, last=True)

    text = "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, " \
           "Douglas reminds us to always bring our towel. " \
           "The main character in Doug's novel is called Arthur Dent."
    doc = nlp(text)

    print()
    for token in doc:
        print("token", token.text, token.ent_type_, token.ent_kb_id_)

    print()
    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)


if __name__ == "__main__":
    nlp = spacy.load('en_core_web_sm')
    my_kb = create_kb(nlp.vocab)
    # add_el(my_kb, nlp)
