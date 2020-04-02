from timeit import default_timer as timer
from wasabi import msg

from ..gold import GoldCorpus
from .. import util
from .. import displacy


def evaluate(
    # fmt: off
    model: ("Model name or path", "positional", None, str),
    data_path: ("Location of JSON-formatted evaluation data", "positional", None, str),
    gpu_id: ("Use GPU", "option", "g", int) = -1,
    gold_preproc: ("Use gold preprocessing", "flag", "G", bool) = False,
    displacy_path: ("Directory to output rendered parses as HTML", "option", "dp", str) = None,
    displacy_limit: ("Limit of parses to render as HTML", "option", "dl", int) = 25,
    return_scores: ("Return dict containing model scores", "flag", "R", bool) = False,
    # fmt: on
):
    """
    Evaluate a model. To render a sample of parses in a HTML file, set an
    output directory as the displacy_path argument.
    """
    util.fix_random_seed()
    if gpu_id >= 0:
        util.use_gpu(gpu_id)
    util.set_env_log(False)
    data_path = util.ensure_path(data_path)
    displacy_path = util.ensure_path(displacy_path)
    if not data_path.exists():
        msg.fail("Evaluation data not found", data_path, exits=1)
    if displacy_path and not displacy_path.exists():
        msg.fail("Visualization output directory not found", displacy_path, exits=1)
    corpus = GoldCorpus(data_path, data_path)
    nlp = util.load_model(model)
    dev_dataset = list(corpus.dev_dataset(nlp, gold_preproc=gold_preproc))
    begin = timer()
    scorer = nlp.evaluate(dev_dataset, verbose=False)
    end = timer()
    nwords = sum(len(ex.doc) for ex in dev_dataset)
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
        "Textcat": f"{scorer.textcat_score:.2f}",
        "Sent P": f"{scorer.sent_p:.2f}",
        "Sent R": f"{scorer.sent_r:.2f}",
        "Sent F": f"{scorer.sent_f:.2f}",
    }
    msg.table(results, title="Results")

    if displacy_path:
        docs = [ex.doc for ex in dev_dataset]
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
    if return_scores:
        return scorer.scores


def render_parses(docs, output_path, model_name="", limit=250, deps=True, ents=True):
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
