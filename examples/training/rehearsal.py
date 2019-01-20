"""Prevent catastrophic forgetting with rehearsal updates."""
import plac
import random
import srsly
import spacy
from spacy.gold import GoldParse
from spacy.util import minibatch


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

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            random.shuffle(raw_docs)
            losses = {}
            r_losses = {}
            # batch up the examples using spaCy's minibatch
            raw_batches = minibatch(raw_docs, size=batch_size)
            for doc, gold in TRAIN_DATA:
                nlp.update([doc], [gold], sgd=optimizer, drop=dropout, losses=losses)
                raw_batch = list(next(raw_batches))
                nlp.rehearse(raw_batch, sgd=optimizer, losses=r_losses)
            print("Losses", losses)
            print("R. Losses", r_losses)


if __name__ == "__main__":
    plac.call(main)
