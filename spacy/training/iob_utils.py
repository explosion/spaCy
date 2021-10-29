from typing import List, Dict, Tuple, Iterable, Union, Iterator
import warnings

from ..errors import Errors, Warnings
from ..tokens import Span, Doc


def iob_to_biluo(tags: Iterable[str]) -> List[str]:
    out: List[str] = []
    tags = list(tags)
    while tags:
        out.extend(_consume_os(tags))
        out.extend(_consume_ent(tags))
    return out


def biluo_to_iob(tags: Iterable[str]) -> List[str]:
    out = []
    for tag in tags:
        if tag is None:
            out.append(tag)
        else:
            tag = tag.replace("U-", "B-", 1).replace("L-", "I-", 1)
            out.append(tag)
    return out


def _consume_os(tags: List[str]) -> Iterator[str]:
    while tags and tags[0] == "O":
        yield tags.pop(0)


def _consume_ent(tags: List[str]) -> List[str]:
    if not tags:
        return []
    tag = tags.pop(0)
    target_in = "I" + tag[1:]
    target_last = "L" + tag[1:]
    length = 1
    while tags and tags[0] in {target_in, target_last}:
        length += 1
        tags.pop(0)
    label = tag[2:]
    if length == 1:
        if len(label) == 0:
            raise ValueError(Errors.E177.format(tag=tag))
        return ["U-" + label]
    else:
        start = "B-" + label
        end = "L-" + label
        middle = [f"I-{label}" for _ in range(1, length - 1)]
        return [start] + middle + [end]


def doc_to_biluo_tags(doc: Doc, missing: str = "O"):
    return offsets_to_biluo_tags(
        doc,
        [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents],
        missing=missing,
    )


def offsets_to_biluo_tags(
    doc: Doc, entities: Iterable[Tuple[int, int, Union[str, int]]], missing: str = "O"
) -> List[str]:
    """Encode labelled spans into per-token tags, using the
    Begin/In/Last/Unit/Out scheme (BILUO).

    doc (Doc): The document that the entity offsets refer to. The output tags
        will refer to the token boundaries within the document.
    entities (iterable): A sequence of `(start, end, label)` triples. `start`
        and `end` should be character-offset integers denoting the slice into
        the original string.
    missing (str): The label used for missing values, e.g. if tokenization
        doesn’t align with the entity offsets. Defaults to "O".
    RETURNS (list): A list of unicode strings, describing the tags. Each tag
        string will be of the form either "", "O" or "{action}-{label}", where
        action is one of "B", "I", "L", "U". The missing label is used where the
        entity offsets don't align with the tokenization in the `Doc` object.
        The training algorithm will view these as missing values. "O" denotes a
        non-entity token. "B" denotes the beginning of a multi-token entity,
        "I" the inside of an entity of three or more tokens, and "L" the end
        of an entity of two or more tokens. "U" denotes a single-token entity.

    EXAMPLE:
        >>> text = 'I like London.'
        >>> entities = [(len('I like '), len('I like London'), 'LOC')]
        >>> doc = nlp.tokenizer(text)
        >>> tags = offsets_to_biluo_tags(doc, entities)
        >>> assert tags == ["O", "O", 'U-LOC', "O"]
    """
    # Ensure no overlapping entity labels exist
    tokens_in_ents: Dict[int, Tuple[int, int, Union[str, int]]] = {}
    starts = {token.idx: token.i for token in doc}
    ends = {token.idx + len(token): token.i for token in doc}
    biluo = ["-" for _ in doc]
    # Handle entity cases
    for start_char, end_char, label in entities:
        if not label:
            for s in starts:  # account for many-to-one
                if s >= start_char and s < end_char:
                    biluo[starts[s]] = "O"
        else:
            for token_index in range(start_char, end_char):
                if token_index in tokens_in_ents.keys():
                    raise ValueError(
                        Errors.E103.format(
                            span1=(
                                tokens_in_ents[token_index][0],
                                tokens_in_ents[token_index][1],
                                tokens_in_ents[token_index][2],
                            ),
                            span2=(start_char, end_char, label),
                        )
                    )
                tokens_in_ents[token_index] = (start_char, end_char, label)
            start_token = starts.get(start_char)
            end_token = ends.get(end_char)
            # Only interested if the tokenization is correct
            if start_token is not None and end_token is not None:
                if start_token == end_token:
                    biluo[start_token] = f"U-{label}"
                else:
                    biluo[start_token] = f"B-{label}"
                    for i in range(start_token + 1, end_token):
                        biluo[i] = f"I-{label}"
                    biluo[end_token] = f"L-{label}"
    # Now distinguish the O cases from ones where we miss the tokenization
    entity_chars = set()
    for start_char, end_char, label in entities:
        for i in range(start_char, end_char):
            entity_chars.add(i)
    for token in doc:
        for i in range(token.idx, token.idx + len(token)):
            if i in entity_chars:
                break
        else:
            biluo[token.i] = missing
    if "-" in biluo and missing != "-":
        ent_str = str(entities)
        warnings.warn(
            Warnings.W030.format(
                text=doc.text[:50] + "..." if len(doc.text) > 50 else doc.text,
                entities=ent_str[:50] + "..." if len(ent_str) > 50 else ent_str,
            )
        )
    return biluo


