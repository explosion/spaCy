from spacy.kb import KnowledgeBase
from spacy.lang.en import English
from spacy.training import Example


def test_issue7065():
    text = "Kathleen Battle sang in Mahler 's Symphony No. 8 at the Cincinnati Symphony Orchestra 's May Festival."
    nlp = English()
    nlp.add_pipe("sentencizer")
    ruler = nlp.add_pipe("entity_ruler")
    patterns = [{"label": "THING", "pattern": [{"LOWER": "symphony"}, {"LOWER": "no"}, {"LOWER": "."}, {"LOWER": "8"}]}]
    ruler.add_patterns(patterns)

    doc = nlp(text)
    sentences = [s for s in doc.sents]
    assert len(sentences) == 2
    sent0 = sentences[0]
    ent = doc.ents[0]
    assert ent.start < sent0.end < ent.end
    assert sentences.index(ent.sent) == 0


def test_issue7065_b():
    # Test that the NEL doesn't crash when an entity crosses a sentence boundary
    nlp = English()
    vector_length = 3
    nlp.add_pipe("sentencizer")

    text = "Mahler 's Symphony No. 8 was beautiful."
    entities = [(0, 6, "PERSON"), (10, 24, "WORK")]
    links = {(0, 6): {"Q7304": 1.0, "Q270853": 0.0},
             (10, 24): {"Q7304": 0.0, "Q270853": 1.0}}
    sent_starts = [1, -1, 0, 0, 0, 0, 0, 0, 0]
    doc = nlp(text)
    example = Example.from_dict(doc, {"entities": entities, "links": links, "sent_starts": sent_starts})
    train_examples = [example]

    def create_kb(vocab):
        # create artificial KB
        mykb = KnowledgeBase(vocab, entity_vector_length=vector_length)
        mykb.add_entity(entity="Q270853", freq=12, entity_vector=[9, 1, -7])
        mykb.add_alias(
            alias="No. 8",
            entities=["Q270853"],
            probabilities=[1.0],
        )
        mykb.add_entity(entity="Q7304", freq=12, entity_vector=[6, -4, 3])
        mykb.add_alias(
            alias="Mahler",
            entities=["Q7304"],
            probabilities=[1.0],
        )
        return mykb

    # Create the Entity Linker component and add it to the pipeline
    entity_linker = nlp.add_pipe("entity_linker", last=True)
    entity_linker.set_kb(create_kb)

    # train the NEL pipe
    optimizer = nlp.initialize(get_examples=lambda: train_examples)
    for i in range(2):
        losses = {}
        nlp.update(train_examples, sgd=optimizer, losses=losses)

    # Add a custom rule-based component to mimick NER
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "mahler"}]},
        {"label": "WORK", "pattern": [{"LOWER": "symphony"}, {"LOWER": "no"}, {"LOWER": "."}, {"LOWER": "8"}]}
    ]
    ruler = nlp.add_pipe("entity_ruler", before="entity_linker")
    ruler.add_patterns(patterns)

    # test the trained model - this should not throw E148
    doc = nlp(text)
    assert doc
