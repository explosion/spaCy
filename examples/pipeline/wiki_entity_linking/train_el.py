# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir

from examples.pipeline.wiki_entity_linking import run_el, training_set_creator, kb_creator
from examples.pipeline.wiki_entity_linking import wikidata_processor as wd

""" TODO: this code needs to be implemented in pipes.pyx"""


def train_model(kb, nlp, training_dir, entity_descr_output, limit=None):
    run_el._prepare_pipeline(nlp, kb)

    correct_entries, incorrect_entries = training_set_creator.read_training_entities(training_output=training_dir,
                                                                                     collect_correct=True,
                                                                                     collect_incorrect=True)

    entities = kb.get_entity_strings()

    id_to_descr = kb_creator._get_id_to_description(entity_descr_output)

    cnt = 0
    for f in listdir(training_dir):
        if not limit or cnt < limit:
            if not run_el.is_dev(f):
                article_id = f.replace(".txt", "")
                if cnt % 500 == 0:
                    print(datetime.datetime.now(), "processed", cnt, "files in the dev dataset")
                cnt += 1
                with open(os.path.join(training_dir, f), mode="r", encoding='utf8') as file:
                    text = file.read()
                    print()
                    doc = nlp(text)
                    doc_vector = doc.vector
                    print("FILE", f, len(doc_vector), "D vector")

                    for mention_pos, entity_pos in correct_entries[article_id].items():
                        descr = id_to_descr.get(entity_pos)
                        if descr:
                            doc_descr = nlp(descr)
                            descr_vector = doc_descr.vector
                            print("GOLD POS", mention_pos, entity_pos, len(descr_vector), "D vector")

                    for mention_neg, entity_negs in incorrect_entries[article_id].items():
                        for entity_neg in entity_negs:
                            descr = id_to_descr.get(entity_neg)
                            if descr:
                                doc_descr = nlp(descr)
                                descr_vector = doc_descr.vector
                                print("GOLD NEG", mention_neg, entity_neg, len(descr_vector), "D vector")

    print()
    print("Processed", cnt, "dev articles")
    print()

