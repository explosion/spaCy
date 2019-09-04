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
from pathlib import Path
import plac

from bin.wiki_entity_linking import training_set_creator
from bin.wiki_entity_linking import TRAINING_DATA_FILE, KB_MODEL_DIR, KB_FILE
from bin.wiki_entity_linking.entity_linker_evaluation import measure_acc, measure_baselines
from bin.wiki_entity_linking.kb_creator import read_nlp_kb

from spacy.util import minibatch, compounding


LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
logger = logging.getLogger(__name__)


@plac.annotations(
    output_dir=("Output directory", "positional"),
    epochs=("Number of training iterations (default 10)", "option", "e", int),
    dropout=("Dropout to prevent overfitting (default 0.5)", "option", "p", float),
    lr=("Learning rate (default 0.005)", "option", "n", float),
    l2=("L2 regularization", "option", "r", float),
    train_inst=("# training instances (default 90% of all)", "option", "t", int),
    dev_inst=("# test instances (default 10% of all)", "option", "d", int),
    limit=("Optional threshold to limit lines read from WP dump", "option", "l", int),
)
def main(
    output_dir,
    epochs=10,
    dropout=0.5,
    lr=0.005,
    l2=1e-6,
    train_inst=None,
    dev_inst=None,
    limit=None,
):
    logger.info("Creating Entity Linker with Wikipedia and WikiData")

    output_dir = Path(output_dir)
    training_path = output_dir / TRAINING_DATA_FILE
    nlp_dir = output_dir / KB_MODEL_DIR
    kb_path = output_dir / KB_FILE
    nlp_loc = output_dir / "nlp"

    # STEP 0: set up IO
    if output_dir and not output_dir.exists():
        output_dir.mkdir()

    # STEP 1 : load the NLP object
    logger.info("STEP 1: loading model from {}".format(nlp_dir))
    nlp, kb = read_nlp_kb(nlp_dir, kb_path)

    # check that there is a NER component in the pipeline
    if "ner" not in nlp.pipe_names:
        raise ValueError("The `nlp` object should have a pre-trained `ner` component.")

    # STEP 3: create a training dataset from WP
    logger.info("STEP 3: reading training dataset from {}".format(training_path))

    train_data = training_set_creator.read_training(
        nlp=nlp,
        entity_file_path=training_path,
        dev=False,
        limit=train_inst,
        kb=kb,
    )

    # for testing, get all pos instances, whether or not they are in the kb
    dev_data = training_set_creator.read_training(
        nlp=nlp,
        entity_file_path=training_path,
        dev=True,
        limit=dev_inst,
        kb=kb,
    )

    # STEP 5: create and train the entity linking pipe
    logger.info("STEP 5: training Entity Linking pipe")

    el_pipe = nlp.create_pipe(
        name="entity_linker", config={"pretrained_vectors": nlp.vocab.vectors.name}
    )
    el_pipe.set_kb(kb)
    nlp.add_pipe(el_pipe, last=True)

    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "entity_linker"]
    with nlp.disable_pipes(*other_pipes):  # only train Entity Linking
        optimizer = nlp.begin_training()
        optimizer.learn_rate = lr
        optimizer.L2 = l2

    logger.info(f"Training on {len(train_data)} articles")
    logger.info(f"Dev testing on {len(dev_data)} articles")

    dev_baseline_accuracies = measure_baselines(
        dev_data, kb
    )

    logger.info(f"Dev Baseline Accuracies:")
    logger.info(dev_baseline_accuracies.report_accuracy("random"))
    logger.info(dev_baseline_accuracies.report_accuracy("prior"))
    logger.info(dev_baseline_accuracies.report_accuracy("oracle"))

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
                    print("Error updating batch:", e)

            el_pipe.cfg["incl_context"] = True
            el_pipe.cfg["incl_prior"] = True
            dev_precision_context, dev_recall_context, _ = measure_acc(dev_data, el_pipe)
            losses["entity_linker"] = losses["entity_linker"] / batchnr
            logger.info(f"Epoch {itn} | "
                        f"train loss {round(losses['entity_linker'] / batchnr, 2)} | "
                        f"Dev precision with prior {round(dev_precision_context, 3)} | "
                        f"Dev recall with prior {round(dev_precision_context, 3)}")

    # STEP 6: measure the performance of our trained pipe on an independent dev set
    logger.info("STEP 6: performance measurement of Entity Linking pipe")

    # using only context
    el_pipe.cfg["incl_context"] = True
    el_pipe.cfg["incl_prior"] = False
    dev_precision_context, dev_recall_context, _ = measure_acc(dev_data, el_pipe)
    logger.info("Dev precision with context "
                "{} | ".format(round(dev_precision_context, 3)) +
                "Dev recall with context "
                "{}".format(round(dev_precision_context, 3)))

    # measuring combined accuracy (prior + context)
    el_pipe.cfg["incl_context"] = True
    el_pipe.cfg["incl_prior"] = True
    dev_precision_context, dev_recall_context, _ = measure_acc(dev_data, el_pipe)
    logger.info("Dev precision with prior + context "
                "{} | ".format(round(dev_precision_context, 3)) +
                "Dev recall with prior + context "
                "{}".format(round(dev_precision_context, 3)))

    # STEP 7: apply the EL pipe on a toy example
    logger.info("STEP 7: applying Entity Linking to toy example")
    run_el_toy_example(nlp=nlp)

    # STEP 8: write the NLP pipeline (including entity linker) to file
    logger.info("STEP 8: Writing trained NLP to", nlp_loc)
    nlp.to_disk(nlp_loc)

    logger.info("Done!")


def check_kb(kb):
    for mention in ("Bush", "Douglas Adams", "Homer", "Brazil", "China"):
        candidates = kb.get_candidates(mention)

        print("generating candidates for " + mention + " :")
        for c in candidates:
            print(
                " ",
                c.prior_prob,
                c.alias_,
                "-->",
                c.entity_ + " (freq=" + str(c.entity_freq) + ")",
            )


def run_el_toy_example(nlp):
    text = (
        "In The Hitchhiker's Guide to the Galaxy, written by Douglas Adams, "
        "Douglas reminds us to always bring our towel, even in China or Brazil. "
        "The main character in Doug's novel is the man Arthur Dent, "
        "but Dougledydoug doesn't write about George Washington or Homer Simpson."
    )
    doc = nlp(text)
    print(text)
    for ent in doc.ents:
        print(" ent", ent.text, ent.label_, ent.kb_id_)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    plac.call(main)
