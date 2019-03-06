import spacy


def add_el():
    nlp = spacy.load('en_core_web_sm')
    print("pipes", nlp.pipe_names)

    el_pipe = nlp.create_pipe(name='el')
    nlp.add_pipe(el_pipe, last=True)

    print("pipes", nlp.pipe_names)
    print()

    text = "Australian striker John hits century"
    doc = nlp(text)
    for token in doc:
        print("token", token.text, token.tag_, token.pos_, token.kb_id)


if __name__ == "__main__":
    add_el()
