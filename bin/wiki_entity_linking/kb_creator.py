# coding: utf-8
from __future__ import unicode_literals

import logging

from spacy.kb import KnowledgeBase

from bin.wiki_entity_linking import wikipedia_processor as wp
from bin.wiki_entity_linking.train_descriptions import EntityEncoder
from bin.wiki_entity_linking import wiki_io as io


logger = logging.getLogger(__name__)


def create_kb(
    nlp,
    max_entities_per_alias,
    min_entity_freq,
    min_occ,
    entity_def_path,
    entity_descr_path,
    entity_alias_path,
    entity_freq_path,
    prior_prob_path,
    entity_vector_length,
):
    # Create the knowledge base from Wikidata entries
    kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=entity_vector_length)

    # read the mappings from file
    title_to_id = io.read_title_to_id(entity_def_path)
    id_to_descr = io.read_id_to_descr(entity_descr_path)
    id_to_alias = io.read_id_to_alias(entity_alias_path)

    # check the length of the nlp vectors
    if "vectors" in nlp.meta and nlp.vocab.vectors.size:
        input_dim = nlp.vocab.vectors_length
        logger.info("Loaded pre-trained vectors of size %s" % input_dim)
    else:
        raise ValueError(
            "The `nlp` object should have access to pre-trained word vectors, "
            " cf. https://spacy.io/usage/models#languages."
        )

    logger.info("Filtering entities with fewer than {} mentions".format(min_entity_freq))
    entity_frequencies = io.read_entity_to_count(entity_freq_path)
    # filter the entities for in the KB by frequency, because there's just too much data (8M entities) otherwise
    filtered_title_to_id, entity_list, description_list, frequency_list = get_filtered_entities(
        title_to_id,
        id_to_descr,
        entity_frequencies,
        min_entity_freq
    )
    logger.info("Kept {} entities from the set of {}".format(len(description_list), len(title_to_id.keys())))

    logger.info("Training entity encoder")
    encoder = EntityEncoder(nlp, input_dim, entity_vector_length)
    encoder.train(description_list=description_list, to_print=True)

    logger.info("Getting entity embeddings")
    embeddings = encoder.apply_encoder(description_list)

    logger.info("Adding {} entities".format(len(entity_list)))
    kb.set_entities(
        entity_list=entity_list, freq_list=frequency_list, vector_list=embeddings
    )

    logger.info("Adding aliases from Wikipedia and Wikidata")
    _add_aliases(
        kb,
        entity_list=entity_list,
        title_to_id=filtered_title_to_id,
        max_entities_per_alias=max_entities_per_alias,
        min_occ=min_occ,
        prior_prob_path=prior_prob_path,
        id_to_alias=id_to_alias
    )

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


def _add_aliases(kb, entity_list, title_to_id, max_entities_per_alias, min_occ, prior_prob_path, id_to_alias):
    # We have aliases+prior probs from Wikipedia
    wp_titles = title_to_id.keys()

    # We have aliases from Wikidata without prior probabilities
    alias_to_ids = dict()

    for qid, alias_list in id_to_alias.items():
        for alias in alias_list:
            q_list = alias_to_ids.get(alias, [])
            if qid in entity_list:
                q_list.append(qid)
                alias_to_ids[alias] = q_list

    # adding aliases with prior probabilities
    # we can read this file sequentially, it's sorted by alias, and then by count
    with prior_prob_path.open("r", encoding="utf8") as prior_file:
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
                            # We try adding aliases from Wikidata, for which we have no prior probabilities.
                            # We "fill up" the remaining % of the prior probability to sum up to 100,
                            # but cap at 10% prior probability. This is kind of an artificial trick,
                            # but better than not having the WD aliases at all.
                            perc_left = 1 - sum(prior_probs)
                            wd_qids = alias_to_ids.get(previous_alias, [])
                            wd_entities = []
                            for qid in wd_qids:
                                if qid not in selected_entities:
                                    wd_entities.append(qid)
                            wd_priors = [min(perc_left/len(wd_entities), 0.1)] * len(wd_entities) if wd_entities else []

                            # merge the two
                            selected_entities.extend(wd_entities)
                            prior_probs.extend(wd_priors)

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

    # when we're done, add WD aliases that we haven't encountered before
    for alias, q_list in alias_to_ids.items():
        if not kb.contains_alias(alias):
            prior_list = [1 / len(q_list)] * len(q_list)
            kb.add_alias(
                alias=alias,
                entities=q_list,
                probabilities=prior_list,
            )


def read_kb(nlp, kb_file):
    kb = KnowledgeBase(vocab=nlp.vocab)
    kb.load_bulk(kb_file)
    return kb
