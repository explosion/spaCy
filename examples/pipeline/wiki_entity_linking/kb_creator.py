# coding: utf-8
from __future__ import unicode_literals

import spacy
from spacy.kb import KnowledgeBase

import datetime

from . import wikipedia_processor as wp
from . import wikidata_processor as wd


def create_kb(vocab, max_entities_per_alias, min_occ, entity_output, count_input, prior_prob_input,
              to_print=False, write_entity_defs=True):
    """ Create the knowledge base from Wikidata entries """
    kb = KnowledgeBase(vocab=vocab)

    print()
    print("1. _read_wikidata_entities", datetime.datetime.now())
    print()
    # title_to_id = _read_wikidata_entities_regex_depr(limit=1000)
    title_to_id = wd.read_wikidata_entities_json(limit=None)

    # write the title-ID mapping to file
    if write_entity_defs:
        with open(entity_output, mode='w', encoding='utf8') as entity_file:
            entity_file.write("WP_title" + "|" + "WD_id" + "\n")
            for title, qid in title_to_id.items():
                entity_file.write(title + "|" + str(qid) + "\n")

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


def test_kb(kb):
    # TODO: the vocab objects are now different between nlp and kb - will be fixed when KB is written as part of NLP IO
    nlp = spacy.load('en_core_web_sm')

    el_pipe = nlp.create_pipe(name='entity_linker', config={"kb": kb})
    nlp.add_pipe(el_pipe, last=True)

    candidates = kb.get_candidates("Bush")

    print("generating candidates for 'Bush' :")
    for c in candidates:
        print(" ", c.prior_prob, c.alias_, "-->", c.entity_ + " (freq=" + str(c.entity_freq) + ")")
    print()

    text = "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, " \
           "Douglas reminds us to always bring our towel. " \
           "The main character in Doug's novel is the man Arthur Dent, " \
           "but Douglas doesn't write about George Washington or Homer Simpson."
    doc = nlp(text)

    for ent in doc.ents:
        print("ent", ent.text, ent.label_, ent.kb_id_)
