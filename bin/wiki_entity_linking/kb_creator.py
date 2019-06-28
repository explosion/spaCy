# coding: utf-8
from __future__ import unicode_literals

from .train_descriptions import EntityEncoder
from . import wikidata_processor as wd, wikipedia_processor as wp
from spacy.kb import KnowledgeBase

import csv
import datetime


INPUT_DIM = 300  # dimension of pre-trained input vectors
DESC_WIDTH = 64  # dimension of output entity vectors


def create_kb(nlp, max_entities_per_alias, min_entity_freq, min_occ,
              entity_def_output, entity_descr_output,
              count_input, prior_prob_input, wikidata_input):
    # Create the knowledge base from Wikidata entries
    kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=DESC_WIDTH)

    # disable this part of the pipeline when rerunning the KB generation from preprocessed files
    read_raw_data = True

    if read_raw_data:
        print()
        print(" * _read_wikidata_entities", datetime.datetime.now())
        title_to_id, id_to_descr = wd.read_wikidata_entities_json(wikidata_input)

        # write the title-ID and ID-description mappings to file
        _write_entity_files(entity_def_output, entity_descr_output, title_to_id, id_to_descr)

    else:
        # read the mappings from file
        title_to_id = get_entity_to_id(entity_def_output)
        id_to_descr = get_id_to_description(entity_descr_output)

    print()
    print(" * _get_entity_frequencies", datetime.datetime.now())
    print()
    entity_frequencies = wp.get_all_frequencies(count_input=count_input)

    # filter the entities for in the KB by frequency, because there's just too much data (8M entities) otherwise
    filtered_title_to_id = dict()
    entity_list = []
    description_list = []
    frequency_list = []
    for title, entity in title_to_id.items():
        freq = entity_frequencies.get(title, 0)
        desc = id_to_descr.get(entity, None)
        if desc and freq > min_entity_freq:
            entity_list.append(entity)
            description_list.append(desc)
            frequency_list.append(freq)
            filtered_title_to_id[title] = entity

    print("Kept", len(filtered_title_to_id.keys()), "out of", len(title_to_id.keys()),
          "titles with filter frequency", min_entity_freq)

    print()
    print(" * train entity encoder", datetime.datetime.now())
    print()
    encoder = EntityEncoder(nlp, INPUT_DIM, DESC_WIDTH)
    encoder.train(description_list=description_list, to_print=True)

    print()
    print(" * get entity embeddings", datetime.datetime.now())
    print()
    embeddings = encoder.apply_encoder(description_list)

    print()
    print(" * adding", len(entity_list), "entities", datetime.datetime.now())
    kb.set_entities(entity_list=entity_list, prob_list=frequency_list, vector_list=embeddings)

    print()
    print(" * adding aliases", datetime.datetime.now())
    print()
    _add_aliases(kb, title_to_id=filtered_title_to_id,
                 max_entities_per_alias=max_entities_per_alias, min_occ=min_occ,
                 prior_prob_input=prior_prob_input)

    print()
    print("kb size:", len(kb), kb.get_size_entities(), kb.get_size_aliases())

    print("done with kb", datetime.datetime.now())
    return kb


def _write_entity_files(entity_def_output, entity_descr_output, title_to_id, id_to_descr):
    with open(entity_def_output, mode='w', encoding='utf8') as id_file:
        id_file.write("WP_title" + "|" + "WD_id" + "\n")
        for title, qid in title_to_id.items():
            id_file.write(title + "|" + str(qid) + "\n")

    with open(entity_descr_output, mode='w', encoding='utf8') as descr_file:
        descr_file.write("WD_id" + "|" + "description" + "\n")
        for qid, descr in id_to_descr.items():
            descr_file.write(str(qid) + "|" + descr + "\n")


def get_entity_to_id(entity_def_output):
    entity_to_id = dict()
    with open(entity_def_output, 'r', encoding='utf8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        # skip header
        next(csvreader)
        for row in csvreader:
            entity_to_id[row[0]] = row[1]
    return entity_to_id


def get_id_to_description(entity_descr_output):
    id_to_desc = dict()
    with open(entity_descr_output, 'r', encoding='utf8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        # skip header
        next(csvreader)
        for row in csvreader:
            id_to_desc[row[0]] = row[1]
    return id_to_desc


def _add_aliases(kb, title_to_id, max_entities_per_alias, min_occ, prior_prob_input):
    wp_titles = title_to_id.keys()

    # adding aliases with prior probabilities
    # we can read this file sequentially, it's sorted by alias, and then by count
    with open(prior_prob_input, mode='r', encoding='utf8') as prior_file:
        # skip header
        prior_file.readline()
        line = prior_file.readline()
        previous_alias = None
        total_count = 0
        counts = []
        entities = []
        while line:
            splits = line.replace('\n', "").split(sep='|')
            new_alias = splits[0]
            count = int(splits[1])
            entity = splits[2]

            if new_alias != previous_alias and previous_alias:
                # done reading the previous alias --> output
                if len(entities) > 0:
                    selected_entities = []
                    prior_probs = []
                    for ent_count, ent_string in zip(counts, entities):
                        if ent_string in wp_titles:
                            wd_id = title_to_id[ent_string]
                            p_entity_givenalias = ent_count / total_count
                            selected_entities.append(wd_id)
                            prior_probs.append(p_entity_givenalias)

                    if selected_entities:
                        try:
                            kb.add_alias(alias=previous_alias, entities=selected_entities, probabilities=prior_probs)
                        except ValueError as e:
                            print(e)
                total_count = 0
                counts = []
                entities = []

            total_count += count

            if len(entities) < max_entities_per_alias and count >= min_occ:
                counts.append(count)
                entities.append(entity)
            previous_alias = new_alias

            line = prior_file.readline()

