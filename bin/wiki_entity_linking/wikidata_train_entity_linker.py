# coding: utf-8
"""Script that takes a previously created Knowledge Base and trains an entity linking
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
from tqdm import tqdm

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
    train_articles=("# training articles (default 90% of all)", "option", "t", int),
    dev_articles=("# dev test articles (default 10% of all)", "option", "d", int),
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
    train_articles=None,
    dev_articles=None,
    labels_discard=None
):
    if not output_dir:
        logger.warning("No output dir specified so no results will be written, are you sure about this ?")

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
    logger.info("Original NLP pipeline has following pipeline components: {}".format(nlp.pipe_names))

    # check that there is a NER component in the pipeline
    if "ner" not in nlp.pipe_names:
        raise ValueError("The `nlp` object should have a pretrained `ner` component.")

    logger.info("STEP 1b: Loading KB from {}".format(kb_path))
    kb = read_kb(nlp, kb_path)

    # STEP 2: read the training dataset previously created from WP
    logger.info("STEP 2: Reading training & dev dataset from {}".format(training_path))
    train_indices, dev_indices = wikipedia_processor.read_training_indices(training_path)
    logger.info("Training set has {} articles, limit set to roughly {} articles per epoch"
                .format(len(train_indices), train_articles if train_articles else "all"))
    logger.info("Dev set has {} articles, limit set to rougly {} articles for evaluation"
                .format(len(dev_indices), dev_articles if dev_articles else "all"))
    if dev_articles:
        dev_indices = dev_indices[0:dev_articles]

    # STEP 3: create and train an entity linking pipe
    logger.info("STEP 3: Creating and training an Entity Linking pipe for {} epochs".format(epochs))
    if labels_discard:
        labels_discard = [x.strip() for x in labels_discard.split(",")]
        logger.info("Discarding {} NER types: {}".format(len(labels_discard), labels_discard))
    else:
        labels_discard = []

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

    logger.info("Dev Baseline Accuracies:")
    dev_data = wikipedia_processor.read_el_docs_golds(nlp=nlp, entity_file_path=training_path,
                                                      dev=True, line_ids=dev_indices,
                                                      kb=kb, labels_discard=labels_discard)

    measure_performance(dev_data, kb, el_pipe, baseline=True, context=False, dev_limit=len(dev_indices))

    for itn in range(epochs):
        random.shuffle(train_indices)
        losses = {}
        batches = minibatch(train_indices, size=compounding(8.0, 128.0, 1.001))
        batchnr = 0
        articles_processed = 0

        # we either process the whole training file, or just a part each epoch
        bar_total = len(train_indices)
        if train_articles:
            bar_total = train_articles

        with tqdm(total=bar_total, leave=False, desc='Epoch ' + str(itn)) as pbar:
            for batch in batches:
                if not train_articles or articles_processed < train_articles:
                    with nlp.disable_pipes("entity_linker"):
                        train_batch = wikipedia_processor.read_el_docs_golds(nlp=nlp, entity_file_path=training_path,
                                                                             dev=False, line_ids=batch,
                                                                             kb=kb, labels_discard=labels_discard)
                        docs, golds = zip(*train_batch)
                    try:
                        with nlp.disable_pipes(*other_pipes):
                            nlp.update(
                                docs=docs,
                                golds=golds,
                                sgd=optimizer,
                                drop=dropout,
                                losses=losses,
                            )
                            batchnr += 1
                            articles_processed += len(docs)
                            pbar.update(len(docs))
                    except Exception as e:
                        logger.error("Error updating batch:" + str(e))
        if batchnr > 0:
            logging.info("Epoch {} trained on {} articles, train loss {}"
                         .format(itn, articles_processed, round(losses["entity_linker"] / batchnr, 2)))
            # re-read the dev_data (data is returned as a generator)
            dev_data = wikipedia_processor.read_el_docs_golds(nlp=nlp, entity_file_path=training_path,
                                                              dev=True, line_ids=dev_indices,
                                                              kb=kb, labels_discard=labels_discard)
            measure_performance(dev_data, kb, el_pipe, baseline=False, context=True, dev_limit=len(dev_indices))

    if output_dir:
        # STEP 4: write the NLP pipeline (now including an EL model) to file
        logger.info("Final NLP pipeline has following pipeline components: {}".format(nlp.pipe_names))
        logger.info("STEP 4: Writing trained NLP to {}".format(nlp_output_dir))
        nlp.to_disk(nlp_output_dir)

        logger.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    plac.call(main)
