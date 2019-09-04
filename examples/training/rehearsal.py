"""Prevent catastrophic forgetting with rehearsal updates."""
import plac
import random
import srsly
import spacy
from spacy.gold import GoldParse
from spacy.util import minibatch, compounding


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
    docs = []
    golds = []
    for json_obj in srsly.read_jsonl(gold_loc):
        doc = nlp.make_doc(json_obj["text"])
        ents = [(ent["start"], ent["end"], ent["label"]) for ent in json_obj["spans"]]
        gold = GoldParse(doc, entities=ents)
        docs.append(doc)
        golds.append(gold)
    return list(zip(docs, golds))


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
    optimizer.alpha = 0.1
    optimizer.b1 = 0.0
    optimizer.b2 = 0.0

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    sizes = compounding(1.0, 4.0, 1.001)
    with nlp.disable_pipes(*other_pipes):
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            random.shuffle(raw_docs)
            losses = {}
            r_losses = {}
            # batch up the examples using spaCy's minibatch
            raw_batches = minibatch(raw_docs, size=4)
            for batch in minibatch(TRAIN_DATA, size=sizes):
                docs, golds = zip(*batch)
                nlp.update(docs, golds, sgd=optimizer, drop=dropout, losses=losses)
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
