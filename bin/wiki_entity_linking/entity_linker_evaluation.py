import logging
import random

from tqdm import tqdm
from typing import NamedTuple

logger = logging.getLogger(__name__)


class BaselineResults(NamedTuple):
    random_recall: float
    random_precision: float
    prior_recall: float
    prior_precision: float
    oracle_recall: float
    oracle_precision: float

    def report_accuracy(self, model):
        model_str = model.title()
        recall = getattr(self, "{}_recall".format(model))
        precision = getattr(self, "{}_precision".format(model))
        return ("{}: ".format(model_str) +
                "Recall = {} | ".format(round(recall, 3)) +
                "Precision = {}".format(round(precision, 3)))


class Metrics(object):
    def __init__(self, true_pos, false_pos, false_neg):
        self.true_pos = true_pos
        self.false_pos = false_pos
        self.false_neg = false_neg

    def update_results(self, true_entity, candidate):
        candidate_is_correct = true_entity == candidate
        self.true_pos += candidate_is_correct
        self.false_neg += not candidate_is_correct
        if candidate != "" and candidate != "NIL":
            self.false_pos += not candidate_is_correct

    def calculate_precision(self):
        if self.true_pos == 0:
            return 0.0
        else:
            return self.true_pos / (self.true_pos + self.false_pos)

    def calculate_recall(self):
        if self.true_pos == 0:
            return 0.0
        else:
            return self.true_pos / (self.true_pos + self.false_neg)


def measure_performance(dev_data, kb, el_pipe):
    baseline_accuracies = measure_baselines(
        dev_data, kb
    )

    logger.info(baseline_accuracies.report_accuracy("random"))
    logger.info(baseline_accuracies.report_accuracy("prior"))
    logger.info(baseline_accuracies.report_accuracy("oracle"))

    # using only context
    el_pipe.cfg["incl_context"] = True
    el_pipe.cfg["incl_prior"] = False
    dev_precision_context, dev_recall_context = measure_precision_recall(dev_data, el_pipe)
    logger.info("dev precision context avg: {}".format(round(dev_precision_context, 3)))
    logger.info("dev recall context avg: {}".format(round(dev_recall_context, 3)))

    # measuring combined accuracy (prior + context)
    el_pipe.cfg["incl_context"] = True
    el_pipe.cfg["incl_prior"] = True
    dev_precision_combo, dev_recall_combo = measure_precision_recall(dev_data, el_pipe)
    logger.info("dev precision combo avg: {}".format(round(dev_precision_combo, 3)))
    logger.info("dev recall combo avg: {}".format(round(dev_recall_combo, 3)))


def measure_precision_recall(data, el_pipe=None):
    # If the docs in the data require further processing with an entity linker, set el_pipe
    docs = []
    golds = []
    for d, g in tqdm(data, leave=False):
        if len(d) > 0:
            golds.append(g)
            if el_pipe is not None:
                docs.append(el_pipe(d))
            else:
                docs.append(d)

    results = Metrics(0, 0, 0)
    for doc, gold in zip(docs, golds):
        try:
            correct_entries_per_article = dict()
            for entity, kb_dict in gold.links.items():
                start, end = entity
                # only evaluating on positive examples
                for gold_kb, value in kb_dict.items():
                    if value:
                        offset = _offset(start, end)
                        correct_entries_per_article[offset] = gold_kb

            for ent in doc.ents:
                pred_entity = ent.kb_id_
                start = ent.start_char
                end = ent.end_char
                offset = _offset(start, end)
                gold_entity = correct_entries_per_article.get(offset, None)
                # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
                if gold_entity is not None:
                    results.update_results(gold_entity, pred_entity)

        except Exception as e:
            logging.error("Error assessing accuracy " + str(e))

    return results.calculate_precision(), results.calculate_recall()


def measure_baselines(data, kb):
    # Measure 3 performance baselines: random selection, prior probabilities, and 'oracle' prediction for upper bound
    counts_d = dict()

    random_results = Metrics(0, 0, 0)
    oracle_results = Metrics(0, 0, 0)
    prior_results = Metrics(0, 0, 0)

    docs = [d for d, g in data if len(d) > 0]
    golds = [g for d, g in data if len(d) > 0]

    for doc, gold in zip(docs, golds):
        correct_entries_per_article = dict()
        tagged_entries_per_article = {_offset(ent.start_char, ent.end_char): ent for ent in doc.ents}
        for entity, kb_dict in gold.links.items():
            start, end = entity
            for gold_kb, value in kb_dict.items():
                # only evaluating on positive examples
                if value:
                    offset = _offset(start, end)
                    correct_entries_per_article[offset] = gold_kb
                    if offset not in tagged_entries_per_article:
                        random_results.false_neg += 1
                        oracle_results.false_neg += 1
                        prior_results.false_neg += 1

        for ent in doc.ents:
            start = ent.start_char
            end = ent.end_char
            offset = _offset(start, end)
            gold_entity = correct_entries_per_article.get(offset, None)

            # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
            if gold_entity is not None:
                candidates = kb.get_candidates(ent.text)
                oracle_candidate = ""
                best_candidate = ""
                random_candidate = ""
                if candidates:
                    scores = []

                    for c in candidates:
                        scores.append(c.prior_prob)
                        if c.entity_ == gold_entity:
                            oracle_candidate = c.entity_

                    best_index = scores.index(max(scores))
                    best_candidate = candidates[best_index].entity_
                    random_candidate = random.choice(candidates).entity_

                oracle_results.update_results(gold_entity, oracle_candidate)
                prior_results.update_results(gold_entity, best_candidate)
                random_results.update_results(gold_entity, random_candidate)

    return BaselineResults(
        random_results.calculate_recall(),
        random_results.calculate_precision(),
        prior_results.calculate_recall(),
        prior_results.calculate_precision(),
        oracle_results.calculate_recall(),
        oracle_results.calculate_precision(),
    )


def _offset(start, end):
    return "{}_{}".format(start, end)
