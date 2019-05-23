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

from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc

""" TODO: this code needs to be implemented in pipes.pyx"""


class EL_Model:

    PRINT_INSPECT = False
    PRINT_TRAIN = False
    EPS = 0.0000000005
    CUTOFF = 0.5

    BATCH_SIZE = 5

    DOC_CUTOFF = 300    # number of characters from the doc context
    INPUT_DIM = 300     # dimension of pre-trained vectors

    HIDDEN_1_WIDTH = 32   # 10
    HIDDEN_2_WIDTH = 32  # 6
    DESC_WIDTH = 64     # 4
    ARTICLE_WIDTH = 64   # 8
    SENT_WIDTH = 64

    DROP = 0.1

    name = "entity_linker"

    def __init__(self, kb, nlp):
        run_el._prepare_pipeline(nlp, kb)
        self.nlp = nlp
        self.kb = kb

        self._build_cnn(in_width=self.INPUT_DIM,
                        desc_width=self.DESC_WIDTH,
                        article_width=self.ARTICLE_WIDTH,
                        sent_width=self.SENT_WIDTH,
                        hidden_1_width=self.HIDDEN_1_WIDTH,
                        hidden_2_width=self.HIDDEN_2_WIDTH)

    def train_model(self, training_dir, entity_descr_output, trainlimit=None, devlimit=None, to_print=True):
        # raise errors instead of runtime warnings in case of int/float overflow
        np.seterr(all='raise')

        train_ent, train_gold, train_desc, train_art, train_art_texts, train_sent, train_sent_texts = \
            self._get_training_data(training_dir, entity_descr_output, False, trainlimit, to_print=False)

        # inspect data
        if self.PRINT_INSPECT:
            for entity in train_ent:
                print("entity", entity)
                print("gold", train_gold[entity])
                print("desc", train_desc[entity])
                print("sentence ID", train_sent[entity])
                print("sentence text", train_sent_texts[train_sent[entity]])
                print("article ID", train_art[entity])
                print("article text", train_art_texts[train_art[entity]])
                print()

        train_pos_entities = [k for k, v in train_gold.items() if v]
        train_neg_entities = [k for k, v in train_gold.items() if not v]

        train_pos_count = len(train_pos_entities)
        train_neg_count = len(train_neg_entities)

        if to_print:
            print()
            print("Upsampling, original training instances pos/neg:", train_pos_count, train_neg_count)

        # upsample positives to 50-50 distribution
        while train_pos_count < train_neg_count:
            train_ent.append(random.choice(train_pos_entities))
            train_pos_count += 1

        # upsample negatives to 50-50 distribution
        while train_neg_count < train_pos_count:
            train_ent.append(random.choice(train_neg_entities))
            train_neg_count += 1

        shuffle(train_ent)

        dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts = \
            self._get_training_data(training_dir, entity_descr_output, True, devlimit, to_print=False)
        shuffle(dev_ent)

        dev_pos_count = len([g for g in dev_gold.values() if g])
        dev_neg_count = len([g for g in dev_gold.values() if not g])

        self._begin_training()

        if to_print:
            print()
            print("Training on", len(train_ent), "entities in", len(train_art_texts), "articles")
            print("Training instances pos/neg:", train_pos_count, train_neg_count)
            print()
            print("Dev test on", len(dev_ent), "entities in", len(dev_art_texts), "articles")
            print("Dev instances pos/neg:", dev_pos_count, dev_neg_count)
            print()
            print(" CUTOFF", self.CUTOFF)
            print(" DOC_CUTOFF", self.DOC_CUTOFF)
            print(" INPUT_DIM", self.INPUT_DIM)
            print(" HIDDEN_1_WIDTH", self.HIDDEN_1_WIDTH)
            print(" DESC_WIDTH", self.DESC_WIDTH)
            print(" ARTICLE_WIDTH", self.ARTICLE_WIDTH)
            print(" SENT_WIDTH", self.SENT_WIDTH)
            print(" HIDDEN_2_WIDTH", self.HIDDEN_2_WIDTH)
            print(" DROP", self.DROP)
            print()

        self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts,
                       print_string="dev_random", calc_random=True)
        self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts,
                       print_string="dev_pre", avg=True)
        print()

        start = 0
        stop = min(self.BATCH_SIZE, len(train_ent))
        processed = 0

        while start < len(train_ent):
            next_batch = train_ent[start:stop]

            golds = [train_gold[e] for e in next_batch]
            descs = [train_desc[e] for e in next_batch]
            article_texts = [train_art_texts[train_art[e]] for e in next_batch]
            sent_texts = [train_sent_texts[train_sent[e]] for e in next_batch]

            self.update(entities=next_batch, golds=golds, descs=descs, art_texts=article_texts, sent_texts=sent_texts)
            self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts,
                           print_string="dev_inter", avg=True)

            processed += len(next_batch)

            start = start + self.BATCH_SIZE
            stop = min(stop + self.BATCH_SIZE, len(train_ent))

        if to_print:
            print()
            print("Trained on", processed, "entities in total")

    def _test_dev(self, entities, gold_by_entity, desc_by_entity, art_by_entity, art_texts, sent_by_entity, sent_texts,
                  print_string, avg=True, calc_random=False):
        golds = [gold_by_entity[e] for e in entities]

        if calc_random:
            predictions = self._predict_random(entities=entities)

        else:
            desc_docs = self.nlp.pipe([desc_by_entity[e] for e in entities])
            article_docs = self.nlp.pipe([art_texts[art_by_entity[e]] for e in entities])
            sent_docs = self.nlp.pipe([sent_texts[sent_by_entity[e]] for e in entities])
            predictions = self._predict(entities=entities, article_docs=article_docs, sent_docs=sent_docs,
                                        desc_docs=desc_docs, avg=avg)

        # TODO: combine with prior probability
        p, r, f, acc = run_el.evaluate(predictions, golds, to_print=False, times_hundred=False)
        loss, gradient = self.get_loss(self.model.ops.asarray(predictions), self.model.ops.asarray(golds))

        print("p/r/F/acc/loss", print_string, round(p, 2), round(r, 2), round(f, 2), round(acc, 2), round(loss, 2))

        return loss, p, r, f

    def _predict(self, entities, article_docs, sent_docs, desc_docs, avg=True, apply_threshold=True):
        if avg:
            with self.article_encoder.use_params(self.sgd_article.averages) \
                 and self.desc_encoder.use_params(self.sgd_desc.averages):
                doc_encodings = self.article_encoder(article_docs)
                desc_encodings = self.desc_encoder(desc_docs)
                sent_encodings = self.sent_encoder(sent_docs)

        else:
            doc_encodings = self.article_encoder(article_docs)
            desc_encodings = self.desc_encoder(desc_docs)
            sent_encodings = self.sent_encoder(sent_docs)

        concat_encodings = [list(doc_encodings[i]) + list(sent_encodings[i]) + list(desc_encodings[i]) for i in
                            range(len(entities))]

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
            return [float(random.uniform(0, 1)) for _ in entities]
        else:
            return [float(1.0) if random.uniform(0, 1) > self.CUTOFF else float(0.0) for _ in entities]

    def _build_cnn(self, in_width, desc_width, article_width, sent_width, hidden_1_width, hidden_2_width):
        with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
            self.desc_encoder = self._encoder(in_width=in_width, hidden_with=hidden_1_width, end_width=desc_width)
            self.article_encoder = self._encoder(in_width=in_width, hidden_with=hidden_1_width, end_width=article_width)
            self.sent_encoder = self._encoder(in_width=in_width, hidden_with=hidden_1_width, end_width=sent_width)

            in_width = article_width + sent_width + desc_width
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
            convolution = Residual((ExtractWindow(nW=1) >>
                                    LN(Maxout(hidden_with, hidden_with * 3, pieces=cnn_maxout_pieces))))

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
        self.sgd_sent = create_default_optimizer(self.sent_encoder.ops)
        self.sgd_desc = create_default_optimizer(self.desc_encoder.ops)
        self.sgd = create_default_optimizer(self.model.ops)

    @staticmethod
    def get_loss(predictions, golds):
        d_scores = (predictions - golds)
        gradient = d_scores.mean()
        loss = (d_scores ** 2).mean()
        return loss, gradient

    def update(self, entities, golds, descs, art_texts, sent_texts):
        golds = self.model.ops.asarray(golds)

        art_docs = self.nlp.pipe(art_texts)
        sent_docs = self.nlp.pipe(sent_texts)
        desc_docs = self.nlp.pipe(descs)

        doc_encodings, bp_doc = self.article_encoder.begin_update(art_docs, drop=self.DROP)
        sent_encodings, bp_sent = self.sent_encoder.begin_update(sent_docs, drop=self.DROP)
        desc_encodings, bp_desc = self.desc_encoder.begin_update(desc_docs, drop=self.DROP)

        concat_encodings = [list(doc_encodings[i]) + list(sent_encodings[i]) + list(desc_encodings[i])
                            for i in range(len(entities))]

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

        # concat = doc + sent + desc, but doc is the same within this function
        sent_start = self.ARTICLE_WIDTH
        desc_start = self.ARTICLE_WIDTH + self.SENT_WIDTH
        doc_gradient = model_gradient[0][0:sent_start]
        sent_gradients = list()
        desc_gradients = list()
        for x in model_gradient:
            sent_gradients.append(list(x[sent_start:desc_start]))
            desc_gradients.append(list(x[desc_start:]))

        # print("doc_gradient", doc_gradient)
        # print("sent_gradients", sent_gradients)
        # print("desc_gradients", desc_gradients)

        bp_doc([doc_gradient], sgd=self.sgd_article)
        bp_sent(sent_gradients, sgd=self.sgd_sent)
        bp_desc(desc_gradients, sgd=self.sgd_desc)

    def _get_training_data(self, training_dir, entity_descr_output, dev, limit, to_print):
        id_to_descr = kb_creator._get_id_to_description(entity_descr_output)

        correct_entries, incorrect_entries = training_set_creator.read_training_entities(training_output=training_dir,
                                                                                         collect_correct=True,
                                                                                         collect_incorrect=True)

        entities = set()
        gold_by_entity = dict()
        desc_by_entity = dict()
        article_by_entity = dict()
        text_by_article = dict()
        sentence_by_entity = dict()
        text_by_sentence = dict()

        cnt = 0
        next_entity_nr = 1
        next_sent_nr = 1
        files = listdir(training_dir)
        shuffle(files)
        for f in files:
            if not limit or cnt < limit:
                if dev == run_el.is_dev(f):
                    article_id = f.replace(".txt", "")
                    if cnt % 500 == 0 and to_print:
                        print(datetime.datetime.now(), "processed", cnt, "files in the training dataset")
                    cnt += 1

                    # parse the article text
                    with open(os.path.join(training_dir, f), mode="r", encoding='utf8') as file:
                        text = file.read()
                        article_doc = self.nlp(text)
                        truncated_text = text[0:min(self.DOC_CUTOFF, len(text))]
                        text_by_article[article_id] = truncated_text

                    # process all positive and negative entities, collect all relevant mentions in this article
                    article_terms = set()
                    entities_by_mention = dict()

                    for mention, entity_pos in correct_entries[article_id].items():
                        descr = id_to_descr.get(entity_pos)
                        if descr:
                            entity = "E_" + str(next_entity_nr) + "_" + article_id + "_" + mention
                            next_entity_nr += 1
                            gold_by_entity[entity] = 1
                            desc_by_entity[entity] = descr
                            article_terms.add(mention)
                            mention_entities = entities_by_mention.get(mention, set())
                            mention_entities.add(entity)
                            entities_by_mention[mention] = mention_entities

                    for mention, entity_negs in incorrect_entries[article_id].items():
                        for entity_neg in entity_negs:
                            descr = id_to_descr.get(entity_neg)
                            if descr:
                                entity = "E_" + str(next_entity_nr) + "_" + article_id + "_" + mention
                                next_entity_nr += 1
                                gold_by_entity[entity] = 0
                                desc_by_entity[entity] = descr
                                article_terms.add(mention)
                                mention_entities = entities_by_mention.get(mention, set())
                                mention_entities.add(entity)
                                entities_by_mention[mention] = mention_entities

                    # find all matches in the doc for the mentions
                    # TODO: fix this - doesn't look like all entities are found
                    matcher = PhraseMatcher(self.nlp.vocab)
                    patterns = list(self.nlp.tokenizer.pipe(article_terms))

                    matcher.add("TerminologyList", None, *patterns)
                    matches = matcher(article_doc)

                    # store sentences
                    sentence_to_id = dict()
                    for match_id, start, end in matches:
                        span = article_doc[start:end]
                        sent_text = span.sent.text
                        sent_nr = sentence_to_id.get(sent_text,  None)
                        mention = span.text
                        if sent_nr is None:
                            sent_nr = "S_" + str(next_sent_nr) + article_id
                            next_sent_nr += 1
                            text_by_sentence[sent_nr] = sent_text
                            sentence_to_id[sent_text] = sent_nr
                        mention_entities = entities_by_mention[mention]
                        for entity in mention_entities:
                            entities.add(entity)
                            sentence_by_entity[entity] = sent_nr
                            article_by_entity[entity] = article_id

        # remove entities that didn't have all data
        gold_by_entity = {k: v for k, v in gold_by_entity.items() if k in entities}
        desc_by_entity = {k: v for k, v in desc_by_entity.items() if k in entities}

        article_by_entity = {k: v for k, v in article_by_entity.items() if k in entities}
        text_by_article = {k: v for k, v in text_by_article.items() if k in article_by_entity.values()}

        sentence_by_entity = {k: v for k, v in sentence_by_entity.items() if k in entities}
        text_by_sentence = {k: v for k, v in text_by_sentence.items() if k in sentence_by_entity.values()}

        if to_print:
            print()
            print("Processed", cnt, "training articles, dev=" + str(dev))
            print()
        return list(entities), gold_by_entity, desc_by_entity, article_by_entity, text_by_article, \
               sentence_by_entity, text_by_sentence

