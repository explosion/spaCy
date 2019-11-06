# flake8: noqa
"""Train for CONLL 2017 UD treebank evaluation. Takes .conllu files, writes
.conllu format for development data, allowing the official scorer to be used.
"""
from __future__ import unicode_literals

import plac
from pathlib import Path
import re
import sys
import srsly

import spacy
import spacy.util
from spacy.tokens import Token, Doc
from spacy.gold import GoldParse
from spacy.util import compounding, minibatch_by_words
from spacy.syntax.nonproj import projectivize
from spacy.matcher import Matcher

# from spacy.morphology import Fused_begin, Fused_inside
from spacy import displacy
from collections import defaultdict, Counter
from timeit import default_timer as timer

Fused_begin = None
Fused_inside = None

import itertools
import random
import numpy.random

from . import conll17_ud_eval

from spacy import lang
from spacy.lang import zh
from spacy.lang import ja
from spacy.lang import ru


################
# Data reading #
################

space_re = re.compile(r"\s+")


def split_text(text):
    return [space_re.sub(" ", par.strip()) for par in text.split("\n\n")]


##############
# Evaluation #
##############


def read_conllu(file_):
    docs = []
    sent = []
    doc = []
    for line in file_:
        if line.startswith("# newdoc"):
            if doc:
                docs.append(doc)
            doc = []
        elif line.startswith("#"):
            continue
        elif not line.strip():
            if sent:
                doc.append(sent)
            sent = []
        else:
            sent.append(list(line.strip().split("\t")))
            if len(sent[-1]) != 10:
                print(repr(line))
                raise ValueError
    if sent:
        doc.append(sent)
    if doc:
        docs.append(doc)
    return docs


def evaluate(nlp, text_loc, gold_loc, sys_loc, limit=None):
    if text_loc.parts[-1].endswith(".conllu"):
        docs = []
        with text_loc.open(encoding="utf8") as file_:
            for conllu_doc in read_conllu(file_):
                for conllu_sent in conllu_doc:
                    words = [line[1] for line in conllu_sent]
                    docs.append(Doc(nlp.vocab, words=words))
        for name, component in nlp.pipeline:
            docs = list(component.pipe(docs))
    else:
        with text_loc.open("r", encoding="utf8") as text_file:
            texts = split_text(text_file.read())
            docs = list(nlp.pipe(texts))
    with sys_loc.open("w", encoding="utf8") as out_file:
        write_conllu(docs, out_file)
    with gold_loc.open("r", encoding="utf8") as gold_file:
        gold_ud = conll17_ud_eval.load_conllu(gold_file)
        with sys_loc.open("r", encoding="utf8") as sys_file:
            sys_ud = conll17_ud_eval.load_conllu(sys_file)
        scores = conll17_ud_eval.evaluate(gold_ud, sys_ud)
    return docs, scores


def write_conllu(docs, file_):
    merger = Matcher(docs[0].vocab)
    merger.add("SUBTOK", None, [{"DEP": "subtok", "op": "+"}])
    for i, doc in enumerate(docs):
        matches = []
        if doc.is_parsed:
            matches = merger(doc)
        spans = [doc[start : end + 1] for _, start, end in matches]
        with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)
        file_.write("# newdoc id = {i}\n".format(i=i))
        for j, sent in enumerate(doc.sents):
            file_.write("# sent_id = {i}.{j}\n".format(i=i, j=j))
            file_.write("# text = {text}\n".format(text=sent.text))
            for k, token in enumerate(sent):
                file_.write(_get_token_conllu(token, k, len(sent)) + "\n")
            file_.write("\n")
            for word in sent:
                if word.head.i == word.i and word.dep_ == "ROOT":
                    break
            else:
                print("Rootless sentence!")
                print(sent)
                print(i)
                for w in sent:
                    print(w.i, w.text, w.head.text, w.head.i, w.dep_)
                raise ValueError


def _get_token_conllu(token, k, sent_len):
    if token.check_morph(Fused_begin) and (k + 1 < sent_len):
        n = 1
        text = [token.text]
        while token.nbor(n).check_morph(Fused_inside):
            text.append(token.nbor(n).text)
            n += 1
        id_ = "%d-%d" % (k + 1, (k + n))
        fields = [id_, "".join(text)] + ["_"] * 8
        lines = ["\t".join(fields)]
    else:
        lines = []
    if token.head.i == token.i:
        head = 0
    else:
        head = k + (token.head.i - token.i) + 1
    fields = [
        str(k + 1),
        token.text,
        token.lemma_,
        token.pos_,
        token.tag_,
        "_",
        str(head),
        token.dep_.lower(),
        "_",
        "_",
    ]
    if token.check_morph(Fused_begin) and (k + 1 < sent_len):
        if k == 0:
            fields[1] = token.norm_[0].upper() + token.norm_[1:]
        else:
            fields[1] = token.norm_
    elif token.check_morph(Fused_inside):
        fields[1] = token.norm_
    elif token._.split_start is not None:
        split_start = token._.split_start
        split_end = token._.split_end
        split_len = (split_end.i - split_start.i) + 1
        n_in_split = token.i - split_start.i
        subtokens = guess_fused_orths(split_start.text, [""] * split_len)
        fields[1] = subtokens[n_in_split]

    lines.append("\t".join(fields))
    return "\n".join(lines)


