import logging
import random

from collections import defaultdict
from tqdm import tqdm
from typing import Dict, NamedTuple

logger = logging.getLogger(__name__)


class BaselineResults(NamedTuple):
    counts_dict: Dict
    random_recall: float
    random_precision: float
    random_accuracy_by_label: Dict
    prior_recall: float
    prior_precision: float
    prior_accuracy_by_label: Dict
    oracle_recall: float
    oracle_precision: float
    oracle_accuracy_by_label: Dict

    def report_accuracy(self, model: str) -> str:
        model_str = model.title()
        recall = getattr(self, f"{model}_recall")
        precision = getattr(self, f"{model}_precision")
        return (f"{model_str}: "
                f"Recall = {round(recall, 3)} | "
                f"Precision = {round(precision, 3)}")


def measure_performance(dev_data, kb, el_pipe):
    baseline_accuracies = measure_baselines(
        dev_data, kb
    )
    print("dev counts:", sorted(baseline_accuracies.counts_dict.items(), key=lambda x: x[0]))

    logger.info(baseline_accuracies.report_accuracy("random"))
    logger.info(baseline_accuracies.report_accuracy("prior"))
    logger.info(baseline_accuracies.report_accuracy("oracle"))

    # using only context
    el_pipe.cfg["incl_context"] = True
    el_pipe.cfg["incl_prior"] = False
    dev_precision_context, dev_recall_context, dev_acc_cont_d = measure_acc(dev_data, el_pipe)
    print("dev precision context avg:", round(dev_precision_context, 3))
    print("dev recall context avg:", round(dev_recall_context, 3))

    # measuring combined accuracy (prior + context)
    el_pipe.cfg["incl_context"] = True
    el_pipe.cfg["incl_prior"] = True
    dev_precision_combo, dev_recall_combo, dev_acc_combo_d = measure_acc(dev_data, el_pipe)
    print("dev precision combo avg:", round(dev_precision_combo, 3))
    print("dev recall combo avg:", round(dev_recall_combo, 3))


def measure_acc(data, el_pipe=None, error_analysis=False):
    # If the docs in the data require further processing with an entity linker, set el_pipe
    correct_by_label = defaultdict(int)
    incorrect_by_label = defaultdict(int)

    docs = []
    golds = []
    for d, g in tqdm(data, leave=False):
        if len(d) > 0:
            docs.append(el_pipe(d))
            golds.append(g)

    false_positives = 0
    true_positives = 0
    false_negatives = 0
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
                ent_label = ent.label_
                pred_entity = ent.kb_id_
                start = ent.start_char
                end = ent.end_char
                offset = _offset(start, end)
                gold_entity = correct_entries_per_article.get(offset, None)
                # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
                if gold_entity is not None:
                    if gold_entity == pred_entity:
                        correct_by_label[ent_label] += 1
                        true_positives += 1
                    elif pred_entity == "NIL":
                        false_negatives += 1
                    else:
                        incorrect_by_label[ent_label] += 1
                        false_positives += 1
                        false_negatives += 1

        except Exception as e:
            print("Error assessing accuracy", e)

    _, acc_by_label = calculate_acc(correct_by_label, incorrect_by_label)
    return (
        _calculate_precision(true_positives, false_positives),
        _calculate_recall(true_positives, false_negatives),
        acc_by_label
    )


def measure_baselines(data, kb):
    # Measure 3 performance baselines: random selection, prior probabilities, and 'oracle' prediction for upper bound
    counts_d = dict()

    random_true_positives = 0
    random_false_positives = 0
    random_false_negatives = 0
    random_correct_d = defaultdict(int)
    random_incorrect_d = defaultdict(int)

    oracle_true_positives = 0
    oracle_false_positives = 0
    oracle_false_negatives = 0
    oracle_correct_d = defaultdict(int)
    oracle_incorrect_d = defaultdict(int)

    prior_true_positives = 0
    prior_false_positives = 0
    prior_false_negatives = 0
    prior_correct_d = defaultdict(int)
    prior_incorrect_d = defaultdict(int)

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
                        random_false_negatives += 1
                        oracle_false_negatives += 1
                        prior_false_negatives += 1

        for ent in doc.ents:
            label = ent.label_
            start = ent.start_char
            end = ent.end_char
            offset = _offset(start, end)
            gold_entity = correct_entries_per_article.get(offset, None)

            # the gold annotations are not complete so we can't evaluate missing annotations as 'wrong'
            if gold_entity is not None:
                counts_d[label] = counts_d.get(label, 0) + 1
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

                random_correct_d[label] += (gold_entity == random_candidate)
                random_incorrect_d[label] += (not gold_entity == random_candidate)

                random_true_positives += (gold_entity == random_candidate)
                random_false_negatives += (not gold_entity == random_candidate)
                if candidates:
                    random_false_positives += (not gold_entity == random_candidate)

                prior_correct_d[label] += (gold_entity == best_candidate)
                prior_incorrect_d[label] += (not gold_entity == best_candidate)

                prior_true_positives += (gold_entity == best_candidate)
                prior_false_negatives += (not gold_entity == best_candidate)
                if candidates:
                    prior_false_positives += (not gold_entity == best_candidate)

                oracle_correct_d[label] += (gold_entity == oracle_candidate)
                oracle_incorrect_d[label] += (not gold_entity == oracle_candidate)

                oracle_true_positives += (gold_entity == oracle_candidate)
                oracle_false_negatives += (not gold_entity == oracle_candidate)
                if candidates:
                    oracle_false_positives += (not gold_entity == oracle_candidate)

    return BaselineResults(
        counts_d,
        _calculate_recall(random_true_positives, random_false_negatives),
        _calculate_precision(random_true_positives, random_false_positives),
        calculate_acc(random_correct_d, random_incorrect_d)[1],
        _calculate_recall(prior_true_positives, prior_false_negatives),
        _calculate_precision(prior_true_positives, prior_false_positives),
        calculate_acc(prior_correct_d, prior_incorrect_d)[1],
        _calculate_recall(oracle_true_positives, oracle_false_negatives),
        _calculate_precision(oracle_true_positives, oracle_false_positives),
        calculate_acc(oracle_correct_d, oracle_incorrect_d)[1],
    )


def _offset(start, end):
    return "{}_{}".format(start, end)


def calculate_acc(correct_by_label, incorrect_by_label):
    acc_by_label = dict()
    all_keys = set(correct_by_label.keys()).union(set(incorrect_by_label.keys()))

    total_correct = sum(correct_by_label.values())
    total_incorrect = sum(incorrect_by_label.values())
    acc = _calculate_precision(total_correct, total_incorrect)

    for label in sorted(all_keys):
        correct = correct_by_label.get(label, 0)
        incorrect = incorrect_by_label.get(label, 0)
        acc_by_label[label] = _calculate_precision(correct, incorrect)
    return acc, acc_by_label


def _calculate_precision(true_positives: int, false_positives: int):
    if true_positives == 0:
        return 0.0
    else:
        return true_positives / (true_positives + false_positives)


def _calculate_recall(true_positives: int, false_negatives: int):
    if true_positives == 0:
        return 0.0
    else:
        return true_positives / (true_positives + false_negatives)
