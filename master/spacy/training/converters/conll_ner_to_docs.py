from wasabi import Printer

from .. import tags_to_entities
from ...training import iob_to_biluo
from ...tokens import Doc, Span
from ...errors import Errors
from ...util import load_model, get_lang_class


def conll_ner_to_docs(
    input_data, n_sents=10, seg_sents=False, model=None, no_print=False, **kwargs
):
    """
    Convert files in the CoNLL-2003 NER format and similar
    whitespace-separated columns into Doc objects.

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
                f"No sentence boundaries found to use with option `-n {n_sents}`. "
                f"Use `-s` to automatically segment sentences or `-n 0` "
                f"to disable."
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

    if model:
        nlp = load_model(model)
    else:
        nlp = get_lang_class("xx")()
    for conll_doc in input_data.strip().split(doc_delimiter):
        conll_doc = conll_doc.strip()
        if not conll_doc:
            continue
        words = []
        sent_starts = []
        pos_tags = []
        biluo_tags = []
        for conll_sent in conll_doc.split("\n\n"):
            conll_sent = conll_sent.strip()
            if not conll_sent:
                continue
            lines = [line.strip() for line in conll_sent.split("\n") if line.strip()]
            cols = list(zip(*[line.split() for line in lines]))
            if len(cols) < 2:
                raise ValueError(Errors.E903)
            length = len(cols[0])
            words.extend(cols[0])
            sent_starts.extend([True] + [False] * (length - 1))
            biluo_tags.extend(iob_to_biluo(cols[-1]))
            pos_tags.extend(cols[1] if len(cols) > 2 else ["-"] * length)

        doc = Doc(nlp.vocab, words=words)
        for i, token in enumerate(doc):
            token.tag_ = pos_tags[i]
            token.is_sent_start = sent_starts[i]
        entities = tags_to_entities(biluo_tags)
        doc.ents = [Span(doc, start=s, end=e + 1, label=L) for L, s, e in entities]
        yield doc


def segment_sents_and_docs(doc, n_sents, doc_delimiter, model=None, msg=None):
    sentencizer = None
    if model:
        nlp = load_model(model)
        if "parser" in nlp.pipe_names:
            msg.info(f"Segmenting sentences with parser from model '{model}'.")
            for name, proc in nlp.pipeline:
                if "parser" in getattr(proc, "listening_components", []):
                    nlp.replace_listeners(name, "parser", ["model.tok2vec"])
            sentencizer = nlp.get_pipe("parser")
    if not sentencizer:
        msg.info(
            "Segmenting sentences with sentencizer. (Use `-b model` for "
            "improved parser-based sentence segmentation.)"
        )
        nlp = get_lang_class("xx")()
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
    msg.info(f"Grouping every {n_sents} sentences into a document.")
    if n_sents == 1:
        msg.warn(
            "To generate better training data, you may want to group "
            "sentences into documents with `-n 10`."
        )
