# coding: utf-8
"""Script to process Wikipedia and Wikidata dumps and create a knowledge base (KB)
with specific parameters. Intermediate files are written to disk.

Running the full pipeline on a standard laptop, may take up to 13 hours of processing.
Use the -p, -d and -s options to speed up processing using the intermediate files
from a previous run.

For the Wikidata dump: get the latest-all.json.bz2 from https://dumps.wikimedia.org/wikidatawiki/entities/
For the Wikipedia dump: get enwiki-latest-pages-articles-multistream.xml.bz2
from https://dumps.wikimedia.org/enwiki/latest/

"""
from __future__ import unicode_literals

import logging
from pathlib import Path
import plac

from bin.wiki_entity_linking import wikipedia_processor as wp, wikidata_processor as wd
from bin.wiki_entity_linking import wiki_io as io
from bin.wiki_entity_linking import kb_creator
from bin.wiki_entity_linking import TRAINING_DATA_FILE, KB_FILE, ENTITY_DESCR_PATH, KB_MODEL_DIR, LOG_FORMAT
from bin.wiki_entity_linking import ENTITY_FREQ_PATH, PRIOR_PROB_PATH, ENTITY_DEFS_PATH, ENTITY_ALIAS_PATH
import spacy
from bin.wiki_entity_linking.kb_creator import read_kb

logger = logging.getLogger(__name__)


