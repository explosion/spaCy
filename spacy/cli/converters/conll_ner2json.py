# coding: utf8
from __future__ import unicode_literals

from wasabi import Printer

from ...gold import iob_to_biluo
from ...lang.xx import MultiLanguage
from ...tokens.doc import Doc
from ...util import load_model


def conll_ner2json(
    input_data, n_sents=10, seg_sents=False, model=None, no_print=False, **kwargs
):
    """
    Convert files in the CoNLL-2003 NER format and similar
    whitespace-separated columns into JSON format for use with train cli.

    The first column is the tokens, the final column is the IOB tags. If an
    additional second column is present, the second column is the tags.

    Sentences are separated with whitespace and documents can be separated
    using the line "-DOCSTART- -X- O O".

    Sample format:

    -DOCSTART- -X- O O

    I O
    like O
    London B-GPE
    and O
    New B-GPE
    York I-GPE
    City I-GPE
    . O

    """
    msg = Printer(no_print=no_print)
    doc_delimiter = "-DOCSTART- -X- O O"
    # check for existing delimiters, which should be preserved
    if "\n\n" in input_data and seg_sents:
        msg.warn(
            "Sentence boundaries found, automatic sentence segmentation with "
            "`-s` disabled."
        )
        seg_sents = False
    if doc_delimiter in input_data and n_sents:
        msg.warn(
            "Document delimiters found, automatic document segmentation with "
            "`-n` disabled."
        )
        n_sents = 0
    # do document segmentation with existing sentences
    if "\n\n" in input_data and doc_delimiter not in input_data and n_sents:
        n_sents_info(msg, n_sents)
        input_data = segment_docs(input_data, n_sents, doc_delimiter)
    # do sentence segmentation with existing documents
    if "\n\n" not in input_data and doc_delimiter in input_data and seg_sents:
        input_data = segment_sents_and_docs(input_data, 0, "", model=model, msg=msg)
    # do both sentence segmentation and document segmentation according
    # to options
    if "\n\n" not in input_data and doc_delimiter not in input_data:
        # sentence segmentation required for document segmentation
        if n_sents > 0 and not seg_sents:
            msg.warn(
                "No sentence boundaries found to use with option `-n {}`. "
                "Use `-s` to automatically segment sentences or `-n 0` "
                "to disable.".format(n_sents)
            )
        else:
            n_sents_info(msg, n_sents)
            input_data = segment_sents_and_docs(
                input_data, n_sents, doc_delimiter, model=model, msg=msg
            )
    # provide warnings for problematic data
    if "\n\n" not in input_data:
        msg.warn(
            "No sentence boundaries found. Use `-s` to automatically segment "
            "sentences."
        )
    if doc_delimiter not in input_data:
        msg.warn(
            "No document delimiters found. Use `-n` to automatically group "
            "sentences into documents."
        )
    output_docs = []
    for doc in input_data.strip().split(doc_delimiter):
        doc = doc.strip()
        if not doc:
            continue
        output_doc = []
        for sent in doc.split("\n\n"):
            sent = sent.strip()
            if not sent:
                continue
            lines = [line.strip() for line in sent.split("\n") if line.strip()]
            cols = list(zip(*[line.split() for line in lines]))
            if len(cols) < 2:
                raise ValueError(
                    "The token-per-line NER file is not formatted correctly. "
                    "Try checking whitespace and delimiters. See "
                    "https://spacy.io/api/cli#convert"
                )
            words = cols[0]
            iob_ents = cols[-1]
            if len(cols) > 2:
                tags = cols[1]
            else:
                tags = ["-"] * len(words)
            biluo_ents = iob_to_biluo(iob_ents)
            output_doc.append(
                {
                    "tokens": [
                        {"orth": w, "tag": tag, "ner": ent}
                        for (w, tag, ent) in zip(words, tags, biluo_ents)
                    ]
                }
            )
        output_docs.append(
            {"id": len(output_docs), "paragraphs": [{"sentences": output_doc}]}
        )
        output_doc = []
    return output_docs


def segment_sents_and_docs(doc, n_sents, doc_delimiter, model=None, msg=None):
    sentencizer = None
    if model:
        nlp = load_model(model)
        if "parser" in nlp.pipe_names:
            msg.info("Segmenting sentences with parser from model '{}'.".format(model))
            sentencizer = nlp.get_pipe("parser")
    if not sentencizer:
        msg.info(
            "Segmenting sentences with sentencizer. (Use `-b model` for "
            "improved parser-based sentence segmentation.)"
        )
        nlp = MultiLanguage()
        sentencizer = nlp.create_pipe("sentencizer")
    lines = doc.strip().split("\n")
    words = [line.strip().split()[0] for line in lines]
    nlpdoc = Doc(nlp.vocab, words=words)
    sentencizer(nlpdoc)
    lines_with_segs = []
    sent_count = 0
    for i, token in enumerate(nlpdoc):
        if token.is_sent_start:
            if n_sents and sent_count % n_sents == 0:
                lines_with_segs.append(doc_delimiter)
            lines_with_segs.append("")
            sent_count += 1
        lines_with_segs.append(lines[i])
    return "\n".join(lines_with_segs)


def segment_docs(input_data, n_sents, doc_delimiter):
    sent_delimiter = "\n\n"
    sents = input_data.split(sent_delimiter)
    docs = [sents[i : i + n_sents] for i in range(0, len(sents), n_sents)]
    input_data = ""
    for doc in docs:
        input_data += sent_delimiter + doc_delimiter
        input_data += sent_delimiter.join(doc)
    return input_data


def n_sents_info(msg, n_sents):
    msg.info("Grouping every {} sentences into a document.".format(n_sents))
    if n_sents == 1:
        msg.warn(
            "To generate better training data, you may want to group "
            "sentences into documents with `-n 10`."
        )
