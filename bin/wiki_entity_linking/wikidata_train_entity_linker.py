# coding: utf-8
"""Script to take a previously created Knowledge Base and train an entity linking
pipeline. The provided KB directory should hold the kb, the original nlp object and
its vocab used to create the KB, and a few auxiliary files such as the entity definitions,
as created by the script `wikidata_create_kb`.

For the Wikipedia dump: get enwiki-latest-pages-articles-multistream.xml.bz2
from https://dumps.wikimedia.org/enwiki/latest/
"""
from __future__ import unicode_literals

import random
import logging
import spacy
from pathlib import Path
import plac

from bin.wiki_entity_linking import wikipedia_processor
from bin.wiki_entity_linking import TRAINING_DATA_FILE, KB_MODEL_DIR, KB_FILE, LOG_FORMAT, OUTPUT_MODEL_DIR
from bin.wiki_entity_linking.entity_linker_evaluation import measure_performance
from bin.wiki_entity_linking.kb_creator import read_kb

from spacy.util import minibatch, compounding

logger = logging.getLogger(__name__)


@plac.annotations(
    dir_kb=("Directory with KB, NLP and related files", "positional", None, Path),
    output_dir=("Output directory", "option", "o", Path),
    loc_training=("Location to training data", "option", "k", Path),
    epochs=("Number of training iterations (default 10)", "option", "e", int),
    dropout=("Dropout to prevent overfitting (default 0.5)", "option", "p", float),
    lr=("Learning rate (default 0.005)", "option", "n", float),
    l2=("L2 regularization", "option", "r", float),
    train_inst=("# training instances (default 90% of all)", "option", "t", int),
    dev_inst=("# test instances (default 10% of all)", "option", "d", int),
    labels_discard=("NER labels to discard (default None)", "option", "l", str),
)
def main(
    dir_kb,
    output_dir=None,
    loc_training=None,
    epochs=10,
    dropout=0.5,
    lr=0.005,
    l2=1e-6,
    train_inst=None,
    dev_inst=None,
    labels_discard=None
):
    logger.info("Creating Entity Linker with Wikipedia and WikiData")

    output_dir = Path(output_dir) if output_dir else dir_kb
    training_path = loc_training if loc_training else dir_kb / TRAINING_DATA_FILE
    nlp_dir = dir_kb / KB_MODEL_DIR
    kb_path = dir_kb / KB_FILE
    nlp_output_dir = output_dir / OUTPUT_MODEL_DIR

    # STEP 0: set up IO
    if not output_dir.exists():
        output_dir.mkdir()

    # STEP 1 : load the NLP object
    logger.info("STEP 1a: Loading model from {}".format(nlp_dir))
    nlp = spacy.load(nlp_dir)
    logger.info("STEP 1b: Loading KB from {}".format(kb_path))
    kb = read_kb(nlp, kb_path)

    # check that there is a NER component in the pipeline
    if "ner" not in nlp.pipe_names:
        raise ValueError("The `nlp` object should have a pretrained `ner` component.")

    # STEP 2: read the training dataset previously created from WP
    logger.info("STEP 2: Reading training dataset from {}".format(training_path))

    if labels_discard:
        labels_discard = [x.strip() for x in labels_discard.split(",")]
        logger.info("Discarding {} NER types: {}".format(len(labels_discard), labels_discard))
    else:
        labels_discard = []

    train_data = wikipedia_processor.read_training(
        nlp=nlp,
        entity_file_path=training_path,
        dev=False,
        limit=train_inst,
        kb=kb,
        labels_discard=labels_discard
    )

    # for testing, get all pos instances (independently of KB)
    dev_data = wikipedia_processor.read_training(
        nlp=nlp,
        entity_file_path=training_path,
        dev=True,
        limit=dev_inst,
        kb=None,
        labels_discard=labels_discard
    )

    # STEP 3: create and train an entity linking pipe
    logger.info("STEP 3: Creating and training an Entity Linking pipe")

    el_pipe = nlp.create_pipe(
        name="entity_linker", config={"pretrained_vectors": nlp.vocab.vectors.name,
                                      "labels_discard": labels_discard}
    )
    el_pipe.set_kb(kb)
    nlp.add_pipe(el_pipe, last=True)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
    with nlp.disable_pipes(*other_pipes):  # only train Entity Linking
        optimizer = nlp.begin_training()
        optimizer.learn_rate = lr
        optimizer.L2 = l2

    logger.info("Training on {} articles".format(len(train_data)))
    logger.info("Dev testing on {} articles".format(len(dev_data)))

    # baseline performance on dev data
    logger.info("Dev Baseline Accuracies:")
    measure_performance(dev_data, kb, el_pipe, baseline=True, context=False)

    for itn in range(epochs):
        random.shuffle(train_data)
        losses = {}
        batches = minibatch(train_data, size=compounding(4.0, 128.0, 1.001))
        batchnr = 0

        with nlp.disable_pipes(*other_pipes):
            for batch in batches:
                try:
                    docs, golds = zip(*batch)
                    nlp.update(
                        docs=docs,
                        golds=golds,
                        sgd=optimizer,
                        drop=dropout,
                        losses=losses,
                    )
                    batchnr += 1
                except Exception as e:
                    logger.error("Error updating batch:" + str(e))
        if batchnr > 0:
            logging.info("Epoch {}, train loss {}".format(itn, round(losses["entity_linker"] / batchnr, 2)))
            measure_performance(dev_data, kb, el_pipe, baseline=False, context=True)

    # STEP 4: measure the performance of our trained pipe on an independent dev set
    logger.info("STEP 4: Final performance measurement of Entity Linking pipe")
    measure_performance(dev_data, kb, el_pipe)

    # STEP 5: apply the EL pipe on a toy example
    logger.info("STEP 5: Applying Entity Linking to toy example")
    run_el_toy_example(nlp=nlp)

    if output_dir:
        # STEP 6: write the NLP pipeline (now including an EL model) to file
        logger.info("STEP 6: Writing trained NLP to {}".format(nlp_output_dir))
        nlp.to_disk(nlp_output_dir)

        logger.info("Done!")


def check_kb(kb):
    for mention in ("Bush", "Douglas Adams", "Homer", "Brazil", "China"):
        candidates = kb.get_candidates(mention)

        logger.info("generating candidates for " + mention + " :")
        for c in candidates:
            logger.info(" ".join[
                str(c.prior_prob),
                c.alias_,
                "-->",
                c.entity_ + " (freq=" + str(c.entity_freq) + ")"
            ])


def run_el_toy_example(nlp):
    text = (
        "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, "
        "Douglas reminds us to always bring our towel, even in China or Brazil. "
        "The main character in Doug's novel is the man Arthur Dent, "
        "but Dougledydoug doesn't write about George Washington or Homer Simpson."
    )
    doc = nlp(text)
    logger.info(text)
    for ent in doc.ents:
        logger.info(" ".join(["ent", ent.text, ent.label_, ent.kb_id_]))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    plac.call(main)
