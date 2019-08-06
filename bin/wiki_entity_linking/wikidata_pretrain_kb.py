# coding: utf-8
"""Script to process Wikipedia and Wikidata dumps and create a knowledge base (KB)
with specific parameters. Intermediate files are written to disk to speed up
creation of a KB with slightly different parameters in a next run.

For the Wikidata dump: get the latest-all.json.bz2 from https://dumps.wikimedia.org/wikidatawiki/entities/
For the Wikipedia dump: get enwiki-latest-pages-articles-multistream.xml.bz2
from https://dumps.wikimedia.org/enwiki/latest/

"""
from __future__ import unicode_literals

import datetime
from pathlib import Path
import plac

from bin.wiki_entity_linking import wikipedia_processor as wp
from bin.wiki_entity_linking import kb_creator

import spacy

from spacy import Errors


def now():
    return datetime.datetime.now()


@plac.annotations(
    wd_json=("Path to the downloaded WikiData JSON dump.", "positional", None, Path),
    wp_xml=("Path to the downloaded Wikipedia XML dump.", "positional", None, Path),
    output_dir=("Output directory", "positional", None, Path),
    model=("Model name, should include pretrained vectors.", "positional", None, str),
    max_per_alias=("Max. # entities per alias (default 10)", "option", "a", int),
    min_freq=("Min. count of an entity in the corpus (default 20)", "option", "e", int),
    min_pair=("Min. count of entity-alias pairs (default 5)", "option", "c", int),
    entity_vector_length=("Length of entity vectors (default 64)", "option", "v", int),
    loc_prior_prob=("Location to file with prior probabilities", "option", "p", Path),
    loc_entity_freq=("Location to file with entity frequencies", "option", "f", Path),
    limit=("Optional threshold to limit lines read from dumps", "option", "l", int),
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
    loc_entity_freq=None,
    limit=None,
):
    print("Creating KB with Wikipedia and WikiData", now())
    print()

    if limit is not None:
        print("Warning: reading only", limit, "lines of Wikipedia/Wikidata dumps.")

    # STEP 0: set up IO
    if not output_dir.exists():
        output_dir.mkdir()

    # STEP 1: create the NLP object
    print("STEP 1: loaded model", model, now())
    nlp = spacy.load(model)

    # check the length of the nlp vectors
    if "vectors" not in nlp.meta or not nlp.vocab.vectors.size:
        raise ValueError(Errors.E151)

    # STEP 2: create prior probabilities from WP
    print()
    if loc_prior_prob:
        print("STEP 2: reading prior probabilities from", loc_prior_prob, now())
    else:
        loc_prior_prob = output_dir / "prior_prob.csv"
        print("STEP 2: writing prior probabilities at", loc_prior_prob, now())
        wp.read_prior_probs(wp_xml, loc_prior_prob, limit=limit)

    # STEP 3: deduce entity frequencies from WP
    print()
    if loc_entity_freq:
        print("STEP 3: reading entity frequencies from", loc_entity_freq, now())
    else:
        loc_entity_freq = output_dir / "entity_freq.csv"
        print("STEP 3: writing entity frequencies at", loc_entity_freq, now())
        wp.write_entity_counts(loc_prior_prob, loc_entity_freq, to_print=False)

    loc_kb = output_dir / "kb"
    loc_entity_defs = output_dir / "entity_defs.csv"
    loc_entity_desc = output_dir / "entity_descriptions.csv"

    # STEP 4: creating the actual KB
    print()
    print("STEP 4: creating the KB at", loc_kb, now())
    kb = kb_creator.create_kb(
        nlp=nlp,
        max_entities_per_alias=max_per_alias,
        min_entity_freq=min_freq,
        min_occ=min_pair,
        entity_def_output=loc_entity_defs,
        entity_descr_output=loc_entity_desc,
        count_input=loc_entity_freq,
        prior_prob_input=loc_prior_prob,
        wikidata_input=wd_json,
        entity_vector_length=entity_vector_length,
        limit=limit,
    )

    kb.dump(loc_kb)
    nlp.to_disk(output_dir / "nlp")

    print()
    print("Done!", now())


if __name__ == "__main__":
    plac.call(main)
