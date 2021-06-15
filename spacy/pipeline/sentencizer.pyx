# cython: infer_types=True, profile=True, binding=True
from typing import Optional, List
import srsly

from ..tokens.doc cimport Doc
from .pipe import Pipe
from ..language import Language
from ..scorer import Scorer
from ..training import validate_examples
from .. import util

@Language.factory(
    "sentencizer",
    assigns=["token.is_sent_start", "doc.sents"],
    default_config={"punct_chars": None},
    default_score_weights={"sents_f": 1.0, "sents_p": 0.0, "sents_r": 0.0},
)
def make_sentencizer(
    nlp: Language,
    name: str,
    punct_chars: Optional[List[str]]
):
    return Sentencizer(name, punct_chars=punct_chars)


class Sentencizer(Pipe):
    """Segment the Doc into sentences using a rule-based strategy.

    DOCS: https://spacy.io/api/sentencizer
    """

    default_punct_chars = ['!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '߹',
            '।', '॥', '၊', '။', '።', '፧', '፨', '᙮', '᜵', '᜶', '᠃', '᠉', '᥄',
            '᥅', '᪨', '᪩', '᪪', '᪫', '᭚', '᭛', '᭞', '᭟', '᰻', '᰼', '᱾', '᱿',
            '‼', '‽', '⁇', '⁈', '⁉', '⸮', '⸼', '꓿', '꘎', '꘏', '꛳', '꛷', '꡶',
            '꡷', '꣎', '꣏', '꤯', '꧈', '꧉', '꩝', '꩞', '꩟', '꫰', '꫱', '꯫', '﹒',
            '﹖', '﹗', '！', '．', '？', '𐩖', '𐩗', '𑁇', '𑁈', '𑂾', '𑂿', '𑃀',
            '𑃁', '𑅁', '𑅂', '𑅃', '𑇅', '𑇆', '𑇍', '𑇞', '𑇟', '𑈸', '𑈹', '𑈻', '𑈼',
            '𑊩', '𑑋', '𑑌', '𑗂', '𑗃', '𑗉', '𑗊', '𑗋', '𑗌', '𑗍', '𑗎', '𑗏', '𑗐',
            '𑗑', '𑗒', '𑗓', '𑗔', '𑗕', '𑗖', '𑗗', '𑙁', '𑙂', '𑜼', '𑜽', '𑜾', '𑩂',
            '𑩃', '𑪛', '𑪜', '𑱁', '𑱂', '𖩮', '𖩯', '𖫵', '𖬷', '𖬸', '𖭄', '𛲟', '𝪈',
            '｡', '。']

    def __init__(self, name="sentencizer", *, punct_chars=None):
        """Initialize the sentencizer.

        punct_chars (list): Punctuation characters to split on. Will be
            serialized with the nlp object.
        RETURNS (Sentencizer): The sentencizer component.

        DOCS: https://spacy.io/api/sentencizer#init
        """
        self.name = name
        if punct_chars:
            self.punct_chars = set(punct_chars)
        else:
            self.punct_chars = set(self.default_punct_chars)

    def __call__(self, doc):
        """Apply the sentencizer to a Doc and set Token.is_sent_start.

        doc (Doc): The document to process.
        RETURNS (Doc): The processed Doc.

        DOCS: https://spacy.io/api/sentencizer#call
        """
        error_handler = self.get_error_handler()
        try:
            tags = self.predict([doc])
            self.set_annotations([doc], tags)
            return doc
        except Exception as e:
            error_handler(self.name, self, [doc], e)

    def predict(self, docs):
        """Apply the pipe to a batch of docs, without modifying them.

        docs (Iterable[Doc]): The documents to predict.
        RETURNS: The predictions for each document.
        """
        if not any(len(doc) for doc in docs):
            # Handle cases where there are no tokens in any docs.
            guesses = [[] for doc in docs]
            return guesses
        guesses = []
        for doc in docs:
            doc_guesses = [False] * len(doc)
            if len(doc) > 0:
                start = 0
                seen_period = False
                doc_guesses[0] = True
                for i, token in enumerate(doc):
                    is_in_punct_chars = token.text in self.punct_chars
                    if seen_period and not token.is_punct and not is_in_punct_chars:
                        doc_guesses[start] = True
                        start = token.i
                        seen_period = False
                    elif is_in_punct_chars:
                        seen_period = True
                if start < len(doc):
                    doc_guesses[start] = True
            guesses.append(doc_guesses)
        return guesses

    def set_annotations(self, docs, batch_tag_ids):
        """Modify a batch of documents, using pre-computed scores.

        docs (Iterable[Doc]): The documents to modify.
        scores: The tag IDs produced by Sentencizer.predict.
        """
        if isinstance(docs, Doc):
            docs = [docs]
        cdef Doc doc
        cdef int idx = 0
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            for j, tag_id in enumerate(doc_tag_ids):
                # Don't clobber existing sentence boundaries
                if doc.c[j].sent_start == 0:
                    if tag_id:
                        doc.c[j].sent_start = 1
                    else:
                        doc.c[j].sent_start = -1

    def score(self, examples, **kwargs):
        """Score a batch of examples.

        examples (Iterable[Example]): The examples to score.
        RETURNS (Dict[str, Any]): The scores, produced by Scorer.score_spans.

        DOCS: https://spacy.io/api/sentencizer#score
        """
        def has_sents(doc):
            return doc.has_annotation("SENT_START")

        validate_examples(examples, "Sentencizer.score")
        results = Scorer.score_spans(examples, "sents", has_annotation=has_sents, **kwargs)
        del results["sents_per_type"]
        return results

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the sentencizer to a bytestring.

        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/sentencizer#to_bytes
        """
        return srsly.msgpack_dumps({"punct_chars": list(self.punct_chars)})

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load the sentencizer from a bytestring.

        bytes_data (bytes): The data to load.
        returns (Sentencizer): The loaded object.

        DOCS: https://spacy.io/api/sentencizer#from_bytes
        """
        cfg = srsly.msgpack_loads(bytes_data)
        self.punct_chars = set(cfg.get("punct_chars", self.default_punct_chars))
        return self

    def to_disk(self, path, *, exclude=tuple()):
        """Serialize the sentencizer to disk.

        DOCS: https://spacy.io/api/sentencizer#to_disk
        """
        path = util.ensure_path(path)
        path = path.with_suffix(".json")
        srsly.write_json(path, {"punct_chars": list(self.punct_chars)})


    def from_disk(self, path, *, exclude=tuple()):
        """Load the sentencizer from disk.

        DOCS: https://spacy.io/api/sentencizer#from_disk
        """
        path = util.ensure_path(path)
        path = path.with_suffix(".json")
        cfg = srsly.read_json(path)
        self.punct_chars = set(cfg.get("punct_chars", self.default_punct_chars))
        return self
