import spacy


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
    add_el()
