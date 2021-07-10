from spacy.lang.en import English


def test_issue8168():
    nlp = English()
    ruler = nlp.add_pipe("entity_ruler")
    patterns = [
        {"label": "ORG", "pattern": "Apple"},
        {
            "label": "GPE",
            "pattern": [{"LOWER": "san"}, {"LOWER": "francisco"}],
            "id": "san-francisco",
        },
        {
            "label": "GPE",
            "pattern": [{"LOWER": "san"}, {"LOWER": "fran"}],
            "id": "san-francisco",
        },
    ]
    ruler.add_patterns(patterns)

    assert ruler._ent_ids == {8043148519967183733: ("GPE", "san-francisco")}