def biluo_tags_to_spans(doc: Doc, tags: Iterable[str]) -> List[Span]:
    """Encode per-token tags following the BILUO scheme into Span object, e.g.
    to overwrite the doc.ents.

    doc (Doc): The document that the BILUO tags refer to.
    tags (iterable): A sequence of BILUO tags with each tag describing one
        token. Each tag string will be of the form of either "", "O" or
        "{action}-{label}", where action is one of "B", "I", "L", "U".
    RETURNS (list): A sequence of Span objects. Each token with a missing IOB
        tag is returned as a Span with an empty label.
    """
    token_offsets = tags_to_entities(tags)
    spans = []
    for label, start_idx, end_idx in token_offsets:
        span = Span(doc, start_idx, end_idx + 1, label=label)
        spans.append(span)
    return spans


def biluo_tags_to_offsets(
    doc: Doc, tags: Iterable[str]
) -> List[Tuple[int, int, Union[str, int]]]:
    """Encode per-token tags following the BILUO scheme into entity offsets.

    doc (Doc): The document that the BILUO tags refer to.
    tags (iterable): A sequence of BILUO tags with each tag describing one
        token. Each tags string will be of the form of either "", "O" or
        "{action}-{label}", where action is one of "B", "I", "L", "U".
    RETURNS (list): A sequence of `(start, end, label)` triples. `start` and
        `end` will be character-offset integers denoting the slice into the
        original string.
    """
    spans = biluo_tags_to_spans(doc, tags)
    return [(span.start_char, span.end_char, span.label_) for span in spans]


def tags_to_entities(tags: Iterable[str]) -> List[Tuple[str, int, int]]:
    """Note that the end index returned by this function is inclusive.
    To use it for Span creation, increment the end by 1."""
    entities = []
    start = None
    for i, tag in enumerate(tags):
        if tag is None or tag.startswith("-"):
            # TODO: We shouldn't be getting these malformed inputs. Fix this.
            if start is not None:
                start = None
            else:
                entities.append(("", i, i))
        elif tag.startswith("O"):
            pass
        elif tag.startswith("I"):
            if start is None:
                raise ValueError(
                    Errors.E067.format(start="I", tags=list(tags)[: i + 1])
                )
        elif tag.startswith("U"):
            entities.append((tag[2:], i, i))
        elif tag.startswith("B"):
            start = i
        elif tag.startswith("L"):
            if start is None:
                raise ValueError(
                    Errors.E067.format(start="L", tags=list(tags)[: i + 1])
                )
            entities.append((tag[2:], start, i))
            start = None
        else:
            raise ValueError(Errors.E068.format(tag=tag))
    return entities


# Fallbacks to make backwards-compat easier
offsets_from_biluo_tags = biluo_tags_to_offsets
spans_from_biluo_tags = biluo_tags_to_spans
biluo_tags_from_offsets = offsets_to_biluo_tags
