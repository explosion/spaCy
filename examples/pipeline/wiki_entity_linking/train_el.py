# coding: utf-8
from __future__ import unicode_literals

import os
import datetime
from os import listdir
import numpy as np
import random
from random import shuffle
from thinc.neural._classes.convolution import ExtractWindow
from thinc.neural.util import get_array_module

from examples.pipeline.wiki_entity_linking import run_el, training_set_creator, kb_creator

from spacy._ml import SpacyVectors, create_default_optimizer, zero_init, cosine

from thinc.api import chain, concatenate, flatten_add_lengths, clone, with_flatten
from thinc.v2v import Model, Maxout, Affine
from thinc.t2v import Pooling, mean_pool
from thinc.t2t import ParametricAttention
from thinc.misc import Residual
from thinc.misc import LayerNorm as LN

# from spacy.cli.pretrain import get_cossim_loss
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc

""" TODO: this code needs to be implemented in pipes.pyx"""


class EL_Model:

    PRINT_INSPECT = False
    PRINT_BATCH_LOSS = False
    EPS = 0.0000000005

    BATCH_SIZE = 5

    DOC_CUTOFF = 300    # number of characters from the doc context
    INPUT_DIM = 300     # dimension of pre-trained vectors

    HIDDEN_1_WIDTH = 32
    DESC_WIDTH = 64
    ARTICLE_WIDTH = 128
    SENT_WIDTH = 64

    DROP = 0.1
    LEARN_RATE = 0.001
    EPOCHS = 10
    L2 = 1e-6

    name = "entity_linker"

    def __init__(self, kb, nlp):
        run_el._prepare_pipeline(nlp, kb)
        self.nlp = nlp
        self.kb = kb

        self._build_cnn(embed_width=self.INPUT_DIM,
                        desc_width=self.DESC_WIDTH,
                        article_width=self.ARTICLE_WIDTH,
                        sent_width=self.SENT_WIDTH,
                        hidden_1_width=self.HIDDEN_1_WIDTH)

    def train_model(self, training_dir, entity_descr_output, trainlimit=None, devlimit=None, to_print=True):
        np.seterr(divide="raise", over="warn", under="ignore", invalid="raise")

        train_ent, train_gold, train_desc, train_art, train_art_texts, train_sent, train_sent_texts = \
            self._get_training_data(training_dir, entity_descr_output, False, trainlimit, to_print=False)
        train_clusters = list(train_ent.keys())

        dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts = \
            self._get_training_data(training_dir, entity_descr_output, True, devlimit, to_print=False)
        dev_clusters = list(dev_ent.keys())

        dev_pos_count = len([g for g in dev_gold.values() if g])
        dev_neg_count = len([g for g in dev_gold.values() if not g])

        # inspect data
        if self.PRINT_INSPECT:
            for cluster, entities in train_ent.items():
                print()
                for entity in entities:
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

        self._begin_training()

        if to_print:
            print()
            print("Training on", len(train_clusters), "entity clusters in", len(train_art_texts), "articles")
            print("Training instances pos/neg:", train_pos_count, train_neg_count)
            print()
            print("Dev test on", len(dev_clusters), "entity clusters in", len(dev_art_texts), "articles")
            print("Dev instances pos/neg:", dev_pos_count, dev_neg_count)
            print()
            print(" DOC_CUTOFF", self.DOC_CUTOFF)
            print(" INPUT_DIM", self.INPUT_DIM)
            print(" HIDDEN_1_WIDTH", self.HIDDEN_1_WIDTH)
            print(" DESC_WIDTH", self.DESC_WIDTH)
            print(" ARTICLE_WIDTH", self.ARTICLE_WIDTH)
            print(" SENT_WIDTH", self.SENT_WIDTH)
            print(" DROP", self.DROP)
            print(" LEARNING RATE", self.LEARN_RATE)
            print(" BATCH SIZE", self.BATCH_SIZE)
            print()

        dev_random = self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts,
                                    calc_random=True)
        print("acc", "dev_random", round(dev_random, 2))

        dev_pre = self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts,
                                 avg=True)
        print("acc", "dev_pre", round(dev_pre, 2))
        print()

        processed = 0
        for i in range(self.EPOCHS):
            shuffle(train_clusters)

            start = 0
            stop = min(self.BATCH_SIZE, len(train_clusters))

            while start < len(train_clusters):
                next_batch = {c: train_ent[c] for c in train_clusters[start:stop]}
                processed += len(next_batch.keys())

                self.update(entity_clusters=next_batch, golds=train_gold, descs=train_desc,
                            art_texts=train_art_texts, arts=train_art,
                            sent_texts=train_sent_texts, sents=train_sent)

                start = start + self.BATCH_SIZE
                stop = min(stop + self.BATCH_SIZE, len(train_clusters))

            train_acc = self._test_dev(train_ent, train_gold, train_desc, train_art, train_art_texts, train_sent, train_sent_texts, avg=True)
            dev_acc = self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts, avg=True)

            print(i, "acc train/dev", round(train_acc, 2), round(dev_acc, 2))

        if to_print:
            print()
            print("Trained on", processed, "entity clusters across", self.EPOCHS, "epochs")

    def _test_dev(self, entity_clusters, golds, descs, arts, art_texts, sents, sent_texts, avg=True, calc_random=False):
        correct = 0
        incorrect = 0

        if calc_random:
            for cluster, entities in entity_clusters.items():
                correct_entities = [e for e in entities if golds[e]]
                assert len(correct_entities) == 1

                entities = list(entities)
                shuffle(entities)

                if calc_random:
                    predicted_entity = random.choice(entities)
                    if predicted_entity in correct_entities:
                        correct += 1
                    else:
                        incorrect += 1

        else:
            all_clusters = list()
            arts_list = list()
            sents_list = list()

            for cluster in entity_clusters.keys():
                all_clusters.append(cluster)
                arts_list.append(art_texts[arts[cluster]])
                sents_list.append(sent_texts[sents[cluster]])

            art_docs = list(self.nlp.pipe(arts_list))
            sent_docs = list(self.nlp.pipe(sents_list))

            for i, cluster in enumerate(all_clusters):
                entities = entity_clusters[cluster]
                correct_entities = [e for e in entities if golds[e]]
                assert len(correct_entities) == 1

                entities = list(entities)
                shuffle(entities)

                desc_docs = self.nlp.pipe([descs[e] for e in entities])
                sent_doc = sent_docs[i]
                article_doc = art_docs[i]

                predicted_index = self._predict(article_doc=article_doc, sent_doc=sent_doc,
                                                desc_docs=desc_docs, avg=avg)
                if entities[predicted_index] in correct_entities:
                    correct += 1
                else:
                    incorrect += 1

        if correct == incorrect == 0:
            return 0

        acc = correct / (correct + incorrect)
        return acc

    def _predict(self, article_doc, sent_doc, desc_docs, avg=True, apply_threshold=True):
        # print()
        # print("predicting article")

        if avg:
            with self.article_encoder.use_params(self.sgd_article.averages) \
                 and self.desc_encoder.use_params(self.sgd_desc.averages)\
                 and self.sent_encoder.use_params(self.sgd_sent.averages)\
                 and self.cont_encoder.use_params(self.sgd_cont.averages):
                desc_encodings = self.desc_encoder(desc_docs)
                doc_encoding = self.article_encoder([article_doc])
                sent_encoding = self.sent_encoder([sent_doc])

        else:
            desc_encodings = self.desc_encoder(desc_docs)
            doc_encoding = self.article_encoder([article_doc])
            sent_encoding = self.sent_encoder([sent_doc])

        # print("desc_encodings", desc_encodings)
        # print("doc_encoding", doc_encoding)
        # print("sent_encoding", sent_encoding)
        concat_encoding = [list(doc_encoding[0]) + list(sent_encoding[0])]
        # print("concat_encoding", concat_encoding)

        cont_encodings = self.cont_encoder(np.asarray([concat_encoding[0]]))
        # print("cont_encodings", cont_encodings)
        context_enc = np.transpose(cont_encodings)
        # print("context_enc", context_enc)

        highest_sim = -5
        best_i = -1
        for i, desc_enc in enumerate(desc_encodings):
            sim = cosine(desc_enc, context_enc)
            if sim >= highest_sim:
                best_i = i
                highest_sim = sim

        return best_i

    def _build_cnn(self, embed_width, desc_width, article_width, sent_width, hidden_1_width):
        self.desc_encoder = self._encoder(in_width=embed_width, hidden_with=hidden_1_width, end_width=desc_width)
        self.cont_encoder = self._context_encoder(embed_width=embed_width, article_width=article_width,
                                                     sent_width=sent_width, hidden_width=hidden_1_width,
                                                     end_width=desc_width)


    # def _encoder(self, width):
    #    tok2vec = Tok2Vec(width=width, embed_size=2000, pretrained_vectors=self.nlp.vocab.vectors.name, cnn_maxout_pieces=3,
    #                      subword_features=False, conv_depth=4, bilstm_depth=0)
    #
    #    return tok2vec >> flatten_add_lengths >> Pooling(mean_pool)

    def _context_encoder(self, embed_width, article_width, sent_width, hidden_width, end_width):
        self.article_encoder = self._encoder(in_width=embed_width, hidden_with=hidden_width, end_width=article_width)
        self.sent_encoder = self._encoder(in_width=embed_width, hidden_with=hidden_width, end_width=sent_width)

        model = Affine(end_width, article_width+sent_width, drop_factor=0.0)
        return model

    @staticmethod
    def _encoder(in_width, hidden_with, end_width):
        conv_depth = 2
        cnn_maxout_pieces = 3

        with Model.define_operators({">>": chain, "**": clone}):
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
        self.sgd_article.learn_rate = self.LEARN_RATE
        self.sgd_article.L2 = self.L2

        self.sgd_sent = create_default_optimizer(self.sent_encoder.ops)
        self.sgd_sent.learn_rate = self.LEARN_RATE
        self.sgd_sent.L2 = self.L2

        self.sgd_cont = create_default_optimizer(self.cont_encoder.ops)
        self.sgd_cont.learn_rate = self.LEARN_RATE
        self.sgd_cont.L2 = self.L2

        self.sgd_desc = create_default_optimizer(self.desc_encoder.ops)
        self.sgd_desc.learn_rate = self.LEARN_RATE
        self.sgd_desc.L2 = self.L2

    def get_loss(self, v1, v2, targets):
        loss, gradients = self.get_cossim_loss(v1, v2, targets)
        return loss, gradients

    def get_cossim_loss(self, yh, y, t):
        # Add a small constant to avoid 0 vectors
        # print()
        # print("yh", yh)
        # print("y", y)
        # print("t", t)
        yh = yh + 1e-8
        y = y + 1e-8
        # https://math.stackexchange.com/questions/1923613/partial-derivative-of-cosine-similarity
        xp = get_array_module(yh)
        norm_yh = xp.linalg.norm(yh, axis=1, keepdims=True)
        norm_y = xp.linalg.norm(y, axis=1, keepdims=True)
        mul_norms = norm_yh * norm_y
        cos = (yh * y).sum(axis=1, keepdims=True) / mul_norms
        # print("cos", cos)
        d_yh = (y / mul_norms) - (cos * (yh / norm_yh ** 2))
        # print("abs", xp.abs(cos - t))
        loss = xp.abs(cos - t).sum()
        # print("loss", loss)
        # print("d_yh", d_yh)
        inverse = np.asarray([int(t[i][0]) * d_yh[i] for i in range(len(t))])
        # print("inverse", inverse)
        return loss, -inverse

    def update(self, entity_clusters, golds, descs, art_texts, arts, sent_texts, sents):
        all_clusters = list(entity_clusters.keys())

        arts_list = list()
        sents_list = list()
        descs_list = list()
        targets = list()

        for cluster, entities in entity_clusters.items():
            art = art_texts[arts[cluster]]
            sent = sent_texts[sents[cluster]]
            for e in entities:
                if golds[e]:
                    arts_list.append(art)
                    sents_list.append(sent)
                    descs_list.append(descs[e])
                    targets.append([1])
                else:
                    arts_list.append(art)
                    sents_list.append(sent)
                    descs_list.append(descs[e])
                    targets.append([-1])

        desc_docs = self.nlp.pipe(descs_list)
        desc_encodings, bp_desc = self.desc_encoder.begin_update(desc_docs, drop=self.DROP)

        art_docs = self.nlp.pipe(arts_list)
        sent_docs = self.nlp.pipe(sents_list)

        doc_encodings, bp_doc = self.article_encoder.begin_update(art_docs, drop=self.DROP)
        sent_encodings, bp_sent = self.sent_encoder.begin_update(sent_docs, drop=self.DROP)

        concat_encodings = [list(doc_encodings[i]) + list(sent_encodings[i]) for i in
                            range(len(targets))]
        cont_encodings, bp_cont = self.cont_encoder.begin_update(np.asarray(concat_encodings), drop=self.DROP)

        # print("sent_encodings", type(sent_encodings), sent_encodings)
        # print("desc_encodings", type(desc_encodings), desc_encodings)
        # print("doc_encodings", type(doc_encodings), doc_encodings)
        # print("getting los for", len(arts_list), "entities")

        loss, gradient = self.get_loss(cont_encodings, desc_encodings, targets)

        # print("gradient", gradient)
        if self.PRINT_BATCH_LOSS:
            print("batch loss", loss)

        context_gradient = bp_cont(gradient, sgd=self.sgd_cont)

        # gradient : concat (doc+sent) vs. desc
        sent_start = self.ARTICLE_WIDTH
        sent_gradients = list()
        doc_gradients = list()
        for x in context_gradient:
            doc_gradients.append(list(x[0:sent_start]))
            sent_gradients.append(list(x[sent_start:]))

        # print("doc_gradients", doc_gradients)
        # print("sent_gradients", sent_gradients)

        bp_doc(doc_gradients, sgd=self.sgd_article)
        bp_sent(sent_gradients, sgd=self.sgd_sent)

    def _get_training_data(self, training_dir, entity_descr_output, dev, limit, to_print):
        id_to_descr = kb_creator._get_id_to_description(entity_descr_output)

        correct_entries, incorrect_entries = training_set_creator.read_training_entities(training_output=training_dir,
                                                                                         collect_correct=True,
                                                                                         collect_incorrect=True)

        entities_by_cluster = dict()
        gold_by_entity = dict()
        desc_by_entity = dict()
        article_by_cluster = dict()
        text_by_article = dict()
        sentence_by_cluster = dict()
        text_by_sentence = dict()
        sentence_by_text = dict()

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
                    for mention, entity_pos in correct_entries[article_id].items():
                        cluster = article_id + "_" + mention
                        descr = id_to_descr.get(entity_pos)
                        entities = set()
                        if descr:
                            entity = "E_" + str(next_entity_nr) + "_" + cluster
                            next_entity_nr += 1
                            gold_by_entity[entity] = 1
                            desc_by_entity[entity] = descr
                            entities.add(entity)

                            entity_negs = incorrect_entries[article_id][mention]
                            for entity_neg in entity_negs:
                                descr = id_to_descr.get(entity_neg)
                                if descr:
                                    entity = "E_" + str(next_entity_nr) + "_" + cluster
                                    next_entity_nr += 1
                                    gold_by_entity[entity] = 0
                                    desc_by_entity[entity] = descr
                                    entities.add(entity)

                        found_matches = 0
                        if len(entities) > 1:
                            entities_by_cluster[cluster] = entities

                            # find all matches in the doc for the mentions
                            # TODO: fix this - doesn't look like all entities are found
                            matcher = PhraseMatcher(self.nlp.vocab)
                            patterns = list(self.nlp.tokenizer.pipe([mention]))

                            matcher.add("TerminologyList", None, *patterns)
                            matches = matcher(article_doc)


                            # store sentences
                            for match_id, start, end in matches:
                                found_matches += 1
                                span = article_doc[start:end]
                                assert mention == span.text
                                sent_text = span.sent.text
                                sent_nr = sentence_by_text.get(sent_text,  None)
                                if sent_nr is None:
                                    sent_nr = "S_" + str(next_sent_nr) + article_id
                                    next_sent_nr += 1
                                    text_by_sentence[sent_nr] = sent_text
                                    sentence_by_text[sent_text] = sent_nr
                                article_by_cluster[cluster] = article_id
                                sentence_by_cluster[cluster] = sent_nr

                        if found_matches == 0:
                            # TODO print("Could not find neg instances or sentence matches for", mention, "in", article_id)
                            entities_by_cluster.pop(cluster, None)
                            article_by_cluster.pop(cluster, None)
                            sentence_by_cluster.pop(cluster, None)
                            for entity in entities:
                                gold_by_entity.pop(entity, None)
                                desc_by_entity.pop(entity, None)


        if to_print:
            print()
            print("Processed", cnt, "training articles, dev=" + str(dev))
            print()
        return entities_by_cluster, gold_by_entity, desc_by_entity, article_by_cluster, text_by_article, \
               sentence_by_cluster, text_by_sentence

