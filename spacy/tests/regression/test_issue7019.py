from spacy.cli.evaluate import print_textcats_auc_per_cat, print_prf_per_type
from wasabi import msg


def test_issue7019():
    scores = {"LABEL_A": 0.39829102, "LABEL_B": 0.938298329382, "LABEL_C": None}
    print_textcats_auc_per_cat(msg, scores)
    scores = {
        "LABEL_A": {"p": 0.3420302, "r": 0.3929020, "f": 0.49823928932},
        "LABEL_B": {"p": None, "r": None, "f": None},
    }
    print_prf_per_type(msg, scores, name="foo", type="bar")
