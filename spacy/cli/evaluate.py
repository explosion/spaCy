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
    scorer = nlp.evaluate(dev_dataset, verbose=False)
    end = timer()
    nwords = sum(len(ex.predicted) for ex in dev_dataset)
    results = {
        "Time": f"{end - begin:.2f} s",
        "Words": nwords,
        "Words/s": f"{nwords / (end - begin):.0f}",
        "TOK": f"{scorer.token_acc:.2f}",
        "TAG": f"{scorer.tags_acc:.2f}",
        "POS": f"{scorer.pos_acc:.2f}",
        "MORPH": f"{scorer.morphs_acc:.2f}",
        "UAS": f"{scorer.uas:.2f}",
        "LAS": f"{scorer.las:.2f}",
        "NER P": f"{scorer.ents_p:.2f}",
        "NER R": f"{scorer.ents_r:.2f}",
        "NER F": f"{scorer.ents_f:.2f}",
        "Textcat AUC": f"{scorer.textcat_auc:.2f}",
        "Textcat F": f"{scorer.textcat_f:.2f}",
        "Sent P": f"{scorer.sent_p:.2f}",
        "Sent R": f"{scorer.sent_r:.2f}",
        "Sent F": f"{scorer.sent_f:.2f}",
    }
    data = {re.sub(r"[\s/]", "_", k.lower()): v for k, v in results.items()}

    msg.table(results, title="Results")

    if scorer.ents_per_type:
        data["ents_per_type"] = scorer.ents_per_type
        print_ents_per_type(msg, scorer.ents_per_type)
    if scorer.textcats_f_per_cat:
        data["textcats_f_per_cat"] = scorer.textcats_f_per_cat
        print_textcats_f_per_cat(msg, scorer.textcats_f_per_cat)
    if scorer.textcats_auc_per_cat:
        data["textcats_auc_per_cat"] = scorer.textcats_auc_per_cat
        print_textcats_auc_per_cat(msg, scorer.textcats_auc_per_cat)

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
        (k, f"{v['p']:.2f}", f"{v['r']:.2f}", f"{v['f']:.2f}")
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
        (k, f"{v['p']:.2f}", f"{v['r']:.2f}", f"{v['f']:.2f}")
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
        [(k, f"{v['roc_auc_score']:.2f}") for k, v in scores.items()],
        header=("", "ROC AUC"),
        aligns=("l", "r"),
        title="Textcat ROC AUC (per label)",
    )
