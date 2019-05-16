# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir
from random import shuffle
import numpy as np
import random
from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural._classes.feature_extracter import FeatureExtracter

from examples.pipeline.wiki_entity_linking import run_el, training_set_creator, kb_creator

from spacy._ml import SpacyVectors, create_default_optimizer, zero_init, logistic

from thinc.api import chain, concatenate, flatten_add_lengths, with_getitem, clone, with_flatten
from thinc.neural.util import get_array_module
from thinc.v2v import Model, Softmax, Maxout, Affine, ReLu
from thinc.t2v import Pooling, sum_pool, mean_pool, max_pool
from thinc.t2t import ParametricAttention
from thinc.misc import Residual
from thinc.misc import LayerNorm as LN

from spacy.tokens import Doc

""" TODO: this code needs to be implemented in pipes.pyx"""


class EL_Model:

    PRINT_LOSS = True
    PRINT_F = True
    EPS = 0.0000000005
    CUTOFF = 0.5

    INPUT_DIM = 300
    ENTITY_WIDTH = 64
    ARTICLE_WIDTH = 64
    HIDDEN_1_WIDTH = 256
    HIDDEN_2_WIDTH = 64

    name = "entity_linker"

    def __init__(self, kb, nlp):
        run_el._prepare_pipeline(nlp, kb)
        self.nlp = nlp
        self.kb = kb

        self._build_cnn(hidden_entity_width=self.ENTITY_WIDTH, hidden_article_width=self.ARTICLE_WIDTH)

        # self.entity_encoder = self._simple_encoder(in_width=self.INPUT_DIM, out_width=self.OUTPUT_DIM)
        # self.article_encoder = self._simple_encoder(in_width=self.INPUT_DIM, out_width=self.OUTPUT_DIM)

    def train_model(self, training_dir, entity_descr_output, trainlimit=None, devlimit=None, to_print=True):
        # raise errors instead of runtime warnings in case of int/float overflow
        np.seterr(all='raise')

        Doc.set_extension("entity_id", default=None)

        train_instances, train_pos, train_neg, train_doc = self._get_training_data(training_dir,
                                                                                   entity_descr_output,
                                                                                   False,
                                                                                   trainlimit,
                                                                                   to_print=False)

        dev_instances, dev_pos, dev_neg, dev_doc = self._get_training_data(training_dir,
                                                                           entity_descr_output,
                                                                           True,
                                                                           devlimit,
                                                                           to_print=False)

        # self.sgd_entity = self.begin_training(self.entity_encoder)
        # self.sgd_article = self.begin_training(self.article_encoder)
        self._begin_training()

        if self.PRINT_F:
            _, _, f_avg_train = -3.42, -3.42, -3.42 # self._test_dev(train_instances, train_pos, train_neg, train_doc, avg=True)
            _, _, f_nonavg_train = self._test_dev(train_instances, train_pos, train_neg, train_doc, avg=False)
            _, _, f_random_train = self._test_dev(train_instances, train_pos, train_neg, train_doc, calc_random=True)
            _, _, f_avg_dev = -3.42, -3.42, -3.42 # self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc, avg=True)
            _, _, f_nonavg_dev = self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc, avg=False)
            _, _, f_random_dev = self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc, calc_random=True)

            print("random F train", round(f_random_train, 1))
            print("random F dev", round(f_random_dev, 1))
            print()
            print("avg/nonavg F train", round(f_avg_train, 1), round(f_nonavg_train, 1))
            print("avg/nonavg F dev", round(f_avg_dev, 1), round(f_nonavg_dev, 1))
            print()

        instance_pos_count = 0
        instance_neg_count = 0

        if to_print:
            print("Training on", len(train_instances.values()), "articles")
            print("Dev test on", len(dev_instances.values()), "articles")
            print()

        # for article_id, inst_cluster_set in train_instances.items():
            # article_doc = train_doc[article_id]
            # print("training on", article_id, inst_cluster_set)
            # pos_ex_list = list()
            # neg_exs_list = list()
            # for inst_cluster in inst_cluster_set:
                # instance_count += 1
                # pos_ex_list.append(train_pos.get(inst_cluster))
                # neg_exs_list.append(train_neg.get(inst_cluster, []))

            #self.update(article_doc, pos_ex_list, neg_exs_list)

        article_docs = list()
        entities = list()
        golds = list()
        for article_id, inst_cluster_set in train_instances.items():
            for inst_cluster in inst_cluster_set:
                article_docs.append(train_doc[article_id])
                entities.append(train_pos.get(inst_cluster))
                golds.append(float(1.0))
                instance_pos_count += 1
                for neg_entity in train_neg.get(inst_cluster, []):
                    article_docs.append(train_doc[article_id])
                    entities.append(neg_entity)
                    golds.append(float(0.0))
                    instance_neg_count += 1

        for x in range(10):
            print("Updating", x)
            self.update(article_docs=article_docs, entities=entities, golds=golds)

            # eval again
            if self.PRINT_F:
                _, _, f_avg_train = -3.42, -3.42, -3.42 # self._test_dev(train_instances, train_pos, train_neg, train_doc, avg=True)
                _, _, f_nonavg_train = self._test_dev(train_instances, train_pos, train_neg, train_doc, avg=False)
                _, _, f_avg_dev = -3.42, -3.42, -3.42 # self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc, avg=True)
                _, _, f_nonavg_dev = self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc, avg=False)

                print("avg/nonavg F train", round(f_avg_train, 1), round(f_nonavg_train, 1))
                print("avg/nonavg F dev", round(f_avg_dev, 1), round(f_nonavg_dev, 1))
                print()

        if to_print:
            print("Trained on", instance_pos_count, "/", instance_neg_count, "instances pos/neg")

    def _test_dev_depr(self, dev_instances, dev_pos, dev_neg, dev_doc, avg=False, calc_random=False):
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

                    best_entity, highest_prob = self._predict(examples, article_doc, avg)
                    if calc_random:
                        best_entity, highest_prob = self._predict_random(examples)
                    predictions.append(ex_to_id[best_entity])
                    golds.append(ex_to_id[pos_ex])

        # TODO: use lowest_mse and combine with prior probability
        p, r, f = run_el.evaluate(predictions, golds, to_print=False)
        return p, r, f

    def _test_dev(self, dev_instances, dev_pos, dev_neg, dev_doc, avg=False, calc_random=False):
        predictions = list()
        golds = list()

        for article_id, inst_cluster_set in dev_instances.items():
            for inst_cluster in inst_cluster_set:
                pos_ex = dev_pos.get(inst_cluster)
                neg_exs = dev_neg.get(inst_cluster, [])

                article = inst_cluster.split(sep="_")[0]
                entity_id = inst_cluster.split(sep="_")[1]
                article_doc = dev_doc[article]

                if calc_random:
                    prediction = self._predict_random(entity=pos_ex)
                else:
                    prediction = self._predict(article_doc=article_doc, entity=pos_ex, avg=avg)
                predictions.append(prediction)
                golds.append(float(1.0))

                for neg_ex in neg_exs:
                    if calc_random:
                        prediction = self._predict_random(entity=neg_ex)
                    else:
                        prediction = self._predict(article_doc=article_doc, entity=neg_ex, avg=avg)
                    predictions.append(prediction)
                    golds.append(float(0.0))

        # TODO: use lowest_mse and combine with prior probability
        p, r, f = run_el.evaluate(predictions, golds, to_print=False)
        return p, r, f

    def _predict_depr(self, entities, article_doc, avg=False):
        if avg:
            with self.article_encoder.use_params(self.sgd_article.averages):
                doc_encoding = self.article_encoder([article_doc])
        else:
            doc_encoding = self.article_encoder([article_doc])

        highest_prob = None
        best_entity = None

        entity_to_vector = dict()
        for entity in entities:
            if avg:
                with self.entity_encoder.use_params(self.sgd_entity.averages):
                    entity_to_vector[entity] = self.entity_encoder([entity])
            else:
                entity_to_vector[entity] = self.entity_encoder([entity])

        for entity in entities:
            entity_encoding = entity_to_vector[entity]
            prob = self._calculate_probability(doc_encoding, entity_encoding, entity_to_vector.values())
            if not best_entity or prob > highest_prob:
                highest_prob = prob
                best_entity = entity

        return best_entity, highest_prob

    def _predict(self, article_doc, entity, avg=False, apply_threshold=True):
        if avg:
            with self.sgd.use_params(self.model.averages):
                doc_encoding = self.article_encoder([article_doc])
                entity_encoding = self.entity_encoder([entity])
                return self.model(np.append(entity_encoding, doc_encoding))  # TODO list

        doc_encoding = self.article_encoder([article_doc])[0]
        entity_encoding = self.entity_encoder([entity])[0]
        concat_encoding = list(entity_encoding) + list(doc_encoding)
        np_array = np.asarray([concat_encoding])
        prediction = self.model(np_array)
        if not apply_threshold:
            return float(prediction)
        if prediction > self.CUTOFF:
            return float(1.0)
        return float(0.0)

    def _predict_random_depr(self, entities):
        highest_prob = 1
        best_entity = random.choice(entities)
        return best_entity, highest_prob

    def _predict_random(self, entity, apply_threshold=True):
        r = random.uniform(0, 1)
        if not apply_threshold:
            return r
        if r > self.CUTOFF:
            return float(1.0)
        return float(0.0)

    def _build_cnn(self, hidden_entity_width, hidden_article_width):
        with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
            self.entity_encoder = self._encoder(in_width=self.INPUT_DIM, hidden_width=hidden_entity_width)  # entity encoding
            self.article_encoder = self._encoder(in_width=self.INPUT_DIM, hidden_width=hidden_article_width)  # doc encoding

            hidden_input_with = hidden_entity_width + hidden_article_width
            hidden_output_with = self.HIDDEN_1_WIDTH

            convolution_2 = Residual((ExtractWindow(nW=1) >> LN(Maxout(hidden_output_with, hidden_output_with * 3))))

            # self.entity_encoder | self.article_encoder \
            # self.model = with_flatten(LN(Maxout(hidden_with, hidden_with)) >> convolution_2 ** 2, pad=2)  \
            #          >> flatten_add_lengths \
            #          >> ParametricAttention(hidden_with) \
            #          >> Pooling(sum_pool) \
            #          >> Softmax(nr_class, nr_class)

            self.model = Affine(hidden_output_with, hidden_input_with) \
                       >> LN(Maxout(hidden_output_with, hidden_output_with)) \
                       >> convolution_2 \
                       >> Affine(self.HIDDEN_2_WIDTH, hidden_output_with) \
                       >> Affine(1, self.HIDDEN_2_WIDTH) \
                       >> logistic
                       # >> with_flatten(LN(Maxout(hidden_output_with, hidden_output_with)) >> convolution_2 ** 2, pad=2)

                    #  >> convolution_2 \

                       #  >> flatten_add_lengths
                       #  >> ParametricAttention(hidden_output_with) \
                       #  >> Pooling(max_pool) \
                       #  >> Softmax(nr_class, nr_class)

        # self.model.nO = nr_class

    @staticmethod
    def _encoder(in_width, hidden_width):
        with Model.define_operators({">>": chain}):
            encoder = SpacyVectors \
                >> flatten_add_lengths \
                >> ParametricAttention(in_width)\
                >> Pooling(mean_pool) \
                >> Residual(zero_init(Maxout(in_width, in_width)))  \
                >> zero_init(Affine(hidden_width, in_width, drop_factor=0.0))

        return encoder

    def begin_training_depr(self, model):
        # TODO ? link_vectors_to_models(self.vocab) depr?
        sgd = create_default_optimizer(model.ops)
        return sgd

    def _begin_training(self):
        # self.sgd_entity = self.begin_training(self.entity_encoder)
        # self.sgd_article = self.begin_training(self.article_encoder)
        self.sgd = create_default_optimizer(self.model.ops)

    # TODO: deprecated ?
    def _simple_encoder_depr(self, in_width, out_width):
        hidden_with = 128

        conv_depth = 1
        cnn_maxout_pieces = 3
        with Model.define_operators({">>": chain, "**": clone}):
            # encoder = SpacyVectors \
            #            >> flatten_add_lengths \
            #           >> ParametricAttention(in_width)\
            #            >> Pooling(mean_pool) \
            #           >> Residual(zero_init(Maxout(in_width, in_width)))  \
            #           >> zero_init(Affine(out_width, in_width, drop_factor=0.0))
            # encoder = SpacyVectors \
            #         >> flatten_add_lengths \
            #         >> with_getitem(0, Affine(in_width, in_width)) \
            #         >> ParametricAttention(in_width) \
            #         >> Pooling(sum_pool) \
            #         >> Residual(ReLu(in_width, in_width)) ** conv_depth \
            #         >> zero_init(Affine(out_width, in_width, drop_factor=0.0))
            # encoder = SpacyVectors \
            #        >> flatten_add_lengths \
            #        >> ParametricAttention(in_width)\
            #        >> Pooling(sum_pool) \
            #        >> Residual(zero_init(Maxout(in_width, in_width)))  \
            #        >> zero_init(Affine(out_width, in_width, drop_factor=0.0))

            # >> zero_init(Affine(nr_class, width, drop_factor=0.0))
            # >> logistic

            #convolution = Residual(ExtractWindow(nW=1)
            #                       >> LN(Maxout(in_width, in_width * 3, pieces=cnn_maxout_pieces))
            #)
            #encoder = SpacyVectors >> with_flatten(
            #    embed >> convolution ** conv_depth, pad=conv_depth
            #)

            # static_vectors = SpacyVectors >> with_flatten(
            #    Affine(in_width, in_width)
            #)

            convolution_2 = Residual((ExtractWindow(nW=1) >> LN(Maxout(hidden_with, hidden_with * 3))))

            encoder = SpacyVectors >> with_flatten(LN(Maxout(hidden_with, in_width)) >> convolution_2 ** 2, pad = 2)  \
                      >> flatten_add_lengths \
                      >> ParametricAttention(hidden_with) \
                      >> Pooling(sum_pool) \
                      >> Residual(zero_init(Maxout(hidden_with, hidden_with))) \
                      >> zero_init(Affine(out_width, hidden_with, drop_factor=0.0)) \
                      >> logistic

            # convolution = Residual(ExtractWindow(nW=1) >> ReLu(in_width, in_width*3))

            # encoder = static_vectors # >> with_flatten(
            #    ReLu(in_width, in_width)
            #    >> convolution ** conv_depth, pad=conv_depth) \
            #    >> Affine(out_width, in_width, drop_factor=0.0)

            # encoder = SpacyVectors >> with_flatten(
            #    LN(Maxout(in_width, in_width))
            #    >> Residual((ExtractWindow(nW=1) >> LN(Maxout(in_width, in_width * 3, pieces=cnn_maxout_pieces)))) ** conv_depth,
            #    pad=conv_depth,
            #)  >> zero_init(Affine(out_width, in_width, drop_factor=0.0))

            # embed = SpacyVectors >> LN(Maxout(width, width, pieces=3))

            # encoder = SpacyVectors >> flatten_add_lengths >> convolution ** conv_depth
            # encoder = with_flatten(embed >> convolution ** conv_depth, pad=conv_depth)

        return encoder

    def update_depr(self, article_doc, true_entity_list, false_entities_list, drop=0., losses=None):
        doc_encoding, article_bp = self.article_encoder.begin_update([article_doc], drop=drop)
        doc_encoding = doc_encoding[0]
        # print()
        # print("doc", doc_encoding)

        for i, true_entity in enumerate(true_entity_list):
            try:
                false_entities = false_entities_list[i]
                if len(false_entities) > 0:
                    # TODO: batch per doc

                    all_entities = [true_entity]
                    all_entities.extend(false_entities)

                    entity_encodings, entity_bp = self.entity_encoder.begin_update(all_entities, drop=drop)
                    true_entity_encoding = entity_encodings[0]
                    false_entity_encodings = entity_encodings[1:]

                    all_vectors = [true_entity_encoding]
                    all_vectors.extend(false_entity_encodings)

                    # consensus_encoding = self._calculate_consensus(doc_encoding, true_entity_encoding)

                    true_prob = self._calculate_probability(doc_encoding, true_entity_encoding, all_vectors)
                    # print("true", true_prob, true_entity_encoding)

                    all_probs = [true_prob]
                    for false_vector in false_entity_encodings:
                        false_prob = self._calculate_probability(doc_encoding, false_vector, all_vectors)
                        # print("false", false_prob, false_vector)
                        all_probs.append(false_prob)

                    loss = self._calculate_loss(true_prob, all_probs).astype(np.float32)
                    if self.PRINT_LOSS:
                        print("loss train", round(loss, 5))

                    # for false_vector in false_vectors:
                    #    false_gradient = -1 * self._calculate_entity_gradient(loss, doc_encoding, false_vector, false_vectors)
                    #    print("false gradient", false_gradient)

                    # doc_gradient = self._calculate_doc_gradient(loss, doc_encoding, true_entity_encoding, false_entity_encodings)
                    true_gradient, doc_gradient = self._calculate_entity_gradient(loss, doc_encoding, true_entity_encoding, false_entity_encodings)
                    # print("true_gradient", true_gradient)
                    # print("doc_gradient", doc_gradient)
                    article_bp([doc_gradient.astype(np.float32)], sgd=self.sgd_article)
                    entity_bp([true_gradient.astype(np.float32)], sgd=self.sgd_entity)
                    #true_entity_bp([true_gradient.astype(np.float32)], sgd=self.sgd_entity)
            except Exception as e:
                pass

    def update(self, article_docs, entities, golds, drop=0.):
        doc_encodings, bp_doc = self.article_encoder.begin_update(article_docs, drop=drop)
        entity_encodings, bp_encoding = self.entity_encoder.begin_update(entities, drop=drop)
        concat_encodings = [list(entity_encodings[i]) + list(doc_encodings[i]) for i in range(len(entities))]

        predictions, bp_model = self.model.begin_update(np.asarray(concat_encodings), drop=drop)

        predictions = self.model.ops.flatten(predictions)
        golds = self.model.ops.asarray(golds)

        # print("predictions", predictions)
        # print("golds", golds)

        d_scores = (predictions - golds) # / predictions.shape[0]
        # print("d_scores (1)", d_scores)

        loss = (d_scores ** 2).sum()

        if self.PRINT_LOSS:
            print("loss train", round(loss, 5))

        d_scores = d_scores.reshape((-1, 1))
        d_scores = d_scores.astype(np.float32)
        # print("d_scores (2)", d_scores)

        model_gradient = bp_model(d_scores, sgd=self.sgd)

        doc_gradient = [x[0:self.ARTICLE_WIDTH] for x in model_gradient]
        entity_gradient = [x[self.ARTICLE_WIDTH:] for x in model_gradient]

        bp_doc(doc_gradient)
        bp_encoding(entity_gradient)

    def _calculate_probability_depr(self, vector1, vector2, allvectors):
        """ Make sure that vector2 is included in allvectors """
        if len(vector1) != len(vector2):
            raise ValueError("To calculate similarity, both vectors should be of equal length")

        vector1_t = vector1.transpose()
        e = self._calculate_dot_exp(vector2, vector1_t)
        e_sum = 0
        for v in allvectors:
            e_sum += self._calculate_dot_exp(v, vector1_t)

        return float(e / (self.EPS + e_sum))

    def _calculate_loss_depr(self, true_prob, all_probs):
        """ all_probs should include true_prob ! """
        return -1 * np.log((self.EPS + true_prob) / (self.EPS + sum(all_probs)))

    @staticmethod
    def _calculate_doc_gradient_depr(loss, doc_vector, true_vector, false_vectors):
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
                # non-distinctive vector positions should converge to 0
                gradient[i] = doc_vector[i]

        return gradient

    # TODO: delete ? try again ?
    def depr__calculate_true_gradient(self, doc_vector, entity_vector):
        # sum_entity_vector = sum(entity_vector)
        # gradient = [-sum_entity_vector/(self.EPS + np.exp(doc_vector[i] * entity_vector[i])) for i in range(len(doc_vector))]
        gradient = [1 / (self.EPS + np.exp(doc_vector[i] * entity_vector[i])) for i in range(len(doc_vector))]
        return np.asarray(gradient)

    def _calculate_losses_vector_depr(self, doc_vector, true_vector, false_vectors):
        # prob_true = list()
        # prob_false_dict = dict()

        true_losses = list()
        # false_losses_dict = dict()

        for i in range(len(true_vector)):
            doc_i = np.asarray([doc_vector[i]])
            true_i = np.asarray([true_vector[i]])
            falses_i = np.asarray([[fv[i]] for fv in false_vectors])
            all_i = [true_i]
            all_i.extend(falses_i)

            prob_true_i = self._calculate_probability(doc_i, true_i, all_i)
            # prob_true.append(prob_true_i)

            # false_list = list()
            all_probs_i = [prob_true_i]
            for false_i in falses_i:
                prob_false_i = self._calculate_probability(doc_i, false_i, all_i)
                all_probs_i.append(prob_false_i)
                # false_list.append(prob_false_i)
            # prob_false_dict[i] = false_list

            true_loss_i = self._calculate_loss(prob_true_i, all_probs_i).astype(np.float32)
            if doc_vector[i] > 0:
                true_loss_i = -1 * true_loss_i
            true_losses.append(true_loss_i)

            # false_loss_list = list()
            # for prob_false_i in false_list:
                # false_loss_i = self._calculate_loss(prob_false_i, all_probs_i).astype(np.float32)
                # false_loss_list.append(false_loss_i)
            # false_losses_dict[i] = false_loss_list

        return true_losses  # , false_losses_dict

    def _calculate_entity_gradient_depr(self, loss, doc_vector, true_vector, false_vectors):
        true_losses = self._calculate_losses_vector(doc_vector, true_vector, false_vectors)

        # renormalize the gradient so that the total sum of abs values does not exceed the actual loss
        loss_i = sum([abs(x) for x in true_losses])  # sum of absolute values
        entity_gradient = [(x/2) * (loss/loss_i) for x in true_losses]
        doc_gradient = [(x/2) * (loss/loss_i) for x in true_losses]

        return np.asarray(entity_gradient), np.asarray(doc_gradient)


    @staticmethod
    def _calculate_dot_exp_depr(vector1, vector2_transposed):
        dot_product = vector1.dot(vector2_transposed)
        dot_product = min(50, dot_product)
        dot_product = max(-10000, dot_product)
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
