# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir
import numpy as np
from random import shuffle

from examples.pipeline.wiki_entity_linking import run_el, training_set_creator, kb_creator

from spacy._ml import SpacyVectors, create_default_optimizer, zero_init

from thinc.api import chain, flatten_add_lengths, with_getitem, clone, with_flatten
from thinc.v2v import Model, Maxout, Softmax, Affine, ReLu
from thinc.t2v import Pooling, sum_pool, mean_pool
from thinc.t2t import ExtractWindow, ParametricAttention
from thinc.misc import Residual, LayerNorm as LN

from spacy.tokens import Doc

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
        Doc.set_extension("entity_id", default=None)

        train_instances, train_pos, train_neg, train_doc = self._get_training_data(training_dir,
                                                                                   entity_descr_output,
                                                                                   False,
                                                                                   limit, to_print)

        dev_instances, dev_pos, dev_neg, dev_doc = self._get_training_data(training_dir,
                                                                           entity_descr_output,
                                                                           True,
                                                                           limit / 10, to_print)

        if to_print:
            print("Training on", len(train_instances.values()), "articles")
            print("Dev test on", len(dev_instances.values()), "articles")
            print()

        self.sgd_entity = self.begin_training(self.entity_encoder)
        self.sgd_article = self.begin_training(self.article_encoder)

        self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc)

        losses = {}

        instance_count = 0

        for article_id, inst_cluster_set in train_instances.items():
            article_doc = train_doc[article_id]
            pos_ex_list = list()
            neg_exs_list = list()
            for inst_cluster in inst_cluster_set:
                instance_count += 1
                pos_ex_list.append(train_pos.get(inst_cluster))
                neg_exs_list.append(train_neg.get(inst_cluster, []))

            self.update(article_doc, pos_ex_list, neg_exs_list, losses=losses)
            p, r, fscore = self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc)
            print(round(fscore, 1))

        if to_print:
            print("Trained on", instance_count, "instance clusters")


    def _test_dev(self, dev_instances, dev_pos, dev_neg, dev_doc):
        predictions = list()
        golds = list()

        for article_id, inst_cluster_set in dev_instances.items():
            for inst_cluster in inst_cluster_set:
                pos_ex = dev_pos.get(inst_cluster)
                neg_exs = dev_neg.get(inst_cluster, [])
                ex_to_id = dict()

                if pos_ex and neg_exs:
                    ex_to_id[pos_ex] = pos_ex._.entity_id
                    for neg_ex in neg_exs:
                        ex_to_id[neg_ex] = neg_ex._.entity_id

                    article = inst_cluster.split(sep="_")[0]
                    entity_id = inst_cluster.split(sep="_")[1]
                    article_doc = dev_doc[article]

                    examples = list(neg_exs)
                    examples.append(pos_ex)
                    shuffle(examples)

                    best_entity, lowest_mse = self._predict(examples, article_doc)
                    predictions.append(ex_to_id[best_entity])
                    golds.append(ex_to_id[pos_ex])

        # TODO: use lowest_mse and combine with prior probability
        p, r, F = run_el.evaluate(predictions, golds, to_print=False)
        return p, r, F

    def _predict(self, entities, article_doc):
        doc_encoding = self.article_encoder([article_doc])

        lowest_mse = None
        best_entity = None

        for entity in entities:
            entity_encoding = self.entity_encoder([entity])
            mse, _ = self._calculate_similarity(doc_encoding, entity_encoding)
            if not best_entity or mse < lowest_mse:
                lowest_mse = mse
                best_entity = entity

        return best_entity, lowest_mse

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

    def update(self, article_doc, true_entity_list, false_entities_list, drop=0., losses=None):
        # TODO: one call only to begin_update ?

        entity_diffs = None
        doc_diffs = None

        doc_encoding, article_bp = self.article_encoder.begin_update([article_doc], drop=drop)

        for i, true_entity in enumerate(true_entity_list):
            false_entities = false_entities_list[i]

            true_entity_encoding, true_entity_bp = self.entity_encoder.begin_update([true_entity], drop=drop)
            # print("encoding dim", len(true_entity_encoding[0]))

            consensus_encoding = self._calculate_consensus(doc_encoding, true_entity_encoding)
            # consensus_encoding_t = consensus_encoding.transpose()

            doc_mse, doc_diff = self._calculate_similarity(doc_encoding, consensus_encoding)

            entity_mses = list()

            true_mse, true_diffs = self._calculate_similarity(true_entity_encoding, consensus_encoding)
            # print("true_mse", true_mse)
            # print("true_diffs", true_diffs)
            entity_mses.append(true_mse)
            # true_exp = np.exp(true_entity_encoding.dot(consensus_encoding_t))
            # print("true_exp", true_exp)

            # false_exp_sum = 0

            if doc_diffs is not None:
                doc_diffs += doc_diff
                entity_diffs += true_diffs
            else:
                doc_diffs = doc_diff
                entity_diffs = true_diffs

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

            # print("training loss", true_mse)

            # print()

        # TODO: proper backpropagation taking ranking of elements into account ?
        # TODO backpropagation also for negative examples

        if doc_diffs is not None:
            doc_diffs = doc_diffs / len(true_entity_list)

            true_entity_bp(entity_diffs, sgd=self.sgd_entity)
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

    def _get_training_data(self, training_dir, entity_descr_output, dev, limit, to_print):
        id_to_descr = kb_creator._get_id_to_description(entity_descr_output)

        correct_entries, incorrect_entries = training_set_creator.read_training_entities(training_output=training_dir,
                                                                                         collect_correct=True,
                                                                                         collect_incorrect=True)


        instance_by_doc = dict()
        local_vectors = list()   # TODO: local vectors
        doc_by_article = dict()
        pos_entities = dict()
        neg_entities = dict()

        cnt = 0
        for f in listdir(training_dir):
            if not limit or cnt < limit:
                if dev == run_el.is_dev(f):
                    article_id = f.replace(".txt", "")
                    if cnt % 500 == 0 and to_print:
                        print(datetime.datetime.now(), "processed", cnt, "files in the training dataset")
                    cnt += 1
                    if article_id not in doc_by_article:
                        with open(os.path.join(training_dir, f), mode="r", encoding='utf8') as file:
                            text = file.read()
                            doc = self.nlp(text)
                            doc_by_article[article_id] = doc
                            instance_by_doc[article_id] = set()

                    for mention, entity_pos in correct_entries[article_id].items():
                        descr = id_to_descr.get(entity_pos)
                        if descr:
                            instance_by_doc[article_id].add(article_id + "_" + mention)
                            doc_descr = self.nlp(descr)
                            doc_descr._.entity_id = entity_pos
                            pos_entities[article_id + "_" + mention] = doc_descr

                    for mention, entity_negs in incorrect_entries[article_id].items():
                        for entity_neg in entity_negs:
                            descr = id_to_descr.get(entity_neg)
                            if descr:
                                doc_descr = self.nlp(descr)
                                doc_descr._.entity_id = entity_neg
                                descr_list = neg_entities.get(article_id + "_" + mention, [])
                                descr_list.append(doc_descr)
                                neg_entities[article_id + "_" + mention] = descr_list

        if to_print:
            print()
            print("Processed", cnt, "training articles, dev=" + str(dev))
            print()
        return instance_by_doc, pos_entities, neg_entities, doc_by_article
