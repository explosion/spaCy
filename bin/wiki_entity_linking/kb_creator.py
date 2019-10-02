# coding: utf-8
from __future__ import unicode_literals

import csv
import logging
import spacy
import sys

from spacy.kb import KnowledgeBase

from bin.wiki_entity_linking import wikipedia_processor as wp
from bin.wiki_entity_linking.train_descriptions import EntityEncoder

csv.field_size_limit(sys.maxsize)


logger = logging.getLogger(__name__)


def create_kb(
    nlp,
    max_entities_per_alias,
    min_entity_freq,
    min_occ,
    entity_def_input,
    entity_descr_path,
    count_input,
    prior_prob_input,
    entity_vector_length,
):
    # Create the knowledge base from Wikidata entries
    kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=entity_vector_length)

    # read the mappings from file
    title_to_id = get_entity_to_id(entity_def_input)
    id_to_descr = get_id_to_description(entity_descr_path)

    # check the length of the nlp vectors
    if "vectors" in nlp.meta and nlp.vocab.vectors.size:
        input_dim = nlp.vocab.vectors_length
        logger.info("Loaded pretrained vectors of size %s" % input_dim)
    else:
        raise ValueError(
            "The `nlp` object should have access to pretrained word vectors, "
            " cf. https://spacy.io/usage/models#languages."
        )

    logger.info("Get entity frequencies")
    entity_frequencies = wp.get_all_frequencies(count_input=count_input)

    logger.info("Filtering entities with fewer than {} mentions".format(min_entity_freq))
    # filter the entities for in the KB by frequency, because there's just too much data (8M entities) otherwise
    filtered_title_to_id, entity_list, description_list, frequency_list = get_filtered_entities(
        title_to_id,
        id_to_descr,
        entity_frequencies,
        min_entity_freq
    )
    logger.info("Left with {} entities".format(len(description_list)))

    logger.info("Train entity encoder")
    encoder = EntityEncoder(nlp, input_dim, entity_vector_length)
    encoder.train(description_list=description_list, to_print=True)

    logger.info("Get entity embeddings:")
    embeddings = encoder.apply_encoder(description_list)

    logger.info("Adding {} entities".format(len(entity_list)))
    kb.set_entities(
        entity_list=entity_list, freq_list=frequency_list, vector_list=embeddings
    )

    logger.info("Adding aliases")
    _add_aliases(
        kb,
        title_to_id=filtered_title_to_id,
        max_entities_per_alias=max_entities_per_alias,
        min_occ=min_occ,
        prior_prob_input=prior_prob_input,
    )

    logger.info("KB size: {} entities, {} aliases".format(
        kb.get_size_entities(),
        kb.get_size_aliases()))

    logger.info("Done with kb")
    return kb


def get_filtered_entities(title_to_id, id_to_descr, entity_frequencies,
                          min_entity_freq: int = 10):
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
    return filtered_title_to_id, entity_list, description_list, frequency_list


def get_entity_to_id(entity_def_output):
    entity_to_id = dict()
    with entity_def_output.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            entity_to_id[row[0]] = row[1]
    return entity_to_id


def get_id_to_description(entity_descr_path):
    id_to_desc = dict()
    with entity_descr_path.open("r", encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile, delimiter="|")
        # skip header
        next(csvreader)
        for row in csvreader:
            id_to_desc[row[0]] = row[1]
    return id_to_desc


def _add_aliases(kb, title_to_id, max_entities_per_alias, min_occ, prior_prob_input):
    wp_titles = title_to_id.keys()

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
                        except ValueError as e:
                            logger.error(e)
                total_count = 0
                counts = []
                entities = []

            total_count += count

            if len(entities) < max_entities_per_alias and count >= min_occ:
                counts.append(count)
                entities.append(entity)
            previous_alias = new_alias

            line = prior_file.readline()


def read_nlp_kb(model_dir, kb_file):
    nlp = spacy.load(model_dir)
    kb = KnowledgeBase(vocab=nlp.vocab)
    kb.load_bulk(kb_file)
    logger.info("kb entities: {}".format(kb.get_size_entities()))
    logger.info("kb aliases: {}".format(kb.get_size_aliases()))
    return nlp, kb
