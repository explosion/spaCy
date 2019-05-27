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

from spacy._ml import SpacyVectors, create_default_optimizer, zero_init, logistic, Tok2Vec, cosine

from thinc.api import chain, concatenate, flatten_add_lengths, clone, with_flatten
from thinc.v2v import Model, Maxout, Affine, ReLu
from thinc.t2v import Pooling, mean_pool, sum_pool
from thinc.t2t import ParametricAttention
from thinc.misc import Residual
from thinc.misc import LayerNorm as LN

from spacy.cli.pretrain import get_cossim_loss
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc

""" TODO: this code needs to be implemented in pipes.pyx"""


class EL_Model:

    PRINT_INSPECT = False
    PRINT_TRAIN = True
    EPS = 0.0000000005
    CUTOFF = 0.5

    BATCH_SIZE = 5
    # UPSAMPLE = True

    DOC_CUTOFF = 300    # number of characters from the doc context
    INPUT_DIM = 300     # dimension of pre-trained vectors

    HIDDEN_1_WIDTH = 32
    # HIDDEN_2_WIDTH = 32  # 6
    DESC_WIDTH = 64
    ARTICLE_WIDTH = 64
    SENT_WIDTH = 64

    DROP = 0.1
    LEARN_RATE = 0.0001
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
                        sent_width=self.SENT_WIDTH, hidden_1_width=self.HIDDEN_1_WIDTH)

    def train_model(self, training_dir, entity_descr_output, trainlimit=None, devlimit=None, to_print=True):
        # raise errors instead of runtime warnings in case of int/float overflow
        # (not sure if we need this. set L2 to 0 because it throws an error otherwsise)
        # np.seterr(all='raise')
        # alternative:
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

        # if self.UPSAMPLE:
        #    if to_print:
        #        print()
        #        print("Upsampling, original training instances pos/neg:", train_pos_count, train_neg_count)
        #
        #    # upsample positives to 50-50 distribution
        #    while train_pos_count < train_neg_count:
        #        train_ent.append(random.choice(train_pos_entities))
        #        train_pos_count += 1
        #
            # upsample negatives to 50-50 distribution
        #    while train_neg_count < train_pos_count:
        #        train_ent.append(random.choice(train_neg_entities))
        #        train_neg_count += 1

        self._begin_training()

        if to_print:
            print()
            print("Training on", len(train_clusters), "entity clusters in", len(train_art_texts), "articles")
            print("Training instances pos/neg:", train_pos_count, train_neg_count)
            print()
            print("Dev test on", len(dev_clusters), "entity clusters in", len(dev_art_texts), "articles")
            print("Dev instances pos/neg:", dev_pos_count, dev_neg_count)
            print()
            print(" CUTOFF", self.CUTOFF)
            print(" DOC_CUTOFF", self.DOC_CUTOFF)
            print(" INPUT_DIM", self.INPUT_DIM)
            # print(" HIDDEN_1_WIDTH", self.HIDDEN_1_WIDTH)
            print(" DESC_WIDTH", self.DESC_WIDTH)
            print(" ARTICLE_WIDTH", self.ARTICLE_WIDTH)
            print(" SENT_WIDTH", self.SENT_WIDTH)
            # print(" HIDDEN_2_WIDTH", self.HIDDEN_2_WIDTH)
            print(" DROP", self.DROP)
            print(" LEARNING RATE", self.LEARN_RATE)
            print(" UPSAMPLE", self.UPSAMPLE)
            print()

        self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts,
                       print_string="dev_random", calc_random=True)

        self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts,
                       print_string="dev_pre", avg=True)

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

            if self.PRINT_TRAIN:
                print()
                self._test_dev(train_ent, train_gold, train_desc, train_art, train_art_texts, train_sent, train_sent_texts,
                                print_string="train_inter_epoch " + str(i), avg=True)

            self._test_dev(dev_ent, dev_gold, dev_desc, dev_art, dev_art_texts, dev_sent, dev_sent_texts,
                           print_string="dev_inter_epoch " + str(i), avg=True)

        if to_print:
            print()
            print("Trained on", processed, "entity clusters across", self.EPOCHS, "epochs")

    def _test_dev(self, entity_clusters, golds, descs, arts, art_texts, sents, sent_texts,
                  print_string, avg=True, calc_random=False):

        correct = 0
        incorrect = 0

        for cluster, entities in entity_clusters.items():
            correct_entities = [e for e in entities if golds[e]]
            incorrect_entities = [e for e in entities if not golds[e]]
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
                desc_docs = self.nlp.pipe([descs[e] for e in entities])
                # article_texts = [art_texts[arts[e]] for e in entities]

                sent_doc = self.nlp(sent_texts[sents[cluster]])
                article_doc = self.nlp(art_texts[arts[cluster]])

                predicted_index = self._predict(article_doc=article_doc, sent_doc=sent_doc,
                                                desc_docs=desc_docs, avg=avg)
                if entities[predicted_index] in correct_entities:
                    correct += 1
                else:
                    incorrect += 1

        if correct == incorrect == 0:
            print("acc", print_string, "NA")
            return 0

        acc = correct / (correct + incorrect)
        print("acc", print_string, round(acc, 2))
        return acc

    def _predict(self, article_doc, sent_doc, desc_docs, avg=True, apply_threshold=True):
        if avg:
            with self.article_encoder.use_params(self.sgd_article.averages) \
                 and self.desc_encoder.use_params(self.sgd_desc.averages)\
                 and self.sent_encoder.use_params(self.sgd_sent.averages):
                # doc_encoding = self.article_encoder(article_doc)
                desc_encodings = self.desc_encoder(desc_docs)
                sent_encoding = self.sent_encoder([sent_doc])

        else:
            # doc_encodings = self.article_encoder(article_docs)
            desc_encodings = self.desc_encoder(desc_docs)
            sent_encoding = self.sent_encoder([sent_doc])

        sent_enc = np.transpose(sent_encoding)
        highest_sim = -5
        best_i = -1
        for i, desc_enc in enumerate(desc_encodings):
            sim = cosine(desc_enc, sent_enc)
            if sim >= highest_sim:
                best_i = i
                highest_sim = sim

        return best_i

    def _predict_random(self, entities, apply_threshold=True):
        if not apply_threshold:
            return [float(random.uniform(0, 1)) for _ in entities]
        else:
            return [float(1.0) if random.uniform(0, 1) > self.CUTOFF else float(0.0) for _ in entities]

    def _build_cnn(self, embed_width, desc_width, article_width, sent_width, hidden_1_width):
        with Model.define_operators({">>": chain, "|": concatenate, "**": clone}):
            self.desc_encoder = self._encoder(in_width=embed_width, hidden_with=hidden_1_width,
                                                   end_width=desc_width)
            self.article_encoder = self._encoder(in_width=embed_width, hidden_with=hidden_1_width,
                                                      end_width=article_width)
            self.sent_encoder = self._encoder(in_width=embed_width, hidden_with=hidden_1_width,
                                                   end_width=sent_width)

    # def _encoder(self, width):
    #    tok2vec = Tok2Vec(width=width, embed_size=2000, pretrained_vectors=self.nlp.vocab.vectors.name, cnn_maxout_pieces=3,
    #                      subword_features=False, conv_depth=4, bilstm_depth=0)
    #
    #    return tok2vec >> flatten_add_lengths >> Pooling(mean_pool)

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
        self.sgd_article.learn_rate = self.LEARN_RATE
        self.sgd_article.L2 = self.L2

        self.sgd_sent = create_default_optimizer(self.sent_encoder.ops)
        self.sgd_sent.learn_rate = self.LEARN_RATE
        self.sgd_sent.L2 = self.L2

        self.sgd_desc = create_default_optimizer(self.desc_encoder.ops)
        self.sgd_desc.learn_rate = self.LEARN_RATE
        self.sgd_desc.L2 = self.L2

        # self.sgd = create_default_optimizer(self.model.ops)
        # self.sgd.learn_rate = self.LEARN_RATE
        # self.sgd.L2 = self.L2

    @staticmethod
    def get_loss(predictions, golds):
        loss, gradients = get_cossim_loss(predictions, golds)
        return loss, gradients

    def update(self, entity_clusters, golds, descs, art_texts, arts, sent_texts, sents):
        for cluster, entities in entity_clusters.items():
            correct_entities = [e for e in entities if golds[e]]
            incorrect_entities = [e for e in entities if not golds[e]]

            assert len(correct_entities) == 1
            entities = list(entities)
            shuffle(entities)

            # article_text = art_texts[arts[cluster]]
            cluster_sent = sent_texts[sents[cluster]]

            # art_docs = self.nlp.pipe(article_text)
            sent_doc = self.nlp(cluster_sent)

            for e in entities:
                if golds[e]:
                 # TODO: more appropriate loss for the whole cluster (currently only pos entities)
                 #  TODO: speed up
                    desc_doc = self.nlp(descs[e])

                    # doc_encodings, bp_doc = self.article_encoder.begin_update(art_docs, drop=self.DROP)
                    sent_encodings, bp_sent = self.sent_encoder.begin_update([sent_doc], drop=self.DROP)
                    desc_encodings, bp_desc = self.desc_encoder.begin_update([desc_doc], drop=self.DROP)

                    sent_encoding = sent_encodings[0]
                    desc_encoding = desc_encodings[0]

                    sent_enc = self.sent_encoder.ops.asarray([sent_encoding])
                    desc_enc = self.sent_encoder.ops.asarray([desc_encoding])

                    # print("sent_encoding", type(sent_encoding), sent_encoding)
                    # print("desc_encoding", type(desc_encoding), desc_encoding)
                    # print("getting los for entity", e)

                    loss, gradient = self.get_loss(sent_enc, desc_enc)

                    # print("gradient", gradient)
                    # print("loss", loss)

                    bp_sent(gradient, sgd=self.sgd_sent)
                    # bp_desc(desc_gradients, sgd=self.sgd_desc)    TODO
                    # print()

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

