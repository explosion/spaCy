"""Prevent catastrophic forgetting with rehearsal updates."""
import plac
import random
import warnings
import srsly
import spacy
from spacy.gold import Example
from spacy.util import minibatch, compounding

# TODO: further fix & test this script for v.3 ? (read_gold_data is never called)

LABEL = "ANIMAL"
TRAIN_DATA = [
    (
        "Horses are too tall and they pretend to care about your feelings",
        {"entities": [(0, 6, "ANIMAL")]},
    ),
    ("Do they bite?", {"entities": []}),
    (
        "horses are too tall and they pretend to care about your feelings",
        {"entities": [(0, 6, "ANIMAL")]},
    ),
    ("horses pretend to care about your feelings", {"entities": [(0, 6, "ANIMAL")]}),
    (
        "they pretend to care about your feelings, those horses",
        {"entities": [(48, 54, "ANIMAL")]},
    ),
    ("horses?", {"entities": [(0, 6, "ANIMAL")]}),
]


def read_raw_data(nlp, jsonl_loc):
    for json_obj in srsly.read_jsonl(jsonl_loc):
        if json_obj["text"].strip():
            doc = nlp.make_doc(json_obj["text"])
            yield doc


def read_gold_data(nlp, gold_loc):
    examples = []
    for json_obj in srsly.read_jsonl(gold_loc):
        doc = nlp.make_doc(json_obj["text"])
        ents = [(ent["start"], ent["end"], ent["label"]) for ent in json_obj["spans"]]
        example = Example.from_dict(doc, {"entities": ents})
        examples.append(example)
    return examples


def main(model_name, unlabelled_loc):
    n_iter = 10
    dropout = 0.2
    batch_size = 4
    nlp = spacy.load(model_name)
    nlp.get_pipe("ner").add_label(LABEL)
    raw_docs = list(read_raw_data(nlp, unlabelled_loc))
    optimizer = nlp.resume_training()
    # Avoid use of Adam when resuming training. I don't understand this well
    # yet, but I'm getting weird results from Adam. Try commenting out the
    # nlp.update(), and using Adam -- you'll find the models drift apart.
    # I guess Adam is losing precision, introducing gradient noise?
    optimizer.learn_rate = 0.1
    optimizer.b1 = 0.0
    optimizer.b2 = 0.0
    sizes = compounding(1.0, 4.0, 1.001)

    examples_train_data = []
    for text, annotations in TRAIN_DATA:
        examples_train_data.append(Example.from_dict(nlp.make_doc(text), annotations))

    with nlp.select_pipes(enable="ner") and warnings.catch_warnings():
        # show warnings for misaligned entity spans once
        warnings.filterwarnings("once", category=UserWarning, module="spacy")

        for itn in range(n_iter):
            random.shuffle(examples_train_data)
            random.shuffle(raw_docs)
            losses = {}
            r_losses = {}
            # batch up the examples using spaCy's minibatch
            raw_batches = minibatch(raw_docs, size=4)
            for batch in minibatch(examples_train_data, size=sizes):
                nlp.update(batch, sgd=optimizer, drop=dropout, losses=losses)
                raw_batch = list(next(raw_batches))
                nlp.rehearse(raw_batch, sgd=optimizer, losses=r_losses)
            print("Losses", losses)
            print("R. Losses", r_losses)
    print(nlp.get_pipe("ner").model.unseen_classes)
    test_text = "Do you like horses?"
    doc = nlp(test_text)
    print("Entities in '%s'" % test_text)
    for ent in doc.ents:
        print(ent.label_, ent.text)


if __name__ == "__main__":
    plac.call(main)