def guess_fused_orths(word, ud_forms):
    """The UD data 'fused tokens' don't necessarily expand to keys that match
    the form. We need orths that exact match the string. Here we make a best
    effort to divide up the word."""
    if word == "".join(ud_forms):
        # Happy case: we get a perfect split, with each letter accounted for.
        return ud_forms
    elif len(word) == sum(len(subtoken) for subtoken in ud_forms):
        # Unideal, but at least lengths match.
        output = []
        remain = word
        for subtoken in ud_forms:
            assert len(subtoken) >= 1
            output.append(remain[: len(subtoken)])
            remain = remain[len(subtoken) :]
        assert len(remain) == 0, (word, ud_forms, remain)
        return output
    else:
        # Let's say word is 6 long, and there are three subtokens. The orths
        # *must* equal the original string. Arbitrarily, split [4, 1, 1]
        first = word[: len(word) - (len(ud_forms) - 1)]
        output = [first]
        remain = word[len(first) :]
        for i in range(1, len(ud_forms)):
            assert remain
            output.append(remain[:1])
            remain = remain[1:]
        assert len(remain) == 0, (word, output, remain)
        return output


def print_results(name, ud_scores):
    fields = {}
    if ud_scores is not None:
        fields.update(
            {
                "words": ud_scores["Words"].f1 * 100,
                "sents": ud_scores["Sentences"].f1 * 100,
                "tags": ud_scores["XPOS"].f1 * 100,
                "uas": ud_scores["UAS"].f1 * 100,
                "las": ud_scores["LAS"].f1 * 100,
            }
        )
    else:
        fields.update({"words": 0.0, "sents": 0.0, "tags": 0.0, "uas": 0.0, "las": 0.0})
    tpl = "\t".join(
        (name, "{las:.1f}", "{uas:.1f}", "{tags:.1f}", "{sents:.1f}", "{words:.1f}")
    )
    print(tpl.format(**fields))
    return fields


def get_token_split_start(token):
    if token.text == "":
        assert token.i != 0
        i = -1
        while token.nbor(i).text == "":
            i -= 1
        return token.nbor(i)
    elif (token.i + 1) < len(token.doc) and token.nbor(1).text == "":
        return token
    else:
        return None


def get_token_split_end(token):
    if (token.i + 1) == len(token.doc):
        return token if token.text == "" else None
    elif token.text != "" and token.nbor(1).text != "":
        return None
    i = 1
    while (token.i + i) < len(token.doc) and token.nbor(i).text == "":
        i += 1
    return token.nbor(i - 1)


##################
# Initialization #
##################


def load_nlp(experiments_dir, corpus):
    nlp = spacy.load(experiments_dir / corpus / "best-model")
    return nlp


def initialize_pipeline(nlp, docs, golds, config, device):
    nlp.add_pipe(nlp.create_pipe("parser"))
    return nlp


@plac.annotations(
    test_data_dir=(
        "Path to Universal Dependencies test data",
        "positional",
        None,
        Path,
    ),
    experiment_dir=("Parent directory with output model", "positional", None, Path),
    corpus=(
        "UD corpus to evaluate, e.g. UD_English, UD_Spanish, etc",
        "positional",
        None,
        str,
    ),
)
def main(test_data_dir, experiment_dir, corpus):
    Token.set_extension("split_start", getter=get_token_split_start)
    Token.set_extension("split_end", getter=get_token_split_end)
    Token.set_extension("begins_fused", default=False)
    Token.set_extension("inside_fused", default=False)
    lang.zh.Chinese.Defaults.use_jieba = False
    lang.ja.Japanese.Defaults.use_janome = False
    lang.ru.Russian.Defaults.use_pymorphy2 = False

    nlp = load_nlp(experiment_dir, corpus)

    treebank_code = nlp.meta["treebank"]
    for section in ("test", "dev"):
        if section == "dev":
            section_dir = "conll17-ud-development-2017-03-19"
        else:
            section_dir = "conll17-ud-test-2017-05-09"
        text_path = test_data_dir / "input" / section_dir / (treebank_code + ".txt")
        udpipe_path = (
            test_data_dir / "input" / section_dir / (treebank_code + "-udpipe.conllu")
        )
        gold_path = test_data_dir / "gold" / section_dir / (treebank_code + ".conllu")

        header = [section, "LAS", "UAS", "TAG", "SENT", "WORD"]
        print("\t".join(header))
        inputs = {"gold": gold_path, "udp": udpipe_path, "raw": text_path}
        for input_type in ("udp", "raw"):
            input_path = inputs[input_type]
            output_path = (
                experiment_dir / corpus / "{section}.conllu".format(section=section)
            )

            parsed_docs, test_scores = evaluate(nlp, input_path, gold_path, output_path)

            accuracy = print_results(input_type, test_scores)
            acc_path = (
                experiment_dir
                / corpus
                / "{section}-accuracy.json".format(section=section)
            )
            srsly.write_json(acc_path, accuracy)


if __name__ == "__main__":
    plac.call(main)
