# coding: utf-8
from __future__ import unicode_literals

import spacy
from spacy.kb import KnowledgeBase

import csv
import datetime

from . import wikipedia_processor as wp
from . import wikidata_processor as wd


def create_kb(vocab, max_entities_per_alias, min_occ,
              entity_def_output, entity_descr_output,
              count_input, prior_prob_input,
              to_print=False, write_entity_defs=True):
    """ Create the knowledge base from Wikidata entries """
    kb = KnowledgeBase(vocab=vocab)

    print()
    print("1. _read_wikidata_entities", datetime.datetime.now())
    print()
    title_to_id, id_to_descr = wd.read_wikidata_entities_json(limit=None)

    # write the title-ID and ID-description mappings to file
    if write_entity_defs:
        _write_entity_files(entity_def_output, entity_descr_output, title_to_id, id_to_descr)

    title_list = list(title_to_id.keys())
    entity_list = [title_to_id[x] for x in title_list]

    print()
    print("2. _get_entity_frequencies", datetime.datetime.now())
    print()
    entity_frequencies = wp.get_entity_frequencies(count_input=count_input, entities=title_list)

    print()
    print("3. adding", len(entity_list), "entities", datetime.datetime.now())
    print()
    kb.set_entities(entity_list=entity_list, prob_list=entity_frequencies, vector_list=None, feature_list=None)

    print()
    print("4. adding aliases", datetime.datetime.now())
    print()
    _add_aliases(kb, title_to_id=title_to_id,
                 max_entities_per_alias=max_entities_per_alias, min_occ=min_occ,
                 prior_prob_input=prior_prob_input)

    if to_print:
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


def _get_entity_to_id(entity_def_output):
    entity_to_id = dict()
    with open(entity_def_output, 'r', encoding='utf8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        # skip header
        next(csvreader)
        for row in csvreader:
            entity_to_id[row[0]] = row[1]

    return entity_to_id


def _get_id_to_description(entity_descr_output):
    id_to_desc = dict()
    with open(entity_descr_output, 'r', encoding='utf8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter='|')
        # skip header
        next(csvreader)
        for row in csvreader:
            id_to_desc[row[0]] = row[1]

    return id_to_desc


def _add_aliases(kb, title_to_id, max_entities_per_alias, min_occ, prior_prob_input, to_print=False):
    wp_titles = title_to_id.keys()

    if to_print:
        print("wp titles:", wp_titles)

    # adding aliases with prior probabilities
    with open(prior_prob_input, mode='r', encoding='utf8') as prior_file:
        # skip header
        prior_file.readline()
        line = prior_file.readline()
        # we can read this file sequentially, it's sorted by alias, and then by count
        previous_alias = None
        total_count = 0
        counts = list()
        entities = list()
        while line:
            splits = line.replace('\n', "").split(sep='|')
            new_alias = splits[0]
            count = int(splits[1])
            entity = splits[2]

            if new_alias != previous_alias and previous_alias:
                # done reading the previous alias --> output
                if len(entities) > 0:
                    selected_entities = list()
                    prior_probs = list()
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
                counts = list()
                entities = list()

            total_count += count

            if len(entities) < max_entities_per_alias and count >= min_occ:
                counts.append(count)
                entities.append(entity)
            previous_alias = new_alias

            line = prior_file.readline()

    if to_print:
        print("added", kb.get_size_aliases(), "aliases:", kb.get_alias_strings())

