# coding: utf-8
from __future__ import unicode_literals

"""Demonstrate how to build a simple knowledge base and run an Entity Linking algorithm.
Currently still a bit of a dummy algorithm: taking simply the entity with highest probability for a given alias
"""
import spacy
from spacy.kb import KnowledgeBase


def create_kb(vocab):
    kb = KnowledgeBase(vocab=vocab, entity_vector_length=1)

    # adding entities
    entity_0 = "Q1004791_Douglas"
    print("adding entity", entity_0)
    kb.add_entity(entity=entity_0, freq=0.5, entity_vector=[0])

    entity_1 = "Q42_Douglas_Adams"
    print("adding entity", entity_1)
    kb.add_entity(entity=entity_1, freq=0.5, entity_vector=[1])

    entity_2 = "Q5301561_Douglas_Haig"
    print("adding entity", entity_2)
    kb.add_entity(entity=entity_2, freq=0.5, entity_vector=[2])

    # adding aliases
    print()
    alias_0 = "Douglas"
    print("adding alias", alias_0)
    kb.add_alias(alias=alias_0, entities=[entity_0, entity_1, entity_2], probabilities=[0.6, 0.1, 0.2])

    alias_1 = "Douglas Adams"
    print("adding alias", alias_1)
    kb.add_alias(alias=alias_1, entities=[entity_1], probabilities=[0.9])

    print()
    print("kb size:", len(kb), kb.get_size_entities(), kb.get_size_aliases())

    return kb


def add_el(kb, nlp):
    el_pipe = nlp.create_pipe(name='entity_linker', config={"context_width": 64})
    el_pipe.set_kb(kb)
    nlp.add_pipe(el_pipe, last=True)
    nlp.begin_training()
    el_pipe.context_weight = 0
    el_pipe.prior_weight = 1

    for alias in ["Douglas Adams", "Douglas"]:
        candidates = nlp.linker.kb.get_candidates(alias)
        print()
        print(len(candidates), "candidate(s) for", alias, ":")
        for c in candidates:
            print(" ", c.entity_, c.prior_prob)

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
    my_nlp = spacy.load('en_core_web_sm')
    my_kb = create_kb(my_nlp.vocab)
    add_el(my_kb, my_nlp)
