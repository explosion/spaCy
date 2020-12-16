# coding: utf-8
from __future__ import unicode_literals

from numpy.testing import assert_almost_equal, assert_array_almost_equal
import pytest
from pytest import approx
from spacy.gold import GoldParse
from spacy.scorer import Scorer, ROCAUCScore
from spacy.scorer import _roc_auc_score, _roc_curve
from .util import get_doc

test_las_apple = [
    [
        "Apple is looking at buying U.K. startup for $ 1 billion",
        {
            "heads": [2, 2, 2, 2, 3, 6, 4, 4, 10, 10, 7],
            "deps": [
                "nsubj",
                "aux",
                "ROOT",
                "prep",
                "pcomp",
                "compound",
                "dobj",
                "prep",
                "quantmod",
                "compound",
                "pobj",
            ],
        },
    ]
]

test_ner_cardinal = [
    ["100 - 200", {"entities": [[0, 3, "CARDINAL"], [6, 9, "CARDINAL"]]}]
]

test_ner_apple = [
    [
        "Apple is looking at buying U.K. startup for $1 billion",
        {"entities": [(0, 5, "ORG"), (27, 31, "GPE"), (44, 54, "MONEY")]},
    ]
]


def test_las_per_type(en_vocab):
    # Gold and Doc are identical
    scorer = Scorer()
    for input_, annot in test_las_apple:
        doc = get_doc(
            en_vocab,
            words=input_.split(" "),
            heads=([h - i for i, h in enumerate(annot["heads"])]),
            deps=annot["deps"],
        )
        gold = GoldParse(doc, heads=annot["heads"], deps=annot["deps"])
        scorer.score(doc, gold)
    results = scorer.scores

    assert results["uas"] == 100
    assert results["las"] == 100
    assert results["las_per_type"]["nsubj"]["p"] == 100
    assert results["las_per_type"]["nsubj"]["r"] == 100
    assert results["las_per_type"]["nsubj"]["f"] == 100
    assert results["las_per_type"]["compound"]["p"] == 100
    assert results["las_per_type"]["compound"]["r"] == 100
    assert results["las_per_type"]["compound"]["f"] == 100

    # One dep is incorrect in Doc
    scorer = Scorer()
    for input_, annot in test_las_apple:
        doc = get_doc(
            en_vocab,
            words=input_.split(" "),
            heads=([h - i for i, h in enumerate(annot["heads"])]),
            deps=annot["deps"],
        )
        gold = GoldParse(doc, heads=annot["heads"], deps=annot["deps"])
        doc[0].dep_ = "compound"
        scorer.score(doc, gold)
    results = scorer.scores

    assert results["uas"] == 100
    assert_almost_equal(results["las"], 90.9090909)
    assert results["las_per_type"]["nsubj"]["p"] == 0
    assert results["las_per_type"]["nsubj"]["r"] == 0
    assert results["las_per_type"]["nsubj"]["f"] == 0
    assert_almost_equal(results["las_per_type"]["compound"]["p"], 66.6666666)
    assert results["las_per_type"]["compound"]["r"] == 100
    assert results["las_per_type"]["compound"]["f"] == 80


def test_ner_per_type(en_vocab):
    # Gold and Doc are identical
    scorer = Scorer()
    for input_, annot in test_ner_cardinal:
        doc = get_doc(
            en_vocab,
            words=input_.split(" "),
            ents=[[0, 1, "CARDINAL"], [2, 3, "CARDINAL"]],
        )
        gold = GoldParse(doc, entities=annot["entities"])
        scorer.score(doc, gold)
    results = scorer.scores

    assert results["ents_p"] == 100
    assert results["ents_f"] == 100
    assert results["ents_r"] == 100
    assert results["ents_per_type"]["CARDINAL"]["p"] == 100
    assert results["ents_per_type"]["CARDINAL"]["f"] == 100
    assert results["ents_per_type"]["CARDINAL"]["r"] == 100

    # Doc has one missing and one extra entity
    # Entity type MONEY is not present in Doc
    scorer = Scorer()
    for input_, annot in test_ner_apple:
        doc = get_doc(
            en_vocab,
            words=input_.split(" "),
            ents=[[0, 1, "ORG"], [5, 6, "GPE"], [6, 7, "ORG"]],
        )
        gold = GoldParse(doc, entities=annot["entities"])
        scorer.score(doc, gold)
    results = scorer.scores

    assert results["ents_p"] == approx(66.66666)
    assert results["ents_r"] == approx(66.66666)
    assert results["ents_f"] == approx(66.66666)
    assert "GPE" in results["ents_per_type"]
    assert "MONEY" in results["ents_per_type"]
    assert "ORG" in results["ents_per_type"]
    assert results["ents_per_type"]["GPE"]["p"] == 100
    assert results["ents_per_type"]["GPE"]["r"] == 100
    assert results["ents_per_type"]["GPE"]["f"] == 100
    assert results["ents_per_type"]["MONEY"]["p"] == 0
    assert results["ents_per_type"]["MONEY"]["r"] == 0
    assert results["ents_per_type"]["MONEY"]["f"] == 0
    assert results["ents_per_type"]["ORG"]["p"] == 50
    assert results["ents_per_type"]["ORG"]["r"] == 100
    assert results["ents_per_type"]["ORG"]["f"] == approx(66.66666)


def test_roc_auc_score():
    # Binary classification, toy tests from scikit-learn test suite
    y_true = [0, 1]
    y_score = [0, 1]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 0, 1])
    assert_array_almost_equal(fpr, [0, 1, 1])
    assert_almost_equal(roc_auc, 1.0)

    y_true = [0, 1]
    y_score = [1, 0]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 1, 1])
    assert_array_almost_equal(fpr, [0, 0, 1])
    assert_almost_equal(roc_auc, 0.0)

    y_true = [1, 0]
    y_score = [1, 1]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 1])
    assert_array_almost_equal(fpr, [0, 1])
    assert_almost_equal(roc_auc, 0.5)

    y_true = [1, 0]
    y_score = [1, 0]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 0, 1])
    assert_array_almost_equal(fpr, [0, 1, 1])
    assert_almost_equal(roc_auc, 1.0)

    y_true = [1, 0]
    y_score = [0.5, 0.5]
    tpr, fpr, _ = _roc_curve(y_true, y_score)
    roc_auc = _roc_auc_score(y_true, y_score)
    assert_array_almost_equal(tpr, [0, 1])
    assert_array_almost_equal(fpr, [0, 1])
    assert_almost_equal(roc_auc, 0.5)

    # same result as above with ROCAUCScore wrapper
    score = ROCAUCScore()
    score.score_set(0.5, 1)
    score.score_set(0.5, 0)
    assert_almost_equal(score.score, 0.5)

    # check that errors are raised in undefined cases and score is -inf
    y_true = [0, 0]
    y_score = [0.25, 0.75]
    with pytest.raises(ValueError):
        _roc_auc_score(y_true, y_score)

    score = ROCAUCScore()
    score.score_set(0.25, 0)
    score.score_set(0.75, 0)
    assert score.score == -float("inf")

    y_true = [1, 1]
    y_score = [0.25, 0.75]
    with pytest.raises(ValueError):
        _roc_auc_score(y_true, y_score)

    score = ROCAUCScore()
    score.score_set(0.25, 1)
    score.score_set(0.75, 1)
    assert score.score == -float("inf")
