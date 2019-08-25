# coding: utf-8
from __future__ import unicode_literals

from bin.wiki_entity_linking.train_descriptions import EntityEncoder
from bin.wiki_entity_linking import wikidata_processor as wd, wikipedia_processor as wp
from spacy.kb import KnowledgeBase

import csv
import datetime


def create_kb(
    nlp,
    max_entities_per_alias,
    min_entity_freq,
    min_occ,
    entity_def_output,
    entity_descr_output,
    count_input,
    prior_prob_input,
    wikidata_input,
    entity_vector_length,
    limit=None,
    read_raw_data=True,
):
    # Create the knowledge base from Wikidata entries
    kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=entity_vector_length)

    # check the length of the nlp vectors
    if "vectors" in nlp.meta and nlp.vocab.vectors.size:
        input_dim = nlp.vocab.vectors_length
        print("Loaded pre-trained vectors of size %s" % input_dim)
    else:
        raise ValueError(
            "The `nlp` object should have access to pre-trained word vectors, "
            " cf. https://spacy.io/usage/models#languages."
        )

    # disable this part of the pipeline when rerunning the KB generation from preprocessed files
    if read_raw_data:
        print()
        print(now(), " * read wikidata entities:")
        title_to_id, id_to_descr = wd.read_wikidata_entities_json(
            wikidata_input, limit=limit
        )

        # write the title-ID and ID-description mappings to file
        _write_entity_files(
            entity_def_output, entity_descr_output, title_to_id, id_to_descr
        )

    else:
        # read the mappings from file
        title_to_id = get_entity_to_id(entity_def_output)
        id_to_descr = get_id_to_description(entity_descr_output)

    print()
    print(now(), " *  get entity frequencies:")
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

    print(len(title_to_id.keys()), "original titles")
    kept_nr = len(filtered_title_to_id.keys())
    print("kept", kept_nr, "entities with min. frequency", min_entity_freq)

    print()
    print(now(), " * train entity encoder:")
    print()
    encoder = EntityEncoder(nlp, input_dim, entity_vector_length)
    encoder.train(description_list=description_list, to_print=True)

    print()
    print(now(), " * get entity embeddings:")
    print()
    embeddings = encoder.apply_encoder(description_list)

    print(now(), " * adding", len(entity_list), "entities")
    kb.set_entities(
        entity_list=entity_list, freq_list=frequency_list, vector_list=embeddings
    )

    alias_cnt = _add_aliases(
        kb,
        title_to_id=filtered_title_to_id,
        max_entities_per_alias=max_entities_per_alias,
        min_occ=min_occ,
        prior_prob_input=prior_prob_input,
    )
    print()
    print(now(), " * adding", alias_cnt, "aliases")
    print()

    print()
    print("# of entities in kb:", kb.get_size_entities())
    print("# of aliases in kb:", kb.get_size_aliases())

    print(now(), "Done with kb")
    return kb


def _write_entity_files(
    entity_def_output, entity_descr_output, title_to_id, id_to_descr
):
    with entity_def_output.open("w", encoding="utf8") as id_file:
        id_file.write("WP_title" + "|" + "WD_id" + "\n")
        for title, qid in title_to_id.items():
            id_file.write(title + "|" + str(qid) + "\n")

    with entity_descr_output.open("w", encoding="utf8") as descr_file:
        descr_file.write("WD_id" + "|" + "description" + "\n")
        for qid, descr in id_to_descr.items():
            descr_file.write(str(qid) + "|" + descr + "\n")


def get_entity_to_id(entity_def_output):
    entity_to_id = dict()
    with entity_def_output.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            entity_to_id[row[0]] = row[1]
    return entity_to_id


def get_id_to_description(entity_descr_output):
    id_to_desc = dict()
    with entity_descr_output.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            id_to_desc[row[0]] = row[1]
    return id_to_desc


def _add_aliases(kb, title_to_id, max_entities_per_alias, min_occ, prior_prob_input):
    wp_titles = title_to_id.keys()
    cnt = 0

    # adding aliases with prior probabilities
    # we can read this file sequentially, it's sorted by alias, and then by count
    with prior_prob_input.open("r", encoding="utf8") as prior_file:
        # skip header
        prior_file.readline()
        line = prior_file.readline()
        previous_alias = None
        total_count = 0
        counts = []
        entities = []
        while line:
            splits = line.replace("\n", "").split(sep="|")
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
                            kb.add_alias(
                                alias=previous_alias,
                                entities=selected_entities,
                                probabilities=prior_probs,
                            )
                            cnt += 1
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
    return cnt


def now():
    return datetime.datetime.now()
