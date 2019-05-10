# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir
import numpy as np

from examples.pipeline.wiki_entity_linking import run_el, training_set_creator, kb_creator

from spacy._ml import SpacyVectors, create_default_optimizer, zero_init

from thinc.api import chain, flatten_add_lengths, with_getitem, clone, with_flatten
from thinc.v2v import Model, Maxout, Softmax, Affine, ReLu
from thinc.t2v import Pooling, sum_pool, mean_pool
from thinc.t2t import ExtractWindow, ParametricAttention
from thinc.misc import Residual, LayerNorm as LN

""" TODO: this code needs to be implemented in pipes.pyx"""


class EL_Model():

    labels = ["MATCH", "NOMATCH"]
    name = "entity_linker"

    def __init__(self, kb, nlp):
        run_el._prepare_pipeline(nlp, kb)
        self.nlp = nlp
        self.kb = kb

        self.entity_encoder = self._simple_encoder(in_width=300, out_width=96)
        self.article_encoder = self._simple_encoder(in_width=300, out_width=96)

    def train_model(self, training_dir, entity_descr_output, limit=None, to_print=True):
        instances, pos_entities, neg_entities, doc_by_article = self._get_training_data(training_dir,
                                                                                               entity_descr_output,
                                                                                               limit, to_print)

        if to_print:
            print("Training on", len(instances), "instance clusters")
            print()

        self.sgd_entity = self.begin_training(self.entity_encoder)
        self.sgd_article = self.begin_training(self.article_encoder)

        losses = {}

        for inst_cluster in instances:
            pos_ex = pos_entities.get(inst_cluster)
            neg_exs = neg_entities.get(inst_cluster, [])

            if pos_ex and neg_exs:
                article = inst_cluster.split(sep="_")[0]
                entity_id = inst_cluster.split(sep="_")[1]
                article_doc = doc_by_article[article]
                self.update(article_doc, pos_ex, neg_exs, losses=losses)
            # TODO
            # elif not pos_ex:
                # print("Weird. Couldn't find pos example for",  inst_cluster)
            # elif not neg_exs:
                # print("Weird. Couldn't find neg examples for",  inst_cluster)

    def _simple_encoder(self, in_width, out_width):
        conv_depth = 1
        cnn_maxout_pieces = 3
        with Model.define_operators({">>": chain, "**": clone}):
            # encoder = SpacyVectors \
            #            >> flatten_add_lengths \
            #           >> ParametricAttention(in_width)\
            #            >> Pooling(mean_pool) \
            #           >> Residual(zero_init(Maxout(in_width, in_width)))  \
            #           >> zero_init(Affine(out_width, in_width, drop_factor=0.0))
            encoder = SpacyVectors \
                     >> flatten_add_lengths \
                     >> with_getitem(0, Affine(in_width, in_width)) \
                     >> ParametricAttention(in_width) \
                     >> Pooling(sum_pool) \
                     >> Residual(ReLu(in_width, in_width)) ** conv_depth \
                     >> zero_init(Affine(out_width, in_width, drop_factor=0.0))

            # >> zero_init(Affine(nr_class, width, drop_factor=0.0))
            # >> logistic

            # convolution = Residual(
            #    ExtractWindow(nW=1)
            #    >> LN(Maxout(width, width * 3, pieces=cnn_maxout_pieces))
            # )

            # embed = SpacyVectors >> LN(Maxout(width, width, pieces=3))

            # encoder = SpacyVectors >> flatten_add_lengths >> convolution ** conv_depth
            # encoder = with_flatten(embed >> convolution ** conv_depth, pad=conv_depth)

        return encoder

    def begin_training(self, model):
        # TODO ? link_vectors_to_models(self.vocab)
        sgd = create_default_optimizer(model.ops)
        return sgd

    def update(self, article_doc, true_entity, false_entities, drop=0., losses=None):
        doc_encoding, article_bp = self.article_encoder.begin_update([article_doc], drop=drop)

        true_entity_encoding, true_entity_bp = self.entity_encoder.begin_update([true_entity], drop=drop)
        # print("encoding dim", len(true_entity_encoding[0]))

        consensus_encoding = self._calculate_consensus(doc_encoding, true_entity_encoding)
        consensus_encoding_t = consensus_encoding.transpose()

        doc_mse, doc_diffs = self._calculate_similarity(doc_encoding, consensus_encoding)

        entity_mses = list()

        true_mse, true_diffs = self._calculate_similarity(true_entity_encoding, consensus_encoding)
        # print("true_mse", true_mse)
        # print("true_diffs", true_diffs)
        entity_mses.append(true_mse)
        # true_exp = np.exp(true_entity_encoding.dot(consensus_encoding_t))
        # print("true_exp", true_exp)

        # false_exp_sum = 0

        for false_entity in false_entities:
            false_entity_encoding, false_entity_bp = self.entity_encoder.begin_update([false_entity], drop=drop)
            false_mse, false_diffs = self._calculate_similarity(false_entity_encoding, consensus_encoding)
            # print("false_mse", false_mse)
            # false_exp = np.exp(false_entity_encoding.dot(consensus_encoding_t))
            # print("false_exp", false_exp)
            # print("false_diffs", false_diffs)
            entity_mses.append(false_mse)
            # if false_mse > true_mse:
                # true_diffs = true_diffs - false_diffs ???
            # false_exp_sum += false_exp

        # prob = true_exp / false_exp_sum
        # print("prob", prob)

        entity_mses = sorted(entity_mses)
        # mse_sum = sum(entity_mses)
        # entity_probs = [1 - x/mse_sum for x in entity_mses]
        # print("entity_mses", entity_mses)
        # print("entity_probs", entity_probs)
        true_index = entity_mses.index(true_mse)
        # print("true index", true_index)
        # print("true prob", entity_probs[true_index])

        print(true_mse)

        # print()

        # TODO: proper backpropagation taking ranking of elements into account ?
        # TODO backpropagation also for negative examples
        true_entity_bp(true_diffs, sgd=self.sgd_entity)
        article_bp(doc_diffs, sgd=self.sgd_article)


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

    # TODO: expand to more than 2 vectors
    def _calculate_consensus(self, vector1, vector2):
        if len(vector1) != len(vector2):
            raise ValueError("To calculate consenus, both vectors should be of equal length")

        avg = (vector2 + vector1) / 2
        return avg

    def _calculate_similarity(self, vector1, vector2):
        if len(vector1) != len(vector2):
            raise ValueError("To calculate similarity, both vectors should be of equal length")

        diffs = (vector1 - vector2)
        error_sum = (diffs ** 2).sum()
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
        local_vectors = list()   # TODO: local vectors
        doc_by_article = dict()
        pos_entities = dict()
        neg_entities = dict()

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

                    for mention, entity_pos in correct_entries[article_id].items():
                        descr = id_to_descr.get(entity_pos)
                        if descr:
                            instances.append(article_id + "_" + mention)
                            doc_descr = self.nlp(descr)
                            pos_entities[article_id + "_" + mention] = doc_descr

                    for mention, entity_negs in incorrect_entries[article_id].items():
                        for entity_neg in entity_negs:
                            descr = id_to_descr.get(entity_neg)
                            if descr:
                                doc_descr = self.nlp(descr)
                                descr_list = neg_entities.get(article_id + "_" + mention, [])
                                descr_list.append(doc_descr)
                                neg_entities[article_id + "_" + mention] = descr_list

        if to_print:
            print()
            print("Processed", cnt, "dev articles")
            print()
        return instances, pos_entities, neg_entities, doc_by_article
