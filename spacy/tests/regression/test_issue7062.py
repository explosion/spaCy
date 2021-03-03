from spacy.kb import KnowledgeBase
from spacy.training import Example
from spacy.lang.en import English


# fmt: off
TRAIN_DATA = [
    ("Russ Cochran his reprints include EC Comics.",
        {"links": {(0, 12): {"Q2146908": 1.0}},
         "entities": [(0, 12, "PERSON")],
         "sent_starts": [1, -1, 0, 0, 0, 0, 0, 0]})
]
# fmt: on


def test_partial_links():
    # Test that having some entities on the doc without gold links, doesn't crash
    nlp = English()
    vector_length = 3
    train_examples = []
    for text, annotation in TRAIN_DATA:
        doc = nlp(text)
        train_examples.append(Example.from_dict(doc, annotation))

    def create_kb(vocab):
        # create artificial KB
        mykb = KnowledgeBase(vocab, entity_vector_length=vector_length)
        mykb.add_entity(entity="Q2146908", freq=12, entity_vector=[6, -4, 3])
        mykb.add_alias("Russ Cochran", ["Q2146908"], [0.9])
        return mykb

    # Create and train the Entity Linker
    entity_linker = nlp.add_pipe("entity_linker", last=True)
    entity_linker.set_kb(create_kb)
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(2):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    # adding additional components that are required for the entity_linker
    nlp.add_pipe("sentencizer", first=True)
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "russ"}, {"LOWER": "cochran"}]},
        {"label": "ORG", "pattern": [{"LOWER": "ec"}, {"LOWER": "comics"}]}
    ]
    ruler = nlp.add_pipe("entity_ruler", before="entity_linker")
    ruler.add_patterns(patterns)

    # this will run the pipeline on the examples and shouldn't crash
    results = nlp.evaluate(train_examples)
    assert "PERSON" in results["ents_per_type"]
    assert "PERSON" in results["nel_f_per_type"]
    assert "ORG" in results["ents_per_type"]
    assert "ORG" not in results["nel_f_per_type"]
