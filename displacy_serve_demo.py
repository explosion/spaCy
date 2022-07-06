import spacy
from spacy.displacy.render import DEFAULT_LABEL_COLORS
from spacy import displacy

d = {
    "id": "691_batch_2",
    "text": 'Sen. Mazie Hirono, D-Hawaii, the dumbest person in the U.S. Capitol*, \
questions Judge Amy Coney Barrett, the smartest person, \
during Confirmation hearings this week.\n\n* Normally, \
the "dumbest" designation goes to Rep. Maxine Waters, \
D-Calif., but Ms. Waters was not present in the building.\n',
    "labels": [
        {
            "start": 0,
            "end": 67,
            "technique": "Smears",
            "text_fragment": "Sen. Mazie Hirono, D-Hawaii, the dumbest person in the U.S. Capitol",
        },
        {
            "start": 29,
            "end": 47,
            "technique": "Loaded",
            "text_fragment": "the dumbest person",
        },
        {
            "start": 29,
            "end": 47,
            "technique": "ExMin",
            "text_fragment": "the dumbest person",
        },
        # The next entry defines a span that becomes broken by displacy:
        {
            "start": 29,
            "end": 67,
            "technique": "NameCall",
            "text_fragment": "the dumbest person in the U.S. Capitol",
        },
        {
            "start": 80,
            "end": 124,
            "technique": "Virtue",
            "text_fragment": "Judge Amy Coney Barrett, the smartest person",
        },
        {
            "start": 105,
            "end": 124,
            "technique": "NameCall",
            "text_fragment": "the smartest person",
        },
        {
            "start": 105,
            "end": 124,
            "technique": "ExMin",
            "text_fragment": "the smartest person",
        },
        {
            "start": 179,
            "end": 204,
            "technique": "ExMin",
            "text_fragment": 'the "dumbest" designation',
        },
        # The next entry defines a span that becomes broken by displacy:
        {
            "start": 179,
            "end": 241,
            "technique": "Smears",
            "text_fragment": 'the "dumbest" designation goes to Rep. Maxine Waters, D-Calif.',
        },
        {"start": 183, "end": 192, "technique": "Loaded", "text_fragment": '"dumbest"'},
    ],
}


def span_encode(nlp, d, spans_key="sc"):
    """Create a `Doc` object with spans from data"""
    text = d["text"]
    doc = nlp(text)
    span_list = []
    for l in d["labels"]:
        start = l["start"]
        end = l["end"]
        label = l["technique"]
        span = doc.char_span(start, end, label=label)
        span_list.append(span)
    doc.spans[spans_key] = span_list
    return doc


def main():
    spans_key = "mnp"
    nlp = spacy.load("en_core_web_sm")

    doc = span_encode(nlp, d, spans_key=spans_key)

    techniques = ["Smears", "Loaded", "ExMin", "Virtue", "NameCall"]

    # We take the default label colours and attribute them to our labels
    colours = list(DEFAULT_LABEL_COLORS.values())
    colour_dict = {}
    for i, t in enumerate(techniques):
        colour_dict[t] = colours[i]

    options = {"spans_key": spans_key, "colors": colour_dict}

    displacy.serve(doc, style="span", options=options, port=12345)


if __name__ == "__main__":
    main()
