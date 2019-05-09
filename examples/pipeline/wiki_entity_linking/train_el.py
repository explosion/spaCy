# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir

from examples.pipeline.wiki_entity_linking import run_el, training_set_creator, kb_creator

from spacy._ml import SpacyVectors, create_default_optimizer, zero_init

from thinc.api import chain
from thinc.v2v import Model, Maxout, Softmax, Affine, ReLu
from thinc.api import flatten_add_lengths
from thinc.t2v import Pooling, sum_pool, mean_pool
from thinc.t2t import ExtractWindow, ParametricAttention
from thinc.misc import Residual

""" TODO: this code needs to be implemented in pipes.pyx"""


class EL_Model():

    labels = ["MATCH", "NOMATCH"]
    name = "entity_linker"

    def __init__(self, kb, nlp):
        run_el._prepare_pipeline(nlp, kb)
        self.nlp = nlp
        self.kb = kb

        self.entity_encoder = self._simple_encoder(width=300)
        self.article_encoder = self._simple_encoder(width=300)

    def train_model(self, training_dir, entity_descr_output, limit=None, to_print=True):
        instances, gold_vectors, entity_descriptions, doc_by_article = self._get_training_data(training_dir,
                                                                                               entity_descr_output,
                                                                                               limit, to_print)

        if to_print:
            print("Training on", len(gold_vectors), "instances")
            print(" - pos:", len([x for x in gold_vectors if x]), "instances")
            print(" - pos:", len([x for x in gold_vectors if not x]), "instances")
            print()

        self.sgd_entity = self.begin_training(self.entity_encoder)
        self.sgd_article = self.begin_training(self.article_encoder)

        losses = {}

        for inst, label, entity_descr in zip(instances, gold_vectors, entity_descriptions):
            article = inst.split(sep="_")[0]
            entity_id = inst.split(sep="_")[1]
            article_doc = doc_by_article[article]
            self.update(article_doc, entity_descr, label, losses=losses)

    def _simple_encoder(self, width):
        with Model.define_operators({">>": chain}):
            encoder = SpacyVectors \
                      >> flatten_add_lengths \
                      >> ParametricAttention(width)\
                      >> Pooling(sum_pool) \
                      >> Residual(zero_init(Maxout(width, width)))

        return encoder

    def begin_training(self, model):
        # TODO ? link_vectors_to_models(self.vocab)
        sgd = create_default_optimizer(model.ops)
        return sgd

    def update(self, article_doc, entity_descr, label, drop=0., losses=None):
        entity_encoding, entity_bp = self.entity_encoder.begin_update([entity_descr], drop=drop)
        doc_encoding, article_bp = self.article_encoder.begin_update([article_doc], drop=drop)

        # print("entity/article output dim", len(entity_encoding[0]), len(doc_encoding[0]))

        mse, diffs = self._calculate_similarity(entity_encoding, doc_encoding)

        # print()

        # TODO: proper backpropagation taking ranking of elements into account ?
        # TODO backpropagation also for negative examples
        if label:
            entity_bp(diffs, sgd=self.sgd_entity)
            article_bp(diffs, sgd=self.sgd_article)
            print(mse)


    # TODO delete ?
    def _simple_cnn_model(self, internal_dim):
        nr_class = len(self.labels)
        with Model.define_operators({">>": chain}):
            model_entity = SpacyVectors >> flatten_add_lengths >> Pooling(mean_pool)    # entity encoding
            model_doc = SpacyVectors >> flatten_add_lengths >> Pooling(mean_pool)       # doc encoding
            output_layer = Softmax(nr_class, internal_dim*2)
            model = (model_entity | model_doc) >> output_layer
        # model.tok2vec = chain(tok2vec, flatten)
        model.nO = nr_class
        return model

    def predict(self, entity_doc, article_doc):
        entity_encoding = self.entity_encoder(entity_doc)
        doc_encoding = self.article_encoder(article_doc)

        print("entity_encodings", len(entity_encoding), entity_encoding)
        print("doc_encodings", len(doc_encoding), doc_encoding)
        mse, diffs = self._calculate_similarity(entity_encoding, doc_encoding)
        print("mse", mse)

        return mse

    def _calculate_similarity(self, vector1, vector2):
        if len(vector1) != len(vector2):
            raise ValueError("To calculate similarity, both vectors should be of equal length")

        diffs = (vector2 - vector1)
        error_sum = (diffs ** 2).sum(axis=1)
        mean_square_error = error_sum / len(vector1)
        return float(mean_square_error), diffs

    def _get_labels(self):
        return tuple(self.labels)

    def _get_training_data(self, training_dir, entity_descr_output, limit, to_print):
        id_to_descr = kb_creator._get_id_to_description(entity_descr_output)

        correct_entries, incorrect_entries = training_set_creator.read_training_entities(training_output=training_dir,
                                                                                         collect_correct=True,
                                                                                         collect_incorrect=True)

        instances = list()
        entity_descriptions = list()
        local_vectors = list()   # TODO: local vectors
        gold_vectors = list()
        doc_by_article = dict()

        cnt = 0
        for f in listdir(training_dir):
            if not limit or cnt < limit:
                if not run_el.is_dev(f):
                    article_id = f.replace(".txt", "")
                    if cnt % 500 == 0 and to_print:
                        print(datetime.datetime.now(), "processed", cnt, "files in the dev dataset")
                    cnt += 1
                    if article_id not in doc_by_article:
                        with open(os.path.join(training_dir, f), mode="r", encoding='utf8') as file:
                            text = file.read()
                            doc = self.nlp(text)
                            doc_by_article[article_id] = doc

                    for mention_pos, entity_pos in correct_entries[article_id].items():
                        descr = id_to_descr.get(entity_pos)
                        if descr:
                            instances.append(article_id + "_" + entity_pos)
                            doc = self.nlp(descr)
                            entity_descriptions.append(doc)
                            gold_vectors.append(True)

                    for mention_neg, entity_negs in incorrect_entries[article_id].items():
                        for entity_neg in entity_negs:
                            descr = id_to_descr.get(entity_neg)
                            if descr:
                                instances.append(article_id + "_" + entity_neg)
                                doc = self.nlp(descr)
                                entity_descriptions.append(doc)
                                gold_vectors.append(False)

        if to_print:
            print()
            print("Processed", cnt, "dev articles")
            print()
        return instances, gold_vectors, entity_descriptions, doc_by_article
