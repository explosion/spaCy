import logging
import random

from collections import defaultdict

logger = logging.getLogger(__name__)


class Metrics(object):
    true_pos = 0
    false_pos = 0
    false_neg = 0

    def update_results(self, true_entity, candidate):
        candidate_is_correct = true_entity == candidate

        # Assume that we have no labeled negatives in the data (i.e. cases where true_entity is "NIL")
        # Therefore, if candidate_is_correct then we have a true positive and never a true negative
        self.true_pos += candidate_is_correct
        self.false_neg += not candidate_is_correct
        if candidate not in {"", "NIL"}:
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


class EvaluationResults(object):
    def __init__(self):
        self.metrics = Metrics()
        self.metrics_by_label = defaultdict(Metrics)

    def update_metrics(self, ent_label, true_entity, candidate):
        self.metrics.update_results(true_entity, candidate)
        self.metrics_by_label[ent_label].update_results(true_entity, candidate)

    def increment_false_negatives(self):
        self.metrics.false_neg += 1

    def report_metrics(self, model_name):
        model_str = model_name.title()
        recall = self.metrics.calculate_recall()
        precision = self.metrics.calculate_precision()
        return ("{}: ".format(model_str) +
                "Recall = {} | ".format(round(recall, 3)) +
                "Precision = {} | ".format(round(precision, 3)) +
                "Precision by label = {}".format({k: v.calculate_precision()
                                                  for k, v in self.metrics_by_label.items()}))


class BaselineResults(object):
    def __init__(self):
        self.random = EvaluationResults()
        self.prior = EvaluationResults()
        self.oracle = EvaluationResults()

    def report_accuracy(self, model):
        results = getattr(self, model)
        return results.report_metrics(model)

    def update_baselines(self, true_entity, ent_label, random_candidate, prior_candidate, oracle_candidate):
        self.oracle.update_metrics(ent_label, true_entity, oracle_candidate)
        self.prior.update_metrics(ent_label, true_entity, prior_candidate)
        self.random.update_metrics(ent_label, true_entity, random_candidate)


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
    results = get_eval_results(dev_data, el_pipe)
    logger.info(results.report_metrics("context only"))

    # measuring combined accuracy (prior + context)
    el_pipe.cfg["incl_context"] = True
    el_pipe.cfg["incl_prior"] = True
    results = get_eval_results(dev_data, el_pipe)
    logger.info(results.report_metrics("context and prior"))


def get_eval_results(data, el_pipe=None):
    # If the docs in the data require further processing with an entity linker, set el_pipe
    from tqdm import tqdm

    docs = []
    golds = []
    for d, g in tqdm(data, leave=False):
        if len(d) > 0:
            golds.append(g)
            if el_pipe is not None:
                docs.append(el_pipe(d))
            else:
                docs.append(d)

    results = EvaluationResults()
    for doc, gold in zip(docs, golds):
        tagged_entries_per_article = {_offset(ent.start_char, ent.end_char): ent for ent in doc.ents}
        try:
            correct_entries_per_article = dict()
            for entity, kb_dict in gold.links.items():
                start, end = entity
                # only evaluating on positive examples
                for gold_kb, value in kb_dict.items():
                    if value:
                        offset = _offset(start, end)
                        correct_entries_per_article[offset] = gold_kb
                        if offset not in tagged_entries_per_article:
                            results.increment_false_negatives()

            for ent in doc.ents:
                ent_label = ent.label_
                pred_entity = ent.kb_id_
                start = ent.start_char
                end = ent.end_char
                offset = _offset(start, end)
                gold_entity = correct_entries_per_article.get(offset, None)
                # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
                if gold_entity is not None:
                    results.update_metrics(ent_label, gold_entity, pred_entity)

        except Exception as e:
            logging.error("Error assessing accuracy " + str(e))

    return results


def measure_baselines(data, kb):
    # Measure 3 performance baselines: random selection, prior probabilities, and 'oracle' prediction for upper bound
    counts_d = dict()

    baseline_results = BaselineResults()

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
                        baseline_results.random.increment_false_negatives()
                        baseline_results.oracle.increment_false_negatives()
                        baseline_results.prior.increment_false_negatives()

        for ent in doc.ents:
            ent_label = ent.label_
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

                baseline_results.update_baselines(gold_entity, ent_label,
                                                  random_candidate, best_candidate, oracle_candidate)

    return baseline_results


def _offset(start, end):
    return "{}_{}".format(start, end)
