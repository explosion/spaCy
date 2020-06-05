#!/usr/bin/env python
# coding: utf8
"""Train a convolutional neural network text classifier on the
IMDB dataset, using the TextCategorizer component. The dataset will be loaded
automatically via the package `ml_datasets`. The model is added to
spacy.pipeline, and predictions are available via `doc.cats`. For more details,
see the documentation:
* Training: https://spacy.io/usage/training

Compatible with: spaCy v3.0.0+
"""
from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
from ml_datasets import loaders

import spacy
from spacy import util
from spacy.util import minibatch, compounding
from spacy.gold import Example, GoldParse


@plac.annotations(
    config_path=("Path to config file", "positional", None, Path),
    output_dir=("Optional output directory", "option", "o", Path),
    n_texts=("Number of texts to train from", "option", "t", int),
    n_iter=("Number of training iterations", "option", "n", int),
    init_tok2vec=("Pretrained tok2vec weights", "option", "t2v", Path),
    dataset=("Dataset to train on (default: imdb)", "option", "d", str),
    threshold=("Min. number of instances for a given label (default 20)", "option", "m", int)
)
def main(config_path, output_dir=None, n_iter=20, n_texts=2000, init_tok2vec=None, dataset="imdb", threshold=20):
    if not config_path or not config_path.exists():
        raise ValueError(f"Config file not found at {config_path}")

    spacy.util.fix_random_seed()
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()

    print(f"Loading nlp model from {config_path}")
    nlp_config = util.load_config(config_path, create_objects=False)["nlp"]
    nlp = util.load_model_from_config(nlp_config)

    # ensure the nlp object was defined with a textcat component
    if "textcat" not in nlp.pipe_names:
        raise ValueError(f"The nlp definition in the config does not contain a textcat component")

    textcat = nlp.get_pipe("textcat")

    # load the dataset
    print(f"Loading dataset {dataset} ...")
    (train_texts, train_cats), (dev_texts, dev_cats) = load_data(dataset=dataset, threshold=threshold, limit=n_texts)
    print(
        "Using {} examples ({} training, {} evaluation)".format(
            n_texts, len(train_texts), len(dev_texts)
        )
    )
    train_examples = []
    for text, cats in zip(train_texts, train_cats):
        doc = nlp.make_doc(text)
        gold = GoldParse(doc, cats=cats)
        for cat in cats:
            textcat.add_label(cat)
        ex = Example.from_gold(gold, doc=doc)
        train_examples.append(ex)

    with nlp.select_pipes(enable="textcat"):  # only train textcat
        optimizer = nlp.begin_training()
        if init_tok2vec is not None:
            with init_tok2vec.open("rb") as file_:
                textcat.model.get_ref("tok2vec").from_bytes(file_.read())
        print("Training the model...")
        print("{:^5}\t{:^5}\t{:^5}\t{:^5}".format("LOSS", "P", "R", "F"))
        batch_sizes = compounding(4.0, 32.0, 1.001)
        for i in range(n_iter):
            losses = {}
            # batch up the examples using spaCy's minibatch
            random.shuffle(train_examples)
            batches = minibatch(train_examples, size=batch_sizes)
            for batch in batches:
                nlp.update(batch, sgd=optimizer, drop=0.2, losses=losses)
            with textcat.model.use_params(optimizer.averages):
                # evaluate on the dev data split off in load_data()
                scores = evaluate(nlp.tokenizer, textcat, dev_texts, dev_cats)
            print(
                "{0:.3f}\t{1:.3f}\t{2:.3f}\t{3:.3f}".format(  # print a simple table
                    losses["textcat"],
                    scores["textcat_p"],
                    scores["textcat_r"],
                    scores["textcat_f"],
                )
            )

    # test the trained model (only makes sense for sentiment analysis)
    test_text = "This movie sucked"
    doc = nlp(test_text)
    print(test_text, doc.cats)

    if output_dir is not None:
        with nlp.use_params(optimizer.averages):
            nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        doc2 = nlp2(test_text)
        print(test_text, doc2.cats)


def load_data(dataset, threshold, limit=0, split=0.8):
    """Load data from the provided dataset."""
    # Partition off part of the train data for evaluation
    data_loader = loaders.get(dataset)
    train_data, _ = data_loader(limit=int(limit/split))
    random.shuffle(train_data)
    texts, labels = zip(*train_data)

    unique_labels = set()
    for label_set in labels:
        if isinstance(label_set, int) or isinstance(label_set, str):
            unique_labels.add(label_set)
        elif isinstance(label_set, list) or isinstance(label_set, set):
            unique_labels.update(label_set)
    unique_labels = sorted(unique_labels)
    print("unique_labels", unique_labels)
    print(f"# of unique_labels: {len(unique_labels)}")

    count_values_train = dict()
    for text, annot_list in train_data:
        if isinstance(annot_list, int) or isinstance(annot_list, str):
            count_values_train[annot_list] = count_values_train.get(annot_list, 0) + 1
        else:
            for annot in annot_list:
                count_values_train[annot] = count_values_train.get(annot, 0) + 1
    for value, count in sorted(count_values_train.items(), key=lambda item: item[1]):
        if count < threshold:
            unique_labels.remove(value)

    print(f"# of unique_labels after filtering with threshold {threshold}: {len(unique_labels)}")

    if unique_labels == {0, 1}:
        cats = [{"POSITIVE": bool(y), "NEGATIVE": not bool(y)} for y in labels]
    else:
        cats = []
        for y in labels:
            if isinstance(y, str) or isinstance(y, int):
                cats.append({str(label): (label == y) for label in unique_labels})
            elif isinstance(y, set):
                cats.append({str(label): (label in y) for label in unique_labels})
            else:
                raise ValueError(f"Unrecognised type of labels: {type(y)}")

    split = int(len(train_data) * split)
    return (texts[:split], cats[:split]), (texts[split:], cats[split:])


def evaluate(tokenizer, textcat, texts, cats):
    docs = (tokenizer(text) for text in texts)
    tp = 0.0  # True positives
    fp = 1e-8  # False positives
    fn = 1e-8  # False negatives
    tn = 0.0  # True negatives
    for i, doc in enumerate(textcat.pipe(docs)):
        gold = cats[i]
        for label, score in doc.cats.items():
            if label not in gold:
                continue
            if label == "NEGATIVE":
                continue
            if score >= 0.5 and gold[label] >= 0.5:
                tp += 1.0
            elif score >= 0.5 and gold[label] < 0.5:
                fp += 1.0
            elif score < 0.5 and gold[label] < 0.5:
                tn += 1
            elif score < 0.5 and gold[label] >= 0.5:
                fn += 1
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if (precision + recall) == 0:
        f_score = 0.0
    else:
        f_score = 2 * (precision * recall) / (precision + recall)
    return {"textcat_p": precision, "textcat_r": recall, "textcat_f": f_score}


if __name__ == "__main__":
    plac.call(main)
