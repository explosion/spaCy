from typing import Optional, List, Dict
from timeit import default_timer as timer
from wasabi import Printer
from pathlib import Path
import re
import srsly
from thinc.api import require_gpu, fix_random_seed

from ..gold import Corpus
from ..tokens import Doc
from ._app import app, Arg, Opt
from ..scorer import Scorer
from .. import util
from .. import displacy


@app.command("evaluate")
def evaluate_cli(
    # fmt: off
    model: str = Arg(..., help="Model name or path"),
    data_path: Path = Arg(..., help="Location of JSON-formatted evaluation data", exists=True),
    output: Optional[Path] = Opt(None, "--output", "-o", help="Output JSON file for metrics", dir_okay=False),
    gpu_id: int = Opt(-1, "--gpu-id", "-g", help="Use GPU"),
    gold_preproc: bool = Opt(False, "--gold-preproc", "-G", help="Use gold preprocessing"),
    displacy_path: Optional[Path] = Opt(None, "--displacy-path", "-dp", help="Directory to output rendered parses as HTML", exists=True, file_okay=False),
    displacy_limit: int = Opt(25, "--displacy-limit", "-dl", help="Limit of parses to render as HTML"),
    # fmt: on
):
    """
    Evaluate a model. To render a sample of parses in a HTML file, set an
    output directory as the displacy_path argument.
    """
    evaluate(
        model,
        data_path,
        output=output,
        gpu_id=gpu_id,
        gold_preproc=gold_preproc,
        displacy_path=displacy_path,
        displacy_limit=displacy_limit,
        silent=False,
    )


def evaluate(
    model: str,
    data_path: Path,
    output: Optional[Path],
    gpu_id: int = -1,
    gold_preproc: bool = False,
    displacy_path: Optional[Path] = None,
    displacy_limit: int = 25,
    silent: bool = True,
) -> Scorer:
    msg = Printer(no_print=silent, pretty=not silent)
    fix_random_seed()
    if gpu_id >= 0:
        require_gpu(gpu_id)
    util.set_env_log(False)
    data_path = util.ensure_path(data_path)
    output_path = util.ensure_path(output)
    displacy_path = util.ensure_path(displacy_path)
    if not data_path.exists():
        msg.fail("Evaluation data not found", data_path, exits=1)
    if displacy_path and not displacy_path.exists():
        msg.fail("Visualization output directory not found", displacy_path, exits=1)
    corpus = Corpus(data_path, data_path)
    nlp = util.load_model(model)
    dev_dataset = list(corpus.dev_dataset(nlp, gold_preproc=gold_preproc))
    begin = timer()
    scores = nlp.evaluate(dev_dataset, verbose=False)
    end = timer()
    nwords = sum(len(ex.predicted) for ex in dev_dataset)
    metrics = {
        "TOK": "token_acc",
        "TAG": "tag_acc",
        "POS": "pos_acc",
        "MORPH": "morph_acc",
        "LEMMA": "lemma_acc",
        "UAS": "dep_uas",
        "LAS": "dep_las",
        "NER P": "ents_p",
        "NER R": "ents_r",
        "NER F": "ents_f",
        "Textcat AUC": 'textcat_macro_auc',
        "Textcat F": 'textcat_macro_f',
        "Sent P": 'sents_p',
        "Sent R": 'sents_r',
        "Sent F": 'sents_f',
    }
    results = {}
    for metric, key in metrics.items():
        if key in scores:
            results[metric] = f"{scores[key]*100:.2f}"
    data = {re.sub(r"[\s/]", "_", k.lower()): v for k, v in results.items()}

    msg.table(results, title="Results")

    if "ents_per_type" in scores:
        if scores["ents_per_type"]:
            print_ents_per_type(msg, scores["ents_per_type"])
    if "textcat_f_per_cat" in scores:
        if scores["textcat_f_per_cat"]:
            print_textcats_f_per_cat(msg, scores["textcat_f_per_cat"])
    if "textcat_auc_per_cat" in scores:
        if scores["textcat_auc_per_cat"]:
            print_textcats_auc_per_cat(msg, scores["textcat_auc_per_cat"])

    if displacy_path:
        docs = [ex.predicted for ex in dev_dataset]
        render_deps = "parser" in nlp.meta.get("pipeline", [])
        render_ents = "ner" in nlp.meta.get("pipeline", [])
        render_parses(
            docs,
            displacy_path,
            model_name=model,
            limit=displacy_limit,
            deps=render_deps,
            ents=render_ents,
        )
        msg.good(f"Generated {displacy_limit} parses as HTML", displacy_path)

    if output_path is not None:
        srsly.write_json(output_path, data)
        msg.good(f"Saved results to {output_path}")
    return data


def render_parses(
    docs: List[Doc],
    output_path: Path,
    model_name: str = "",
    limit: int = 250,
    deps: bool = True,
    ents: bool = True,
):
    docs[0].user_data["title"] = model_name
    if ents:
        html = displacy.render(docs[:limit], style="ent", page=True)
        with (output_path / "entities.html").open("w", encoding="utf8") as file_:
            file_.write(html)
    if deps:
        html = displacy.render(
            docs[:limit], style="dep", page=True, options={"compact": True}
        )
        with (output_path / "parses.html").open("w", encoding="utf8") as file_:
            file_.write(html)


def print_ents_per_type(msg: Printer, scores: Dict[str, Dict[str, float]]) -> None:
    data = [
        (k, f"{v['p']*100:.2f}", f"{v['r']*100:.2f}", f"{v['f']*100:.2f}")
        for k, v in scores.items()
    ]
    msg.table(
        data,
        header=("", "P", "R", "F"),
        aligns=("l", "r", "r", "r"),
        title="NER (per type)",
    )


def print_textcats_f_per_cat(msg: Printer, scores: Dict[str, Dict[str, float]]) -> None:
    data = [
        (k, f"{v['p']*100:.2f}", f"{v['r']*100:.2f}", f"{v['f']*100:.2f}")
        for k, v in scores.items()
    ]
    msg.table(
        data,
        header=("", "P", "R", "F"),
        aligns=("l", "r", "r", "r"),
        title="Textcat F (per type)",
    )


def print_textcats_auc_per_cat(
    msg: Printer, scores: Dict[str, Dict[str, float]]
) -> None:
    msg.table(
        [(k, f"{v:.2f}") for k, v in scores.items()],
        header=("", "ROC AUC"),
        aligns=("l", "r"),
        title="Textcat ROC AUC (per label)",
    )
