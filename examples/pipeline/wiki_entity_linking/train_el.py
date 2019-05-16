# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir
import numpy as np
import random
from thinc.neural._classes.convolution import ExtractWindow

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
        self._begin_training()

        if self.PRINT_F:
            _, _, f_avg_train = -3.42, -3.42, -3.42   # self._test_dev(train_instances, train_pos, train_neg, train_doc, avg=True)
            _, _, f_nonavg_train = self._test_dev(train_instances, train_pos, train_neg, train_doc, avg=False)
            _, _, f_random_train = self._test_dev(train_instances, train_pos, train_neg, train_doc, calc_random=True)
            _, _, f_avg_dev = -3.42, -3.42, -3.42   # self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc, avg=True)
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
                _, _, f_avg_train = -3.42, -3.42, -3.42  # self._test_dev(train_instances, train_pos, train_neg, train_doc, avg=True)
                _, _, f_nonavg_train = self._test_dev(train_instances, train_pos, train_neg, train_doc, avg=False)
                _, _, f_avg_dev = -3.42, -3.42, -3.42  # self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc, avg=True)
                _, _, f_nonavg_dev = self._test_dev(dev_instances, dev_pos, dev_neg, dev_doc, avg=False)

                print("avg/nonavg F train", round(f_avg_train, 1), round(f_nonavg_train, 1))
                print("avg/nonavg F dev", round(f_avg_dev, 1), round(f_nonavg_dev, 1))
                print()

        if to_print:
            print("Trained on", instance_pos_count, "/", instance_neg_count, "instances pos/neg")

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

            self.model = Affine(hidden_output_with, hidden_input_with) \
                       >> LN(Maxout(hidden_output_with, hidden_output_with)) \
                       >> convolution_2 \
                       >> Affine(self.HIDDEN_2_WIDTH, hidden_output_with) \
                       >> Affine(1, self.HIDDEN_2_WIDTH) \
                       >> logistic

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

    def _begin_training(self):
        self.sgd = create_default_optimizer(self.model.ops)

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
