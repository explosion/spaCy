import spacy
from spacy.kb import KnowledgeBase


def create_kb():
    mykb = KnowledgeBase()
    print("kb size", len(mykb))

    # adding entities
    entity_42 = "Q42"   # douglas adams
    mykb.add_entity(entity_id=entity_42, prob=0.5)
    print("adding entity", entity_42)

    entity_5301561 = "Q5301561"
    mykb.add_entity(entity_id=entity_5301561, prob=0.5)
    print("adding entity", entity_5301561)

    print("kb size", len(mykb))

    # adding aliases
    alias = "douglas"
    print("adding alias", alias)
    mykb.add_alias(alias=alias, entities=["Q42", "Q5301561"], probabilities=[0.8, 0.2])
    print("kb size", len(mykb))

    print("aliases for", alias)
    mykb.get_candidates(alias)


def add_el():
    nlp = spacy.load('en_core_web_sm')
    print("pipes before:", nlp.pipe_names)

    el_pipe = nlp.create_pipe(name='el')
    nlp.add_pipe(el_pipe, last=True)

    print("pipes after:", nlp.pipe_names)
    print()

    text = "The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, reminds us to always bring our towel."
    doc = nlp(text)

    for token in doc:
        print("token", token.text, token.ent_type_, token.ent_kb_id_)

    print()
    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)


if __name__ == "__main__":
    # add_el()
    create_kb()
