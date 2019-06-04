from random import shuffle

from examples.pipeline.wiki_entity_linking import kb_creator

import numpy as np

from spacy._ml import zero_init, create_default_optimizer
from spacy.cli.pretrain import get_cossim_loss

from thinc.v2v import Model
from thinc.api import chain
from thinc.neural._classes.affine import Affine


class EntityEncoder:

    INPUT_DIM = 300  # dimension of pre-trained vectors
    DESC_WIDTH = 64

    DROP = 0
    EPOCHS = 5
    STOP_THRESHOLD = 0.05

    BATCH_SIZE = 1000

    def __init__(self, kb, nlp):
        self.nlp = nlp
        self.kb = kb

    def run(self, entity_descr_output):
        id_to_descr = kb_creator._get_id_to_description(entity_descr_output)

        processed, loss = self._train_model(entity_descr_output, id_to_descr)
        print("Trained on", processed, "entities across", self.EPOCHS, "epochs")
        print("Final loss:", loss)
        print()

        # TODO: apply and write to file afterwards !
        # self._apply_encoder(id_to_descr)

    def _train_model(self, entity_descr_output, id_to_descr):
        # TODO: when loss gets too low, a 'mean of empty slice' warning is thrown by numpy

        self._build_network(self.INPUT_DIM, self.DESC_WIDTH)

        processed = 0
        loss = 1

        for i in range(self.EPOCHS):
            entity_keys = list(id_to_descr.keys())
            shuffle(entity_keys)

            batch_nr = 0
            start = 0
            stop = min(self.BATCH_SIZE, len(entity_keys))

            while loss > self.STOP_THRESHOLD and start < len(entity_keys):
                batch = []
                for e in entity_keys[start:stop]:
                    descr = id_to_descr[e]
                    doc = self.nlp(descr)
                    doc_vector = self._get_doc_embedding(doc)
                    batch.append(doc_vector)

                loss = self.update(batch)
                print(i, batch_nr, loss)
                processed += len(batch)

                batch_nr += 1
                start = start + self.BATCH_SIZE
                stop = min(stop + self.BATCH_SIZE, len(entity_keys))

        return processed, loss

    def _apply_encoder(self, id_to_descr):
        for id, descr in id_to_descr.items():
            doc = self.nlp(descr)
            doc_vector = self._get_doc_embedding(doc)
            encoding = self.encoder(np.asarray([doc_vector]))

    @staticmethod
    def _get_doc_embedding(doc):
        indices = np.zeros((len(doc),), dtype="i")
        for i, word in enumerate(doc):
            if word.orth in doc.vocab.vectors.key2row:
                indices[i] = doc.vocab.vectors.key2row[word.orth]
            else:
                indices[i] = 0
        word_vectors = doc.vocab.vectors.data[indices]
        doc_vector = np.mean(word_vectors, axis=0)  # TODO: min? max?
        return doc_vector

    def _build_network(self, orig_width, hidden_with):
        with Model.define_operators({">>": chain}):
            self.encoder = (
                Affine(hidden_with, orig_width)
            )
            self.model = self.encoder >> zero_init(Affine(orig_width, hidden_with, drop_factor=0.0))

        self.sgd = create_default_optimizer(self.model.ops)

    def update(self, vectors):
        predictions, bp_model = self.model.begin_update(np.asarray(vectors), drop=self.DROP)

        loss, d_scores = self.get_loss(scores=predictions, golds=np.asarray(vectors))
        bp_model(d_scores, sgd=self.sgd)

        return loss / len(vectors)

    @staticmethod
    def get_loss(golds, scores):
        loss, gradients = get_cossim_loss(scores, golds)
        return loss, gradients
