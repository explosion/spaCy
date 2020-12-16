# coding: utf-8
"""
Example of loading previously parsed text using spaCy's DocBin class. The example
performs an entity count to show that the annotations are available.
For more details, see https://spacy.io/usage/saving-loading#docs
Installation:
python -m spacy download en_core_web_lg
Usage:
python examples/load_from_docbin.py en_core_web_lg RC_2015-03-9.spacy
"""
from __future__ import unicode_literals

import spacy
from spacy.tokens import DocBin
from timeit import default_timer as timer
from collections import Counter

EXAMPLE_PARSES_PATH = "RC_2015-03-9.spacy"


def main(model="en_core_web_lg", docbin_path=EXAMPLE_PARSES_PATH):
    nlp = spacy.load(model)
    print("Reading data from {}".format(docbin_path))
    with open(docbin_path, "rb") as file_:
        bytes_data = file_.read()
    nr_word = 0
    start_time = timer()
    entities = Counter()
    docbin = DocBin().from_bytes(bytes_data)
    for doc in docbin.get_docs(nlp.vocab):
        nr_word += len(doc)
        entities.update((e.label_, e.text) for e in doc.ents)
    end_time = timer()
    msg = "Loaded {nr_word} words in {seconds} seconds ({wps} words per second)"
    wps = nr_word / (end_time - start_time)
    print(msg.format(nr_word=nr_word, seconds=end_time - start_time, wps=wps))
    print("Most common entities:")
    for (label, entity), freq in entities.most_common(30):
        print(freq, entity, label)


if __name__ == "__main__":
    import plac

    plac.call(main)
