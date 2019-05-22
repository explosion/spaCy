# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir
import numpy as np
import random
from random import shuffle
from thinc.neural._classes.convolution import ExtractWindow

from examples.pipeline.wiki_entity_linking import run_el, training_set_creator, kb_creator

from spacy._ml import SpacyVectors, create_default_optimizer, zero_init, logistic

from thinc.api import chain, concatenate, flatten_add_lengths, clone, with_flatten
from thinc.v2v import Model, Maxout, Affine, ReLu
from thinc.t2v import Pooling, mean_pool, sum_pool
from thinc.t2t import ParametricAttention
from thinc.misc import Residual
from thinc.misc import LayerNorm as LN

from spacy.tokens import Doc

""" TODO: this code needs to be implemented in pipes.pyx"""


class EL_Model:

    PRINT_TRAIN = False
    EPS = 0.0000000005
    CUTOFF = 0.5

    BATCH_SIZE = 5

    INPUT_DIM = 300
    HIDDEN_1_WIDTH = 32   # 10
    HIDDEN_2_WIDTH = 32  # 6
    DESC_WIDTH = 64     # 4
    ARTICLE_WIDTH = 64   # 8

    DROP = 0.1

    name = "entity_linker"

    def __init__(self, kb, nlp):
        run_el._prepare_pipeline(nlp, kb)
        self.nlp = nlp
        self.kb = kb

        self._build_cnn(in_width=self.INPUT_DIM,
                        desc_width=self.DESC_WIDTH,
                        article_width=self.ARTICLE_WIDTH,
                        hidden_1_width=self.HIDDEN_1_WIDTH,
                        hidden_2_width=self.HIDDEN_2_WIDTH)

    def train_model(self, training_dir, entity_descr_output, trainlimit=None, devlimit=None, to_print=True):
        # raise errors instead of runtime warnings in case of int/float overflow
        np.seterr(all='raise')

        train_ent, train_gold, train_desc, train_article, train_texts = self._get_training_data(training_dir,
                                                                                                entity_descr_output,
                                                                                                False,
                                                                                                trainlimit,
                                                                                                to_print=False)

        train_pos_entities = [k for k,v in train_gold.items() if v]
        train_neg_entities = [k for k,v in train_gold.items() if not v]

        train_pos_count = len(train_pos_entities)
        train_neg_count = len(train_neg_entities)

        # upsample positives to 50-50 distribution
        while train_pos_count < train_neg_count:
            train_ent.append(random.choice(train_pos_entities))
            train_pos_count += 1

        # upsample negatives to 50-50 distribution
        while train_neg_count < train_pos_count:
            train_ent.append(random.choice(train_neg_entities))
            train_neg_count += 1

        shuffle(train_ent)

        dev_ent, dev_gold, dev_desc, dev_article, dev_texts = self._get_training_data(training_dir,
                                                                                      entity_descr_output,
                                                                                      True,
                                                                                      devlimit,
                                                                                      to_print=False)
        shuffle(dev_ent)

        dev_pos_count = len([g for g in dev_gold.values() if g])
        dev_neg_count = len([g for g in dev_gold.values() if not g])

        self._begin_training()

        print()
        self._test_dev(dev_ent, dev_gold, dev_desc, dev_article, dev_texts, print_string="dev_random", calc_random=True)
        print()
        self._test_dev(dev_ent, dev_gold, dev_desc, dev_article, dev_texts, print_string="dev_pre", avg=True)

        if to_print:
            print()
            print("Training on", len(train_ent), "entities in", len(train_texts), "articles")
            print("Training instances pos/neg", train_pos_count, train_neg_count)
            print()
            print("Dev test on", len(dev_ent), "entities in", len(dev_texts), "articles")
            print("Dev instances pos/neg", dev_pos_count, dev_neg_count)
            print()
            print(" CUTOFF", self.CUTOFF)
            print(" INPUT_DIM", self.INPUT_DIM)
            print(" HIDDEN_1_WIDTH", self.HIDDEN_1_WIDTH)
            print(" DESC_WIDTH", self.DESC_WIDTH)
            print(" ARTICLE_WIDTH", self.ARTICLE_WIDTH)
            print(" HIDDEN_2_WIDTH", self.HIDDEN_2_WIDTH)
            print(" DROP", self.DROP)
            print()

        start = 0
        stop = min(self.BATCH_SIZE, len(train_ent))
        processed = 0

        while start < len(train_ent):
            next_batch = train_ent[start:stop]

            golds = [train_gold[e] for e in next_batch]
            descs = [train_desc[e] for e in next_batch]
            articles = [train_texts[train_article[e]] for e in next_batch]

            self.update(entities=next_batch, golds=golds, descs=descs, texts=articles)
            self._test_dev(dev_ent, dev_gold, dev_desc, dev_article, dev_texts, print_string="dev_inter", avg=True)

            processed += len(next_batch)

            start = start + self.BATCH_SIZE
            stop = min(stop + self.BATCH_SIZE, len(train_ent))

        if to_print:
            print()
            print("Trained on", processed, "entities in total")

    def _test_dev(self, entities, gold_by_entity, desc_by_entity, article_by_entity, texts_by_id, print_string, avg=True, calc_random=False):
        golds = [gold_by_entity[e] for e in entities]

        if calc_random:
            predictions = self._predict_random(entities=entities)

        else:
            desc_docs = self.nlp.pipe([desc_by_entity[e] for e in entities])
            article_docs = self.nlp.pipe([texts_by_id[article_by_entity[e]] for e in entities])
            predictions = self._predict(entities=entities, article_docs=article_docs, desc_docs=desc_docs, avg=avg)

        # TODO: combine with prior probability
        p, r, f, acc = run_el.evaluate(predictions, golds, to_print=False)
        loss, gradient = self.get_loss(self.model.ops.asarray(predictions), self.model.ops.asarray(golds))

        print("p/r/F/acc/loss", print_string, round(p, 1), round(r, 1), round(f, 1), round(acc, 2), round(loss, 5))

        return loss, p, r, f

    def _predict(self, entities, article_docs, desc_docs, avg=True, apply_threshold=True):
        if avg:
            with self.article_encoder.use_params(self.sgd_article.averages) \
                 and self.desc_encoder.use_params(self.sgd_entity.averages):
                doc_encodings = self.article_encoder(article_docs)
                desc_encodings = self.desc_encoder(desc_docs)

        else:
            doc_encodings = self.article_encoder(article_docs)
            desc_encodings = self.desc_encoder(desc_docs)

        concat_encodings = [list(desc_encodings[i]) + list(doc_encodings[i]) for i in range(len(entities))]
        np_array_list = np.asarray(concat_encodings)

        if avg:
            with self.model.use_params(self.sgd.averages):
                predictions = self.model(np_array_list)
        else:
            predictions = self.model(np_array_list)

        predictions = self.model.ops.flatten(predictions)
        predictions = [float(p) for p in predictions]
        if apply_threshold:
            predictions = [float(1.0) if p > self.CUTOFF else float(0.0) for p in predictions]

        return predictions

    def _predict_random(self, entities, apply_threshold=True):
        if not apply_threshold:
            return [float(random.uniform(0, 1)) for e in entities]
        else:
            return [float(1.0) if random.uniform(0, 1) > self.CUTOFF else float(0.0) for e in entities]

    def _build_cnn(self, in_width, desc_width, article_width, hidden_1_width, hidden_2_width):
        with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
            self.desc_encoder = self._encoder(in_width=in_width, hidden_with=hidden_1_width, end_width=desc_width)
            self.article_encoder = self._encoder(in_width=in_width, hidden_with=hidden_1_width, end_width=article_width)

            in_width = desc_width + article_width
            out_width = hidden_2_width

            self.model = Affine(out_width, in_width) \
                >> LN(Maxout(out_width, out_width)) \
                >> Affine(1, out_width) \
                >> logistic

    @staticmethod
    def _encoder(in_width, hidden_with, end_width):
        conv_depth = 2
        cnn_maxout_pieces = 3

        with Model.define_operators({">>": chain}):
            convolution = Residual((ExtractWindow(nW=1) >> LN(Maxout(hidden_with, hidden_with * 3, pieces=cnn_maxout_pieces))))

            encoder = SpacyVectors \
                      >> with_flatten(LN(Maxout(hidden_with, in_width)) >> convolution ** conv_depth, pad=conv_depth) \
                      >> flatten_add_lengths \
                      >> ParametricAttention(hidden_with)\
                      >> Pooling(mean_pool) \
                      >> Residual(zero_init(Maxout(hidden_with, hidden_with))) \
                      >> zero_init(Affine(end_width, hidden_with, drop_factor=0.0))

            # TODO: ReLu or LN(Maxout)  ?
            # sum_pool or mean_pool ?

        return encoder

    def _begin_training(self):
        self.sgd_article = create_default_optimizer(self.article_encoder.ops)
        self.sgd_entity = create_default_optimizer(self.desc_encoder.ops)
        self.sgd = create_default_optimizer(self.model.ops)

    @staticmethod
    def get_loss(predictions, golds):
        d_scores = (predictions - golds)
        gradient = d_scores.mean()
        loss = (d_scores ** 2).mean()
        return loss, gradient

    def update(self, entities, golds, descs, texts):
        golds = self.model.ops.asarray(golds)

        desc_docs = self.nlp.pipe(descs)
        article_docs = self.nlp.pipe(texts)

        doc_encodings, bp_doc = self.article_encoder.begin_update(article_docs, drop=self.DROP)

        desc_encodings, bp_entity = self.desc_encoder.begin_update(desc_docs, drop=self.DROP)

        concat_encodings = [list(desc_encodings[i]) + list(doc_encodings[i]) for i in range(len(entities))]

        predictions, bp_model = self.model.begin_update(np.asarray(concat_encodings), drop=self.DROP)
        predictions = self.model.ops.flatten(predictions)

        # print("entities", entities)
        # print("predictions", predictions)
        # print("golds", golds)

        loss, gradient = self.get_loss(predictions, golds)

        if self.PRINT_TRAIN:
            print("loss train", round(loss, 5))

        gradient = float(gradient)
        # print("gradient", gradient)
        # print("loss", loss)

        model_gradient = bp_model(gradient, sgd=self.sgd)
        # print("model_gradient", model_gradient)

        # concat = desc + doc, but doc is the same within this function (TODO: multiple docs/articles)
        doc_gradient = model_gradient[0][self.DESC_WIDTH:]
        entity_gradients = list()
        for x in model_gradient:
            entity_gradients.append(list(x[0:self.DESC_WIDTH]))

        # print("doc_gradient", doc_gradient)
        # print("entity_gradients", entity_gradients)

        bp_doc([doc_gradient], sgd=self.sgd_article)
        bp_entity(entity_gradients, sgd=self.sgd_entity)

    def _get_training_data(self, training_dir, entity_descr_output, dev, limit, to_print):
        id_to_descr = kb_creator._get_id_to_description(entity_descr_output)

        correct_entries, incorrect_entries = training_set_creator.read_training_entities(training_output=training_dir,
                                                                                         collect_correct=True,
                                                                                         collect_incorrect=True)

        local_vectors = list()   # TODO: local vectors
        text_by_article = dict()
        gold_by_entity = dict()
        desc_by_entity = dict()
        article_by_entity = dict()
        entities = list()

        cnt = 0
        next_entity_nr = 0
        files = listdir(training_dir)
        shuffle(files)
        for f in files:
            if not limit or cnt < limit:
                if dev == run_el.is_dev(f):
                    article_id = f.replace(".txt", "")
                    if cnt % 500 == 0 and to_print:
                        print(datetime.datetime.now(), "processed", cnt, "files in the training dataset")
                    cnt += 1
                    if article_id not in text_by_article:
                        with open(os.path.join(training_dir, f), mode="r", encoding='utf8') as file:
                            text = file.read()
                            text_by_article[article_id] = text

                    for mention, entity_pos in correct_entries[article_id].items():
                        descr = id_to_descr.get(entity_pos)
                        if descr:
                            entities.append(next_entity_nr)
                            gold_by_entity[next_entity_nr] = 1
                            desc_by_entity[next_entity_nr] = descr
                            article_by_entity[next_entity_nr] = article_id
                            next_entity_nr += 1

                    for mention, entity_negs in incorrect_entries[article_id].items():
                        for entity_neg in entity_negs:
                            descr = id_to_descr.get(entity_neg)
                            if descr:
                                entities.append(next_entity_nr)
                                gold_by_entity[next_entity_nr] = 0
                                desc_by_entity[next_entity_nr] = descr
                                article_by_entity[next_entity_nr] = article_id
                                next_entity_nr += 1

        if to_print:
            print()
            print("Processed", cnt, "training articles, dev=" + str(dev))
            print()
        return entities, gold_by_entity, desc_by_entity, article_by_entity, text_by_article

