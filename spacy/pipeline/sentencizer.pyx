# cython: infer_types=True, binding=True
import importlib
import sys
from typing import Callable, List, Optional

import srsly

from ..tokens.doc cimport Doc

from .. import util
from ..language import Language
from .pipe import Pipe
from .senter import senter_score

# see #9050
BACKWARD_OVERWRITE = False


class Sentencizer(Pipe):
    """Segment the Doc into sentences using a rule-based strategy.

    DOCS: https://spacy.io/api/sentencizer
    """

    default_punct_chars = [
        '!', '.', '?', '։', '؟', '۔', '܀', '܁', '܂', '߹',
        '।', '॥', '၊', '။', '።', '፧', '፨', '᙮', '᜵', '᜶', '᠃', '᠉', '᥄',
        '᥅', '᪨', '᪩', '᪪', '᪫', '᭚', '᭛', '᭞', '᭟', '᰻', '᰼', '᱾', '᱿',
        '‼', '‽', '⁇', '⁈', '⁉', '⸮', '⸼', '꓿', '꘎', '꘏', '꛳', '꛷', '꡶',
        '꡷', '꣎', '꣏', '꤯', '꧈', '꧉', '꩝', '꩞', '꩟', '꫰', '꫱', '꯫', '﹒',
        '﹖', '﹗', '！', '．', '？', '𐩖', '𐩗', '𑁇', '𑁈', '𑂾', '𑂿', '𑃀',
        '𑃁', '𑅁', '𑅂', '𑅃', '𑇅', '𑇆', '𑇍', '𑇞', '𑇟', '𑈸', '𑈹', '𑈻', '𑈼',
        '𑊩', '𑑋', '𑑌', '𑗂', '𑗃', '𑗉', '𑗊', '𑗋', '𑗌', '𑗍', '𑗎', '𑗏', '𑗐',
        '𑗑', '𑗒', '𑗓', '𑗔', '𑗕', '𑗖', '𑗗', '𑙁', '𑙂', '𑜼', '𑜽', '𑜾', '𑩂',
        '𑩃', '𑪛', '𑪜', '𑱁', '𑱂', '𖩮', '𖩯', '𖫵', '𖬷', '𖬸', '𖭄', '𛲟', '𝪈',
        '｡', '。'
    ]

    def __init__(
        self,
        name="sentencizer",
        *,
        punct_chars=None,
        overwrite=BACKWARD_OVERWRITE,
        scorer=senter_score,
    ):
        """Initialize the sentencizer.

        punct_chars (list): Punctuation characters to split on. Will be
            serialized with the nlp object.
        scorer (Optional[Callable]): The scoring method. Defaults to
            Scorer.score_spans for the attribute "sents".

        DOCS: https://spacy.io/api/sentencizer#init
        """
        self.name = name
        if punct_chars:
            self.punct_chars = set(punct_chars)
        else:
            self.punct_chars = set(self.default_punct_chars)
        self.overwrite = overwrite
        self.scorer = scorer

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
                # Track quote nesting depth to defer sentence boundary detection when
                # sentence-ending punctuation appears within quoted text
                quote_depth = 0
                pending_split_after_quote = False
                doc_guesses[0] = True
                for i, token in enumerate(doc):
                    is_in_punct_chars = token.text in self.punct_chars
                    
                    # Update quote depth to track whether the current position is within quoted text.
                    # This prevents premature sentence splitting when punctuation appears inside quotes.
                    if token.is_quote:
                        if token.is_left_punct and token.is_right_punct:
                            # Symmetric quotes toggle quote state based on current depth.
                            # If currently outside quotes, the quote acts as an opening quote.
                            # If currently inside quotes, the quote acts as a closing quote.
                            quote_depth = 1 if quote_depth == 0 else quote_depth - 1
                        elif token.is_left_punct:
                            # Asymmetric opening quote (e.g., «, ", ').
                            quote_depth += 1
                        elif token.is_right_punct:
                            # Asymmetric closing quote (e.g., », ", ').
                            quote_depth -= 1
                            # Ensure quote_depth does not go negative to handle unopened quotes gracefully.
                            if quote_depth < 0:
                                quote_depth = 0
                    
                    # Handle sentence-ending punctuation.
                    if is_in_punct_chars:
                        seen_period = True
                        # Defer sentence boundary until after closing quote when punctuation
                        # appears within quoted text. This ensures quoted dialogue is not split
                        # at punctuation marks that appear inside the quotes.
                        if quote_depth > 0:
                            pending_split_after_quote = True
                    elif seen_period and not token.is_punct and not is_in_punct_chars:
                        # Create sentence boundary when outside quoted text.
                        # Only split when quote_depth is zero to avoid splitting within quoted dialogue.
                        if quote_depth == 0:
                            if pending_split_after_quote:
                                pending_split_after_quote = False
                            doc_guesses[start] = True
                            start = token.i
                            seen_period = False
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
        for i, doc in enumerate(docs):
            doc_tag_ids = batch_tag_ids[i]
            for j, tag_id in enumerate(doc_tag_ids):
                if doc.c[j].sent_start == 0 or self.overwrite:
                    if tag_id:
                        doc.c[j].sent_start = 1
                    else:
                        doc.c[j].sent_start = -1

    def to_bytes(self, *, exclude=tuple()):
        """Serialize the sentencizer to a bytestring.

        RETURNS (bytes): The serialized object.

        DOCS: https://spacy.io/api/sentencizer#to_bytes
        """
        return srsly.msgpack_dumps({"punct_chars": list(self.punct_chars), "overwrite": self.overwrite})

    def from_bytes(self, bytes_data, *, exclude=tuple()):
        """Load the sentencizer from a bytestring.

        bytes_data (bytes): The data to load.
        returns (Sentencizer): The loaded object.

        DOCS: https://spacy.io/api/sentencizer#from_bytes
        """
        cfg = srsly.msgpack_loads(bytes_data)
        self.punct_chars = set(cfg.get("punct_chars", self.default_punct_chars))
        self.overwrite = cfg.get("overwrite", self.overwrite)
        return self

    def to_disk(self, path, *, exclude=tuple()):
        """Serialize the sentencizer to disk.

        DOCS: https://spacy.io/api/sentencizer#to_disk
        """
        path = util.ensure_path(path)
        path = path.with_suffix(".json")
        srsly.write_json(path, {"punct_chars": list(self.punct_chars), "overwrite": self.overwrite})

    def from_disk(self, path, *, exclude=tuple()):
        """Load the sentencizer from disk.

        DOCS: https://spacy.io/api/sentencizer#from_disk
        """
        path = util.ensure_path(path)
        path = path.with_suffix(".json")
        cfg = srsly.read_json(path)
        self.punct_chars = set(cfg.get("punct_chars", self.default_punct_chars))
        self.overwrite = cfg.get("overwrite", self.overwrite)
        return self


# Setup backwards compatibility hook for factories
def __getattr__(name):
    if name == "make_sentencizer":
        module = importlib.import_module("spacy.pipeline.factories")
        return module.make_sentencizer
    raise AttributeError(f"module {__name__} has no attribute {name}")
