# coding: utf-8
from __future__ import unicode_literals

import logging
import random
from tqdm import tqdm
from collections import defaultdict

logger = logging.getLogger(__name__)


class Metrics(object):
    true_pos = 0
    false_pos = 0
    false_neg = 0

    def update_results(self, true_entity, candidate):
        candidate_is_correct = true_entity == candidate

        # Assume that we have no labeled negatives in the data (i.e. cases where true_entity is "NIL")
        # Therefore, if candidate_is_correct then we have a true positive and never a true negative.
        self.true_pos += candidate_is_correct
        self.false_neg += not candidate_is_correct
        if candidate and candidate not in {"", "NIL"}:
            # A wrong prediction (e.g. Q42 != Q3) counts both as a FP as well as a FN.
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

    def calculate_fscore(self):
        p = self.calculate_precision()
        r = self.calculate_recall()
        if p + r == 0:
            return 0.0
        else:
            return 2 * p * r / (p + r)


class EvaluationResults(object):
    def __init__(self):
        self.metrics = Metrics()
        self.metrics_by_label = defaultdict(Metrics)

    def update_metrics(self, ent_label, true_entity, candidate):
        self.metrics.update_results(true_entity, candidate)
        self.metrics_by_label[ent_label].update_results(true_entity, candidate)

    def report_metrics(self, model_name):
        model_str = model_name.title()
        recall = self.metrics.calculate_recall()
        precision = self.metrics.calculate_precision()
        fscore = self.metrics.calculate_fscore()
        return (
            "{}: ".format(model_str)
            + "F-score = {} | ".format(round(fscore, 3))
            + "Recall = {} | ".format(round(recall, 3))
            + "Precision = {} | ".format(round(precision, 3))
            + "F-score by label = {}".format(
                {k: v.calculate_fscore() for k, v in sorted(self.metrics_by_label.items())}
            )
        )


class BaselineResults(object):
    def __init__(self):
        self.random = EvaluationResults()
        self.prior = EvaluationResults()
        self.oracle = EvaluationResults()

    def report_performance(self, model):
        results = getattr(self, model)
        return results.report_metrics(model)

    def update_baselines(
        self,
        true_entity,
        ent_label,
        random_candidate,
        prior_candidate,
        oracle_candidate,
    ):
        self.oracle.update_metrics(ent_label, true_entity, oracle_candidate)
        self.prior.update_metrics(ent_label, true_entity, prior_candidate)
        self.random.update_metrics(ent_label, true_entity, random_candidate)


def measure_performance(dev_data, kb, el_pipe, baseline=True, context=True, dev_limit=None):
    counts = dict()
    baseline_results = BaselineResults()
    context_results = EvaluationResults()
    combo_results = EvaluationResults()

    for doc, gold in tqdm(dev_data, total=dev_limit, leave=False, desc='Processing dev data'):
        if len(doc) > 0:
            correct_ents = dict()
            for entity, kb_dict in gold.links.items():
                start, end = entity
                for gold_kb, value in kb_dict.items():
                    if value:
                        # only evaluating on positive examples
                        offset = _offset(start, end)
                        correct_ents[offset] = gold_kb

            if baseline:
                _add_baseline(baseline_results, counts, doc, correct_ents, kb)

            if context:
                # using only context
                el_pipe.cfg["incl_context"] = True
                el_pipe.cfg["incl_prior"] = False
                _add_eval_result(context_results, doc, correct_ents, el_pipe)

                # measuring combined accuracy (prior + context)
                el_pipe.cfg["incl_context"] = True
                el_pipe.cfg["incl_prior"] = True
                _add_eval_result(combo_results, doc, correct_ents, el_pipe)

    if baseline:
        logger.info("Counts: {}".format({k: v for k, v in sorted(counts.items())}))
        logger.info(baseline_results.report_performance("random"))
        logger.info(baseline_results.report_performance("prior"))
        logger.info(baseline_results.report_performance("oracle"))

    if context:
        logger.info(context_results.report_metrics("context only"))
        logger.info(combo_results.report_metrics("context and prior"))


def _add_eval_result(results, doc, correct_ents, el_pipe):
    """
    Evaluate the ent.kb_id_ annotations against the gold standard.
    Only evaluate entities that overlap between gold and NER, to isolate the performance of the NEL.
    """
    try:
        doc = el_pipe(doc)
        for ent in doc.ents:
            ent_label = ent.label_
            start = ent.start_char
            end = ent.end_char
            offset = _offset(start, end)
            gold_entity = correct_ents.get(offset, None)
            # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
            if gold_entity is not None:
                pred_entity = ent.kb_id_
                results.update_metrics(ent_label, gold_entity, pred_entity)

    except Exception as e:
        logging.error("Error assessing accuracy " + str(e))


def _add_baseline(baseline_results, counts, doc, correct_ents, kb):
    """
    Measure 3 performance baselines: random selection, prior probabilities, and 'oracle' prediction for upper bound.
    Only evaluate entities that overlap between gold and NER, to isolate the performance of the NEL.
    """
    for ent in doc.ents:
        ent_label = ent.label_
        start = ent.start_char
        end = ent.end_char
        offset = _offset(start, end)
        gold_entity = correct_ents.get(offset, None)

        # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
        if gold_entity is not None:
            candidates = kb.get_candidates(ent.text)
            oracle_candidate = ""
            prior_candidate = ""
            random_candidate = ""
            if candidates:
                scores = []

                for c in candidates:
                    scores.append(c.prior_prob)
                    if c.entity_ == gold_entity:
                        oracle_candidate = c.entity_

                best_index = scores.index(max(scores))
                prior_candidate = candidates[best_index].entity_
                random_candidate = random.choice(candidates).entity_

            current_count = counts.get(ent_label, 0)
            counts[ent_label] = current_count+1

            baseline_results.update_baselines(
                gold_entity,
                ent_label,
                random_candidate,
                prior_candidate,
                oracle_candidate,
            )


def _offset(start, end):
    return "{}_{}".format(start, end)
