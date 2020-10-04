from typing import Optional, List, Dict
from wasabi import Printer
from pathlib import Path
import re
import srsly
from thinc.api import fix_random_seed

from ..training import Corpus
from ..tokens import Doc
from ._util import app, Arg, Opt, setup_gpu, import_code
from ..scorer import Scorer
from .. import util
from .. import displacy


@app.command("evaluate")
def evaluate_cli(
    # fmt: off
    model: str = Arg(..., help="Model name or path"),
    data_path: Path = Arg(..., help="Location of binary evaluation data in .spacy format", exists=True),
    output: Optional[Path] = Opt(None, "--output", "-o", help="Output JSON file for metrics", dir_okay=False),
    code_path: Optional[Path] = Opt(None, "--code", "-c", help="Path to Python file with additional code (registered functions) to be imported"),
    use_gpu: int = Opt(-1, "--gpu-id", "-g", help="GPU ID or -1 for CPU"),
    gold_preproc: bool = Opt(False, "--gold-preproc", "-G", help="Use gold preprocessing"),
    displacy_path: Optional[Path] = Opt(None, "--displacy-path", "-dp", help="Directory to output rendered parses as HTML", exists=True, file_okay=False),
    displacy_limit: int = Opt(25, "--displacy-limit", "-dl", help="Limit of parses to render as HTML"),
    # fmt: on
):
    """
    Evaluate a trained pipeline. Expects a loadable spaCy pipeline and evaluation
    data in the binary .spacy format. The --gold-preproc option sets up the
    evaluation examples with gold-standard sentences and tokens for the
    predictions. Gold preprocessing helps the annotations align to the
    tokenization, and may result in sequences of more consistent length. However,
    it may reduce runtime accuracy due to train/test skew. To render a sample of
    dependency parses in a HTML file, set as output directory as the
    displacy_path argument.

    DOCS: https://nightly.spacy.io/api/cli#evaluate
    """
    import_code(code_path)
    evaluate(
        model,
        data_path,
        output=output,
        use_gpu=use_gpu,
        gold_preproc=gold_preproc,
        displacy_path=displacy_path,
        displacy_limit=displacy_limit,
        silent=False,
    )


def evaluate(
    model: str,
    data_path: Path,
    output: Optional[Path] = None,
    use_gpu: int = -1,
    gold_preproc: bool = False,
    displacy_path: Optional[Path] = None,
    displacy_limit: int = 25,
    silent: bool = True,
) -> Scorer:
    msg = Printer(no_print=silent, pretty=not silent)
    fix_random_seed()
    setup_gpu(use_gpu)
    data_path = util.ensure_path(data_path)
    output_path = util.ensure_path(output)
    displacy_path = util.ensure_path(displacy_path)
    if not data_path.exists():
        msg.fail("Evaluation data not found", data_path, exits=1)
    if displacy_path and not displacy_path.exists():
        msg.fail("Visualization output directory not found", displacy_path, exits=1)
    corpus = Corpus(data_path, gold_preproc=gold_preproc)
    nlp = util.load_model(model)
    dev_dataset = list(corpus(nlp))
    scores = nlp.evaluate(dev_dataset)
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
        "TEXTCAT": "cats_score",
        "SENT P": "sents_p",
        "SENT R": "sents_r",
        "SENT F": "sents_f",
        "SPEED": "speed",
    }
    results = {}
    for metric, key in metrics.items():
        if key in scores:
            if key == "cats_score":
                metric = metric + " (" + scores.get("cats_score_desc", "unk") + ")"
            if key == "speed":
                results[metric] = f"{scores[key]:.0f}"
            else:
                results[metric] = f"{scores[key]*100:.2f}"
    data = {re.sub(r"[\s/]", "_", k.lower()): v for k, v in results.items()}

    msg.table(results, title="Results")

    if "ents_per_type" in scores:
        if scores["ents_per_type"]:
            print_ents_per_type(msg, scores["ents_per_type"])
    if "cats_f_per_type" in scores:
        if scores["cats_f_per_type"]:
            print_textcats_f_per_cat(msg, scores["cats_f_per_type"])
    if "cats_auc_per_type" in scores:
        if scores["cats_auc_per_type"]:
            print_textcats_auc_per_cat(msg, scores["cats_auc_per_type"])

    if displacy_path:
        factory_names = [nlp.get_pipe_meta(pipe).factory for pipe in nlp.pipe_names]
        docs = [ex.predicted for ex in dev_dataset]
        render_deps = "parser" in factory_names
        render_ents = "ner" in factory_names
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
        title="Textcat F (per label)",
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
