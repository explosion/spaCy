# coding: utf-8
from random import shuffle

import logging
import numpy as np

from spacy._ml import zero_init, create_default_optimizer
from spacy.cli.pretrain import get_cossim_loss

from thinc.v2v import Model
from thinc.api import chain
from thinc.neural._classes.affine import Affine

logger = logging.getLogger(__name__)


class EntityEncoder:
    """
    Train the embeddings of entity descriptions to fit a fixed-size entity vector (e.g. 64D).
    This entity vector will be stored in the KB, for further downstream use in the entity model.
    """

    DROP = 0
    BATCH_SIZE = 1000

    # Set min. acceptable loss to avoid a 'mean of empty slice' warning by numpy
    MIN_LOSS = 0.01

    # Reasonable default to stop training when things are not improving
    MAX_NO_IMPROVEMENT = 20

    def __init__(self, nlp, input_dim, desc_width, epochs=5):
        self.nlp = nlp
        self.input_dim = input_dim
        self.desc_width = desc_width
        self.epochs = epochs

    def apply_encoder(self, description_list):
        if self.encoder is None:
            raise ValueError("Can not apply encoder before training it")

        batch_size = 100000

        start = 0
        stop = min(batch_size, len(description_list))
        encodings = []

        while start < len(description_list):
            docs = list(self.nlp.pipe(description_list[start:stop]))
            doc_embeddings = [self._get_doc_embedding(doc) for doc in docs]
            enc = self.encoder(np.asarray(doc_embeddings))
            encodings.extend(enc.tolist())

            start = start + batch_size
            stop = min(stop + batch_size, len(description_list))
            logger.info("Encoded: {} entities".format(stop))

        return encodings

    def train(self, description_list, to_print=False):
        processed, loss = self._train_model(description_list)
        if to_print:
            logger.info(
                "Trained entity descriptions on {} ".format(processed) +
                "(non-unique) descriptions across {} ".format(self.epochs) +
                "epochs"
            )
            logger.info("Final loss: {}".format(loss))

    def _train_model(self, description_list):
        best_loss = 1.0
        iter_since_best = 0
        self._build_network(self.input_dim, self.desc_width)

        processed = 0
        loss = 1
        # copy this list so that shuffling does not affect other functions
        descriptions = description_list.copy()
        to_continue = True

        for i in range(self.epochs):
            shuffle(descriptions)

            batch_nr = 0
            start = 0
            stop = min(self.BATCH_SIZE, len(descriptions))

            while to_continue and start < len(descriptions):
                batch = []
                for descr in descriptions[start:stop]:
                    doc = self.nlp(descr)
                    doc_vector = self._get_doc_embedding(doc)
                    batch.append(doc_vector)

                loss = self._update(batch)
                if batch_nr % 25 == 0:
                    logger.info("loss: {} ".format(loss))
                processed += len(batch)

                # in general, continue training if we haven't reached our ideal min yet
                to_continue = loss > self.MIN_LOSS

                # store the best loss and track how long it's been
                if loss < best_loss:
                    best_loss = loss
                    iter_since_best = 0
                else:
                    iter_since_best += 1

                # stop learning if we haven't seen improvement since the last few iterations
                if iter_since_best > self.MAX_NO_IMPROVEMENT:
                    to_continue = False

                batch_nr += 1
                start = start + self.BATCH_SIZE
                stop = min(stop + self.BATCH_SIZE, len(descriptions))

        return processed, loss

    @staticmethod
    def _get_doc_embedding(doc):
        indices = np.zeros((len(doc),), dtype="i")
        for i, word in enumerate(doc):
            if word.orth in doc.vocab.vectors.key2row:
                indices[i] = doc.vocab.vectors.key2row[word.orth]
            else:
                indices[i] = 0
        word_vectors = doc.vocab.vectors.data[indices]
        doc_vector = np.mean(word_vectors, axis=0)
        return doc_vector

    def _build_network(self, orig_width, hidden_with):
        with Model.define_operators({">>": chain}):
            # very simple encoder-decoder model
            self.encoder = Affine(hidden_with, orig_width)
            self.model = self.encoder >> zero_init(
                Affine(orig_width, hidden_with, drop_factor=0.0)
            )
        self.sgd = create_default_optimizer(self.model.ops)

    def _update(self, vectors):
        predictions, bp_model = self.model.begin_update(
            np.asarray(vectors), drop=self.DROP
        )
        loss, d_scores = self._get_loss(scores=predictions, golds=np.asarray(vectors))
        bp_model(d_scores, sgd=self.sgd)
        return loss / len(vectors)

    @staticmethod
    def _get_loss(golds, scores):
        loss, gradients = get_cossim_loss(scores, golds)
        return loss, gradients
