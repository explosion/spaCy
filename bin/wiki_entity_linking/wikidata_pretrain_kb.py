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
from bin.wiki_entity_linking import kb_creator
from bin.wiki_entity_linking import training_set_creator
from bin.wiki_entity_linking import TRAINING_DATA_FILE, KB_FILE, KB_MODEL_DIR
import spacy

LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
logger = logging.getLogger(__name__)


@plac.annotations(
    wikidata_json=("Path to the downloaded WikiData JSON dump.", "positional", None, Path),
    wikipedia_xml=("Path to the downloaded Wikipedia XML dump.", "positional", None, Path),
    output_dir=("Output directory", "positional", None, Path),
    model=("Model name, should include pretrained vectors.", "positional", None, str),
    model_is_path=("Model is a path not a model name.", "flag", "mp"),
    max_per_alias=("Max. # entities per alias (default 10)", "option", "a", int),
    min_freq=("Min. count of an entity in the corpus (default 20)", "option", "f", int),
    min_pair=("Min. count of entity-alias pairs (default 5)", "option", "c", int),
    entity_vector_length=("Length of entity vectors (default 64)", "option", "v", int),
    limit=("Optional threshold to limit lines read from dumps", "option", "l", int),
    create_prior_probs=("Flag to recreate prior probs", "flag", "cp"),
    create_training_set=("Flag to recreate training data", "flag", "t"),
    lang=("Optional language for which to get wikidata titles. Defaults to 'en'", "option", "la", str),
)
def main(
    wikidata_json,
    wikipedia_xml,
    output_dir,
    model,
    model_is_path=False,
    max_per_alias=10,
    min_freq=20,
    min_pair=5,
    entity_vector_length=64,
    limit=None,
    create_prior_probs=False,
    create_training_set=False,
    lang="en",
):

    entity_defs_path = output_dir / "entity_defs.csv"
    entity_descr_path = output_dir / "entity_descriptions.csv"
    entity_freq_path = output_dir / "entity_freq.csv"
    prior_prob_path = output_dir / "prior_prob.csv"
    training_entities_path = output_dir / TRAINING_DATA_FILE
    kb_path = output_dir / KB_FILE

    logger.info("Creating KB with Wikipedia and WikiData")

    if limit is not None:
        logger.warning("Warning: reading only {} lines of Wikipedia/Wikidata dumps.".format(limit))

    # STEP 0: set up IO
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # STEP 1: create the NLP object
    logger.info("STEP 1: loading model {}".format(model))
    if model_is_path:
        nlp = spacy.load(Path(model))
    else:
        nlp = spacy.load(model)

    # check the length of the nlp vectors
    if "vectors" not in nlp.meta or not nlp.vocab.vectors.size:
        raise ValueError(
            "The `nlp` object should have access to pre-trained word vectors, "
            " cf. https://spacy.io/usage/models#languages."
        )

    # STEP 2: create prior probabilities from WP
    if create_prior_probs or not prior_prob_path.exists():
        # It takes about 2h to process 1000M lines of Wikipedia XML dump
        logger.info("STEP 2: writing prior probabilities to {}".format(prior_prob_path))
        wp.read_prior_probs(wikipedia_xml, prior_prob_path, limit=limit)
    logger.info("STEP 2: reading prior probabilities from {}".format(prior_prob_path))

    # STEP 3: deduce entity frequencies from WP (takes only a few minutes)
    logger.info("STEP 3: calculating entity frequencies")
    wp.write_entity_counts(prior_prob_path, entity_freq_path, to_print=False)

    # STEP 4: reading entity descriptions and definitions from WikiData or from file
    if not entity_defs_path.exists():
        # It takes about 10h to process 55M lines of Wikidata JSON dump
        logger.info("STEP 4: parsing wikidata for entity definitions")
        title_to_id = wd.read_wikidata_entities_json(
            wikidata_json,
            limit,
            to_print=False,
            lang=lang
        )
        wd.write_entity_files(entity_defs_path, title_to_id)

    # STEP 5: Getting descriptions and gold entities from wikipedia
    logger.info("STEP 5: getting descriptions and gold entities")
    if create_training_set or not (entity_descr_path.exists() and training_entities_path.exists()):
        training_set_creator.create_training_examples_and_descriptions(
            wikipedia_xml,
            entity_defs_path,
            entity_descr_path,
            training_entities_path
        )

    # STEP 6: creating the actual KB
    # It takes ca. 30 minutes to pretrain the entity embeddings
    logger.info("STEP 6: creating the KB at {}".format(kb_path))
    kb = kb_creator.create_kb(
        nlp=nlp,
        max_entities_per_alias=max_per_alias,
        min_entity_freq=min_freq,
        min_occ=min_pair,
        entity_def_input=entity_defs_path,
        entity_descr_path=entity_descr_path,
        count_input=entity_freq_path,
        prior_prob_input=prior_prob_path,
        entity_vector_length=entity_vector_length,
    )

    kb.dump(kb_path)
    nlp.to_disk(output_dir / KB_MODEL_DIR)

    logger.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    plac.call(main)
