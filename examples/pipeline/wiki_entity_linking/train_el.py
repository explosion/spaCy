# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir
from random import shuffle
import numpy as np

from examples.pipeline.wiki_entity_linking import run_el, training_set_creator, kb_creator

from spacy._ml import SpacyVectors, create_default_optimizer, zero_init

from thinc.api import chain, flatten_add_lengths, with_getitem, clone
from thinc.neural.util import get_array_module
from thinc.v2v import Model, Softmax, Maxout, Affine, ReLu
from thinc.t2v import Pooling, sum_pool, mean_pool
from thinc.t2t import ParametricAttention
from thinc.misc import Residual

from spacy.tokens import Doc

""" TODO: this code needs to be implemented in pipes.pyx"""


class EL_Model():

    INPUT_DIM = 300
    OUTPUT_DIM = 96
    PRINT_LOSS = False
    PRINT_F = True
    EPS = 0.0000000005

    labels = ["MATCH", "NOMATCH"]
    name = "entity_linker"

    def __init__(self, kb, nlp):
        run_el._prepare_pipeline(nlp, kb)
        self.nlp = nlp
        self.kb = kb

        self.entity_encoder = self._simple_encoder(in_width=self.INPUT_DIM, out_width=self.OUTPUT_DIM)
        self.article_encoder = self._simple_encoder(in_width=self.INPUT_DIM, out_width=self.OUTPUT_DIM)

    def train_model(self, training_dir, entity_descr_output, trainlimit=None, devlimit=None, to_print=True):
        Doc.set_extension("entity_id", default=None)

        train_instances, train_pos, train_neg, train_doc = self._get_training_data(training_dir,
                                                                                   entity_descr_output,
                                                                                   False,
                                                                                   trainlimit,
                                                                                   to_print)

        dev_instances, dev_pos, dev_neg, dev_doc = self._get_training_data(training_dir,
                                                                           entity_descr_output,
                                                                           True,
                                                                           devlimit,
                                                                           to_print)

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
            # print("article", article_id)
            article_doc = train_doc[article_id]
            pos_ex_list = list()
            neg_exs_list = list()
            for inst_cluster in inst_cluster_set:
                # print("inst_cluster", inst_cluster)
                instance_count += 1
                pos_ex_list.append(train_pos.get(inst_cluster))
                neg_exs_list.append(train_neg.get(inst_cluster, []))

            self.update(article_doc, pos_ex_list, neg_exs_list, losses=losses)
            p, r, fscore = self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc)
            if self.PRINT_F:
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

                    best_entity, highest_prob = self._predict(examples, article_doc)
                    predictions.append(ex_to_id[best_entity])
                    golds.append(ex_to_id[pos_ex])

        # TODO: use lowest_mse and combine with prior probability
        p, r, F = run_el.evaluate(predictions, golds, to_print=False)
        return p, r, F

    def _predict(self, entities, article_doc):
        doc_encoding = self.article_encoder([article_doc])

        highest_prob = None
        best_entity = None

        entity_to_vector = dict()
        for entity in entities:
            entity_to_vector[entity] = self.entity_encoder([entity])

        for entity in entities:
            entity_encoding = entity_to_vector[entity]
            prob = self._calculate_probability(doc_encoding, entity_encoding, entity_to_vector.values())
            if not best_entity or prob > highest_prob:
                highest_prob = prob
                best_entity = entity

        return best_entity, highest_prob

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
        doc_encoding, article_bp = self.article_encoder.begin_update([article_doc], drop=drop)
        doc_encoding = doc_encoding[0]
        # print("doc", doc_encoding)

        for i, true_entity in enumerate(true_entity_list):
            try:
                false_vectors = list()
                false_entities = false_entities_list[i]
                if len(false_entities) > 0:
                    # TODO: batch per doc

                    for false_entity in false_entities:
                        # TODO: one call only to begin_update ?
                        false_entity_encoding, false_entity_bp = self.entity_encoder.begin_update([false_entity], drop=drop)
                        false_entity_encoding = false_entity_encoding[0]
                        false_vectors.append(false_entity_encoding)

                    true_entity_encoding, true_entity_bp = self.entity_encoder.begin_update([true_entity], drop=drop)
                    true_entity_encoding = true_entity_encoding[0]
                    # true_gradient = self._calculate_true_gradient(doc_encoding, true_entity_encoding)

                    all_vectors = [true_entity_encoding]
                    all_vectors.extend(false_vectors)

                    # consensus_encoding = self._calculate_consensus(doc_encoding, true_entity_encoding)

                    true_prob = self._calculate_probability(doc_encoding, true_entity_encoding, all_vectors)
                    # print("true", true_prob, true_entity_encoding)
                    # print("true gradient", true_gradient)
                    # print()

                    all_probs = [true_prob]
                    for false_vector in false_vectors:
                        false_prob = self._calculate_probability(doc_encoding, false_vector, all_vectors)
                        # print("false", false_prob, false_vector)
                        # print("false gradient", false_gradient)
                        # print()
                        all_probs.append(false_prob)

                    loss = self._calculate_loss(true_prob, all_probs).astype(np.float32)
                    if self.PRINT_LOSS:
                        print(round(loss, 5))

                    #doc_gradient = self._calculate_doc_gradient(loss, doc_encoding, true_entity_encoding, false_vectors)
                    entity_gradient = self._calculate_entity_gradient(doc_encoding, true_entity_encoding, false_vectors)
                    # print("entity_gradient", entity_gradient)
                    # print("doc_gradient", doc_gradient)
                    # article_bp([doc_gradient.astype(np.float32)], sgd=self.sgd_article)
                    true_entity_bp([entity_gradient.astype(np.float32)], sgd=self.sgd_entity)
                    #true_entity_bp([true_gradient.astype(np.float32)], sgd=self.sgd_entity)
            except Exception as e:
                pass


    # TODO: FIX
    def _calculate_consensus(self, vector1, vector2):
        if len(vector1) != len(vector2):
            raise ValueError("To calculate consensus, both vectors should be of equal length")

        avg = (vector2 + vector1) / 2
        return avg

    def _calculate_probability(self, vector1, vector2, allvectors):
        """ Make sure that vector2 is included in allvectors """
        if len(vector1) != len(vector2):
            raise ValueError("To calculate similarity, both vectors should be of equal length")

        vector1_t = vector1.transpose()
        e = self._calculate_dot_exp(vector2, vector1_t)
        e_sum = 0
        for v in allvectors:
            e_sum += self._calculate_dot_exp(v, vector1_t)

        return float(e / (self.EPS + e_sum))

    def _calculate_loss(self, true_prob, all_probs):
        """ all_probs should include true_prob ! """
        return -1 * np.log((self.EPS + true_prob) / (self.EPS + sum(all_probs)))

    @staticmethod
    def _calculate_doc_gradient(loss, doc_vector, true_vector, false_vectors):
        gradient = np.zeros(len(doc_vector))
        for i in range(len(doc_vector)):
            min_false = min(x[i] for x in false_vectors)
            max_false = max(x[i] for x in false_vectors)

            if true_vector[i] > max_false:
                if doc_vector[i] > 0:
                    gradient[i] = 0
                else:
                    gradient[i] = -loss
            elif true_vector[i] < min_false:
                if doc_vector[i] > 0:
                    gradient[i] = loss
                if doc_vector[i] < 0:
                    gradient[i] = 0
            else:
                target = 0  # non-distinctive vector positions should convert to 0
                gradient[i] = doc_vector[i] - target

        return gradient

    def _calculate_true_gradient(self, doc_vector, entity_vector):
        # sum_entity_vector = sum(entity_vector)
        # gradient = [-sum_entity_vector/(self.EPS + np.exp(doc_vector[i] * entity_vector[i])) for i in range(len(doc_vector))]
        gradient = [1 / (self.EPS + np.exp(doc_vector[i] * entity_vector[i])) for i in range(len(doc_vector))]
        return np.asarray(gradient)

    def _calculate_entity_gradient(self, doc_vector, true_vector, false_vectors):
        entity_gradient = list()
        prob_true = list()
        false_prob_list = list()
        for i in range(len(true_vector)):
            doc_i = np.asarray([doc_vector[i]])
            true_i = np.asarray([true_vector[i]])
            falses_i = np.asarray([[fv[i]] for fv in false_vectors])
            all_i = [true_i]
            all_i.extend(falses_i)

            prob_true_i = self._calculate_probability(doc_i, true_i, all_i)
            prob_true.append(prob_true_i)

            false_list = list()
            all_probs_i = [prob_true_i]
            for false_vector in falses_i:
                false_prob_i = self._calculate_probability(doc_i, false_vector, all_i)
                all_probs_i.append(false_prob_i)
                false_list.append(false_prob_i)
            false_prob_list.append(false_list)

            sign_loss_i = 1
            if doc_vector[i] * true_vector[i] < 0:
                sign_loss_i = -1

            loss_i = sign_loss_i * self._calculate_loss(prob_true_i, all_probs_i).astype(np.float32)
            entity_gradient.append(loss_i)
        # print("prob_true", prob_true)
        # print("false_prob_list", false_prob_list)
        return np.asarray(entity_gradient)


    @staticmethod
    def _calculate_dot_exp(vector1, vector2_transposed):
        dot_product = vector1.dot(vector2_transposed)
        dot_product = min(50, dot_product)
        # dot_product = max(-10000, dot_product)
        # print("DOT", dot_product)
        e = np.exp(dot_product)
        # print("E", e)
        return e

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
