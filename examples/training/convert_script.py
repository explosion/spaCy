import json
import srsly

from examples.training.train_textcat import load_data

from spacy.gold import docs_to_json, GoldCorpus
from spacy import blank
from pathlib import Path

def write(dataset):
    nlp = blank("en")
    nlp.add_pipe(nlp.create_pipe("sentencizer"))

    threshold = 0
    n_texts = 2000
    (train_texts, train_cats), (dev_texts, dev_cats) = load_data(dataset=dataset, threshold=threshold, limit=n_texts)

    train_docs = []
    for text, cats in zip(train_texts, train_cats):
        doc = nlp(text)
        doc.cats = cats
        train_docs.append(doc)

    dev_docs = []
    for text, cats in zip(dev_texts, dev_cats):
        doc = nlp(text)
        doc.cats = cats
        dev_docs.append(doc)

    json_train = docs_to_json(train_docs)
    json_dev = docs_to_json(dev_docs)

    train_file = Path(f'{dataset}_train_2000.json')
    srsly.write_json(train_file, [json_train])

    dev_file = Path(f'{dataset}_dev_2000.json')
    srsly.write_json(dev_file, [json_dev])


def read(dataset):
    train_file = Path(f'{dataset}_train_2000.json')
    dev_file = Path(f'{dataset}_dev_2000.json')
    return GoldCorpus(train=str(train_file), dev=str(dev_file))


if __name__ == "__main__":
    dataset = "imdb"
    # dataset = "dbpedia"
    # dataset = "cmu"

    write(dataset)
    gold = read(dataset)
    print("train:", len(list(gold.dev_examples)))
    print("dev:", len(list(gold.dev_examples)))