from random import shuffle

from examples.pipeline.wiki_entity_linking import kb_creator

import numpy as np

from spacy._ml import zero_init, create_default_optimizer
from spacy.cli.pretrain import get_cossim_loss

from thinc.v2v import Model
from thinc.api import chain
from thinc.neural._classes.affine import Affine


class EntityEncoder:

    DROP = 0
    EPOCHS = 5
    STOP_THRESHOLD = 0.9 # 0.1

    BATCH_SIZE = 1000

    def __init__(self, nlp, input_dim, desc_width):
        self.nlp = nlp
        self.input_dim = input_dim
        self.desc_width = desc_width

    def apply_encoder(self, description_list):
        if self.encoder is None:
            raise ValueError("Can not apply encoder before training it")

        print("Encoding", len(description_list), "entities")

        batch_size = 10000

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
            print("encoded :", len(encodings))

        return encodings

    def train(self, description_list, to_print=False):
        processed, loss = self._train_model(description_list)

        if to_print:
            print("Trained on", processed, "entities across", self.EPOCHS, "epochs")
            print("Final loss:", loss)

        # self._test_encoder()

    def _train_model(self, description_list):
        # TODO: when loss gets too low, a 'mean of empty slice' warning is thrown by numpy

        self._build_network(self.input_dim, self.desc_width)

        processed = 0
        loss = 1
        descriptions = description_list.copy()   # copy this list so that shuffling does not affect other functions

        for i in range(self.EPOCHS):
            shuffle(descriptions)

            batch_nr = 0
            start = 0
            stop = min(self.BATCH_SIZE, len(descriptions))

            while loss > self.STOP_THRESHOLD and start < len(descriptions):
                batch = []
                for descr in descriptions[start:stop]:
                    doc = self.nlp(descr)
                    doc_vector = self._get_doc_embedding(doc)
                    batch.append(doc_vector)

                loss = self._update(batch)
                print(i, batch_nr, loss)
                processed += len(batch)

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
        doc_vector = np.mean(word_vectors, axis=0)  # TODO: min? max?
        return doc_vector

    def _build_network(self, orig_width, hidden_with):
        with Model.define_operators({">>": chain}):
            self.encoder = (
                Affine(hidden_with, orig_width)
            )
            self.model = self.encoder >> zero_init(Affine(orig_width, hidden_with, drop_factor=0.0))

        self.sgd = create_default_optimizer(self.model.ops)

    def _update(self, vectors):
        predictions, bp_model = self.model.begin_update(np.asarray(vectors), drop=self.DROP)

        loss, d_scores = self._get_loss(scores=predictions, golds=np.asarray(vectors))
        bp_model(d_scores, sgd=self.sgd)

        return loss / len(vectors)

    @staticmethod
    def _get_loss(golds, scores):
        loss, gradients = get_cossim_loss(scores, golds)
        return loss, gradients

    def _test_encoder(self):
        """ Test encoder on some dummy examples """
        desc_A1 = "Fictional character in The Simpsons"
        desc_A2 = "Simpsons - fictional human"
        desc_A3 = "Fictional character in The Flintstones"
        desc_A4 = "Politician from the US"

        A1_doc_vector = np.asarray([self._get_doc_embedding(self.nlp(desc_A1))])
        A2_doc_vector = np.asarray([self._get_doc_embedding(self.nlp(desc_A2))])
        A3_doc_vector = np.asarray([self._get_doc_embedding(self.nlp(desc_A3))])
        A4_doc_vector = np.asarray([self._get_doc_embedding(self.nlp(desc_A4))])

        loss_a1_a1, _ = get_cossim_loss(A1_doc_vector, A1_doc_vector)
        loss_a1_a2, _ = get_cossim_loss(A1_doc_vector, A2_doc_vector)
        loss_a1_a3, _ = get_cossim_loss(A1_doc_vector, A3_doc_vector)
        loss_a1_a4, _ = get_cossim_loss(A1_doc_vector, A4_doc_vector)

        print("sim doc A1 A1", loss_a1_a1)
        print("sim doc A1 A2", loss_a1_a2)
        print("sim doc A1 A3", loss_a1_a3)
        print("sim doc A1 A4", loss_a1_a4)

        A1_encoded = self.encoder(A1_doc_vector)
        A2_encoded = self.encoder(A2_doc_vector)
        A3_encoded = self.encoder(A3_doc_vector)
        A4_encoded = self.encoder(A4_doc_vector)

        loss_a1_a1, _ = get_cossim_loss(A1_encoded, A1_encoded)
        loss_a1_a2, _ = get_cossim_loss(A1_encoded, A2_encoded)
        loss_a1_a3, _ = get_cossim_loss(A1_encoded, A3_encoded)
        loss_a1_a4, _ = get_cossim_loss(A1_encoded, A4_encoded)

        print("sim encoded A1 A1", loss_a1_a1)
        print("sim encoded A1 A2", loss_a1_a2)
        print("sim encoded A1 A3", loss_a1_a3)
        print("sim encoded A1 A4", loss_a1_a4)
