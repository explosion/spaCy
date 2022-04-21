from pprint import pprint

import spacy
from spacy.tokens import Doc, Span

if __name__ == "__main__":
    nlp = spacy.blank("en")
    words = ["c", "d", "e"]
    pos = ["VERB", "NOUN", "NOUN"]
    tags = ["VBP", "NN", "NN"]
    heads = [0, 0, 0]
    deps = ["ROOT", "dobj", "dobj"]
    ents = ["O", "B-ORG", "O"]
    morphs = ["Feat1=A", "Feat1=B", "Feat1=A|Feat2=D"]
    doc = Doc(
        nlp.vocab,
        words=words,
        pos=pos,
        tags=tags,
        heads=heads,
        deps=deps,
        ents=ents,
        morphs=morphs,
    )
    doc.spans["test"] = [Span(doc, 0, 2, "test"), Span(doc, 0, 1, "test")]
    vocab = doc.vocab
    docjson = doc.to_json()
    print(doc.spans)

    #####################################################

    pprint(docjson)
    # todo Fallback for empty doc with len_text == 0.

    words = []
    token_annotations = {
        # For each annotation type: store (1) annotation type required to include it, (2) list of annotations for this
        # type.
        annotation_type: {
            "req": annotation_type if annotation_type != "head" else "dep",
            "values": None,
        }
        for annotation_type in ("tag", "pos", "morph", "lemma", "dep", "head")
    }

    # Gather token-level properties.
    for token in docjson["tokens"]:
        words.append(docjson["text"][token["start"] : token["end"]])
        for annotation_type in token_annotations:
            # Note: how strictly do we want to check this? E. g., do we want to ensure that all tokens have exactly the
            # same attribute or just silently assume this?
            if token_annotations[annotation_type]["req"] in token:
                if token_annotations[annotation_type]["values"] is None:
                    token_annotations[annotation_type]["values"] = []
                token_annotations[annotation_type]["values"].append(
                    token[annotation_type]
                )

    # Create Doc instance.
    new_doc = Doc(
        vocab,
        words=words,
        tags=token_annotations["tag"]["values"],
        pos=token_annotations["pos"]["values"],
        morphs=token_annotations["morph"]["values"],
        lemmas=token_annotations["lemma"]["values"],
        heads=token_annotations["head"]["values"],
        deps=token_annotations["dep"]["values"],
    )

    # Complement other document-level properties.
    new_doc.cats = docjson.get("cats", new_doc.cats)
    for span_group in docjson.get("spans", {}):
        # print([Span(doc=new_doc, **span) for span in docjson["spans"][span_group]])
        new_doc.spans[span_group] = [
            Span(doc=new_doc, **span) for span in docjson["spans"][span_group]
        ]
    if "ents" in docjson:
        new_doc.ents = [
            (ent["label"], ent["start"], ent["end"]) for ent in docjson["ents"]
        ]

    # todo spans -> difference start vs. start_char, end vs end_char?
    print("spans for doc -> json:", docjson["spans"])
    print("spans for doc:", doc.spans)
    spans = [span for span in doc.spans["test"]]
    print("spans for json -> doc:", new_doc.spans)
    print()