@plac.annotations(
    wd_json=("Path to the downloaded WikiData JSON dump.", "positional", None, Path),
    wp_xml=("Path to the downloaded Wikipedia XML dump.", "positional", None, Path),
    output_dir=("Output directory", "positional", None, Path),
    model=("Model name or path, should include pretrained vectors.", "positional", None, str),
    max_per_alias=("Max. # entities per alias (default 10)", "option", "a", int),
    min_freq=("Min. count of an entity in the corpus (default 20)", "option", "f", int),
    min_pair=("Min. count of entity-alias pairs (default 5)", "option", "c", int),
    entity_vector_length=("Length of entity vectors (default 64)", "option", "v", int),
    loc_prior_prob=("Location to file with prior probabilities", "option", "p", Path),
    loc_entity_defs=("Location to file with entity definitions", "option", "d", Path),
    loc_entity_desc=("Location to file with entity descriptions", "option", "s", Path),
    descr_from_wp=("Flag for using descriptions from WP instead of WD (default False)", "flag", "wp"),
    limit_prior=("Threshold to limit lines read from WP for prior probabilities", "option", "lp", int),
    limit_train=("Threshold to limit lines read from WP for training set", "option", "lt", int),
    limit_wd=("Threshold to limit lines read from WD", "option", "lw", int),
    lang=("Optional language for which to get Wikidata titles. Defaults to 'en'", "option", "la", str),
)
def main(
    wd_json,
    wp_xml,
    output_dir,
    model,
    max_per_alias=10,
    min_freq=20,
    min_pair=5,
    entity_vector_length=64,
    loc_prior_prob=None,
    loc_entity_defs=None,
    loc_entity_alias=None,
    loc_entity_desc=None,
    descr_from_wp=False,
    limit_prior=None,
    limit_train=None,
    limit_wd=None,
    lang="en",
):
    entity_defs_path = loc_entity_defs if loc_entity_defs else output_dir / ENTITY_DEFS_PATH
    entity_alias_path = loc_entity_alias if loc_entity_alias else output_dir / ENTITY_ALIAS_PATH
    entity_descr_path = loc_entity_desc if loc_entity_desc else output_dir / ENTITY_DESCR_PATH
    entity_freq_path = output_dir / ENTITY_FREQ_PATH
    prior_prob_path = loc_prior_prob if loc_prior_prob else output_dir / PRIOR_PROB_PATH
    training_entities_path = output_dir / TRAINING_DATA_FILE
    kb_path = output_dir / KB_FILE

    logger.info("Creating KB with Wikipedia and WikiData")

    # STEP 0: set up IO
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # STEP 1: Load the NLP object
    logger.info("STEP 1: Loading NLP model {}".format(model))
    nlp = spacy.load(model)

    # check the length of the nlp vectors
    if "vectors" not in nlp.meta or not nlp.vocab.vectors.size:
        raise ValueError(
            "The `nlp` object should have access to pretrained word vectors, "
            " cf. https://spacy.io/usage/models#languages."
        )

    # STEP 2: create prior probabilities from WP
    if not prior_prob_path.exists():
        # It takes about 2h to process 1000M lines of Wikipedia XML dump
        logger.info("STEP 2: Writing prior probabilities to {}".format(prior_prob_path))
        if limit_prior is not None:
            logger.warning("Warning: reading only {} lines of Wikipedia dump".format(limit_prior))
        wp.read_prior_probs(wp_xml, prior_prob_path, limit=limit_prior)
    else:
        logger.info("STEP 2: Reading prior probabilities from {}".format(prior_prob_path))

    # STEP 3: calculate entity frequencies
    if not entity_freq_path.exists():
        logger.info("STEP 3: Calculating and writing entity frequencies to {}".format(entity_freq_path))
        io.write_entity_to_count(prior_prob_path, entity_freq_path)
    else:
        logger.info("STEP 3: Reading entity frequencies from {}".format(entity_freq_path))

    # STEP 4: reading definitions and (possibly) descriptions from WikiData or from file
    if (not entity_defs_path.exists()) or (not descr_from_wp and not entity_descr_path.exists()):
        # It takes about 10h to process 55M lines of Wikidata JSON dump
        logger.info("STEP 4: Parsing and writing Wikidata entity definitions to {}".format(entity_defs_path))
        if limit_wd is not None:
            logger.warning("Warning: reading only {} lines of Wikidata dump".format(limit_wd))
        title_to_id, id_to_descr, id_to_alias = wd.read_wikidata_entities_json(
            wd_json,
            limit_wd,
            to_print=False,
            lang=lang,
            parse_descr=(not descr_from_wp),
        )
        io.write_title_to_id(entity_defs_path, title_to_id)

        logger.info("STEP 4b: Writing Wikidata entity aliases to {}".format(entity_alias_path))
        io.write_id_to_alias(entity_alias_path, id_to_alias)

        if not descr_from_wp:
            logger.info("STEP 4c: Writing Wikidata entity descriptions to {}".format(entity_descr_path))
            io.write_id_to_descr(entity_descr_path, id_to_descr)
    else:
        logger.info("STEP 4: Reading entity definitions from {}".format(entity_defs_path))
        logger.info("STEP 4b: Reading entity aliases from {}".format(entity_alias_path))
        if not descr_from_wp:
            logger.info("STEP 4c: Reading entity descriptions from {}".format(entity_descr_path))

    # STEP 5: Getting gold entities from Wikipedia
    if (not training_entities_path.exists()) or (descr_from_wp and not entity_descr_path.exists()):
        logger.info("STEP 5: Parsing and writing Wikipedia gold entities to {}".format(training_entities_path))
        if limit_train is not None:
            logger.warning("Warning: reading only {} lines of Wikipedia dump".format(limit_train))
        wp.create_training_and_desc(wp_xml, entity_defs_path, entity_descr_path,
                                    training_entities_path, descr_from_wp, limit_train)
        if descr_from_wp:
            logger.info("STEP 5b: Parsing and writing Wikipedia descriptions to {}".format(entity_descr_path))
    else:
        logger.info("STEP 5: Reading gold entities from {}".format(training_entities_path))
        if descr_from_wp:
            logger.info("STEP 5b: Reading entity descriptions from {}".format(entity_descr_path))

    # STEP 6: creating the actual KB
    # It takes ca. 30 minutes to pretrain the entity embeddings
    if not kb_path.exists():
        logger.info("STEP 6: Creating the KB at {}".format(kb_path))
        kb = kb_creator.create_kb(
            nlp=nlp,
            max_entities_per_alias=max_per_alias,
            min_entity_freq=min_freq,
            min_occ=min_pair,
            entity_def_path=entity_defs_path,
            entity_descr_path=entity_descr_path,
            entity_alias_path=entity_alias_path,
            entity_freq_path=entity_freq_path,
            prior_prob_path=prior_prob_path,
            entity_vector_length=entity_vector_length,
        )
        kb.dump(kb_path)
        logger.info("kb entities: {}".format(kb.get_size_entities()))
        logger.info("kb aliases: {}".format(kb.get_size_aliases()))
        nlp.to_disk(output_dir / KB_MODEL_DIR)
    else:
        logger.info("STEP 6: KB already exists at {}".format(kb_path))

    logger.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    plac.call(main)
