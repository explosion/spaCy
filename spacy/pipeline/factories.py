from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

from thinc.api import Model
from thinc.types import Floats2d, Ragged

from ..kb import Candidate, KnowledgeBase
from ..language import Language
from ..pipeline._parser_internals.transition_system import TransitionSystem
from ..pipeline.attributeruler import AttributeRuler
from ..pipeline.dep_parser import DEFAULT_PARSER_MODEL, DependencyParser
from ..pipeline.edit_tree_lemmatizer import (
    DEFAULT_EDIT_TREE_LEMMATIZER_MODEL,
    EditTreeLemmatizer,
)

# Import factory default configurations
from ..pipeline.entity_linker import DEFAULT_NEL_MODEL, EntityLinker, EntityLinker_v1
from ..pipeline.entityruler import DEFAULT_ENT_ID_SEP, EntityRuler
from ..pipeline.functions import DocCleaner, TokenSplitter
from ..pipeline.lemmatizer import Lemmatizer
from ..pipeline.morphologizer import DEFAULT_MORPH_MODEL, Morphologizer
from ..pipeline.multitask import DEFAULT_MT_MODEL, MultitaskObjective
from ..pipeline.ner import DEFAULT_NER_MODEL, EntityRecognizer
from ..pipeline.sentencizer import Sentencizer
from ..pipeline.senter import DEFAULT_SENTER_MODEL, SentenceRecognizer
from ..pipeline.span_finder import DEFAULT_SPAN_FINDER_MODEL, SpanFinder
from ..pipeline.span_ruler import DEFAULT_SPANS_KEY as SPAN_RULER_DEFAULT_SPANS_KEY
from ..pipeline.span_ruler import (
    SpanRuler,
    prioritize_existing_ents_filter,
    prioritize_new_ents_filter,
)
from ..pipeline.spancat import (
    DEFAULT_SPANCAT_MODEL,
    DEFAULT_SPANCAT_SINGLELABEL_MODEL,
    DEFAULT_SPANS_KEY,
    SpanCategorizer,
    Suggester,
)
from ..pipeline.tagger import DEFAULT_TAGGER_MODEL, Tagger
from ..pipeline.textcat import DEFAULT_SINGLE_TEXTCAT_MODEL, TextCategorizer
from ..pipeline.textcat_multilabel import (
    DEFAULT_MULTI_TEXTCAT_MODEL,
    MultiLabel_TextCategorizer,
)
from ..pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL, Tok2Vec
from ..tokens.doc import Doc
from ..tokens.span import Span
from ..vocab import Vocab

# Global flag to track if factories have been registered
FACTORIES_REGISTERED = False


def register_factories() -> None:
    """Register all factories with the registry.

    This function registers all pipeline component factories, centralizing
    the registrations that were previously done with @Language.factory decorators.
    """
    global FACTORIES_REGISTERED

    if FACTORIES_REGISTERED:
        return

    # Register factories using the same pattern as Language.factory decorator
    # We use Language.factory()() pattern which exactly mimics the decorator

    # attributeruler
    Language.factory(
        "attribute_ruler",
        default_config={
            "validate": False,
            "scorer": {"@scorers": "spacy.attribute_ruler_scorer.v1"},
        },
    )(make_attribute_ruler)

    # entity_linker
    Language.factory(
        "entity_linker",
        requires=["doc.ents", "doc.sents", "token.ent_iob", "token.ent_type"],
        assigns=["token.ent_kb_id"],
        default_config={
            "model": DEFAULT_NEL_MODEL,
            "labels_discard": [],
            "n_sents": 0,
            "incl_prior": True,
            "incl_context": True,
            "entity_vector_length": 64,
            "get_candidates": {"@misc": "spacy.CandidateGenerator.v1"},
            "get_candidates_batch": {"@misc": "spacy.CandidateBatchGenerator.v1"},
            "generate_empty_kb": {"@misc": "spacy.EmptyKB.v2"},
            "overwrite": True,
            "scorer": {"@scorers": "spacy.entity_linker_scorer.v1"},
            "use_gold_ents": True,
            "candidates_batch_size": 1,
            "threshold": None,
        },
        default_score_weights={
            "nel_micro_f": 1.0,
            "nel_micro_r": None,
            "nel_micro_p": None,
        },
    )(make_entity_linker)

    # entity_ruler
    Language.factory(
        "entity_ruler",
        assigns=["doc.ents", "token.ent_type", "token.ent_iob"],
        default_config={
            "phrase_matcher_attr": None,
            "matcher_fuzzy_compare": {"@misc": "spacy.levenshtein_compare.v1"},
            "validate": False,
            "overwrite_ents": False,
            "ent_id_sep": DEFAULT_ENT_ID_SEP,
            "scorer": {"@scorers": "spacy.entity_ruler_scorer.v1"},
        },
        default_score_weights={
            "ents_f": 1.0,
            "ents_p": 0.0,
            "ents_r": 0.0,
            "ents_per_type": None,
        },
    )(make_entity_ruler)

    # lemmatizer
    Language.factory(
        "lemmatizer",
        assigns=["token.lemma"],
        default_config={
            "model": None,
            "mode": "lookup",
            "overwrite": False,
            "scorer": {"@scorers": "spacy.lemmatizer_scorer.v1"},
        },
        default_score_weights={"lemma_acc": 1.0},
    )(make_lemmatizer)

    # textcat
    Language.factory(
        "textcat",
        assigns=["doc.cats"],
        default_config={
            "threshold": 0.0,
            "model": DEFAULT_SINGLE_TEXTCAT_MODEL,
            "scorer": {"@scorers": "spacy.textcat_scorer.v2"},
        },
        default_score_weights={
            "cats_score": 1.0,
            "cats_score_desc": None,
            "cats_micro_p": None,
            "cats_micro_r": None,
            "cats_micro_f": None,
            "cats_macro_p": None,
            "cats_macro_r": None,
            "cats_macro_f": None,
            "cats_macro_auc": None,
            "cats_f_per_type": None,
        },
    )(make_textcat)

    # token_splitter
    Language.factory(
        "token_splitter",
        default_config={"min_length": 25, "split_length": 10},
        retokenizes=True,
    )(make_token_splitter)

    # doc_cleaner
    Language.factory(
        "doc_cleaner",
        default_config={"attrs": {"tensor": None, "_.trf_data": None}, "silent": True},
    )(make_doc_cleaner)

    # tok2vec
    Language.factory(
        "tok2vec",
        assigns=["doc.tensor"],
        default_config={"model": DEFAULT_TOK2VEC_MODEL},
    )(make_tok2vec)

    # senter
    Language.factory(
        "senter",
        assigns=["token.is_sent_start"],
        default_config={
            "model": DEFAULT_SENTER_MODEL,
            "overwrite": False,
            "scorer": {"@scorers": "spacy.senter_scorer.v1"},
        },
        default_score_weights={"sents_f": 1.0, "sents_p": 0.0, "sents_r": 0.0},
    )(make_senter)

    # morphologizer
    Language.factory(
        "morphologizer",
        assigns=["token.morph", "token.pos"],
        default_config={
            "model": DEFAULT_MORPH_MODEL,
            "overwrite": True,
            "extend": False,
            "scorer": {"@scorers": "spacy.morphologizer_scorer.v1"},
            "label_smoothing": 0.0,
        },
        default_score_weights={
            "pos_acc": 0.5,
            "morph_acc": 0.5,
            "morph_per_feat": None,
        },
    )(make_morphologizer)

    # spancat
    Language.factory(
        "spancat",
        assigns=["doc.spans"],
        default_config={
            "threshold": 0.5,
            "spans_key": DEFAULT_SPANS_KEY,
            "max_positive": None,
            "model": DEFAULT_SPANCAT_MODEL,
            "suggester": {"@misc": "spacy.ngram_suggester.v1", "sizes": [1, 2, 3]},
            "scorer": {"@scorers": "spacy.spancat_scorer.v1"},
        },
        default_score_weights={"spans_sc_f": 1.0, "spans_sc_p": 0.0, "spans_sc_r": 0.0},
    )(make_spancat)

    # spancat_singlelabel
    Language.factory(
        "spancat_singlelabel",
        assigns=["doc.spans"],
        default_config={
            "spans_key": DEFAULT_SPANS_KEY,
            "model": DEFAULT_SPANCAT_SINGLELABEL_MODEL,
            "negative_weight": 1.0,
            "suggester": {"@misc": "spacy.ngram_suggester.v1", "sizes": [1, 2, 3]},
            "scorer": {"@scorers": "spacy.spancat_scorer.v1"},
            "allow_overlap": True,
        },
        default_score_weights={"spans_sc_f": 1.0, "spans_sc_p": 0.0, "spans_sc_r": 0.0},
    )(make_spancat_singlelabel)

    # future_entity_ruler
    Language.factory(
        "future_entity_ruler",
        assigns=["doc.ents"],
        default_config={
            "phrase_matcher_attr": None,
            "validate": False,
            "overwrite_ents": False,
            "scorer": {"@scorers": "spacy.entity_ruler_scorer.v1"},
            "ent_id_sep": "__unused__",
            "matcher_fuzzy_compare": {"@misc": "spacy.levenshtein_compare.v1"},
        },
        default_score_weights={
            "ents_f": 1.0,
            "ents_p": 0.0,
            "ents_r": 0.0,
            "ents_per_type": None,
        },
    )(make_future_entity_ruler)

    # span_ruler
    Language.factory(
        "span_ruler",
        assigns=["doc.spans"],
        default_config={
            "spans_key": SPAN_RULER_DEFAULT_SPANS_KEY,
            "spans_filter": None,
            "annotate_ents": False,
            "ents_filter": {"@misc": "spacy.first_longest_spans_filter.v1"},
            "phrase_matcher_attr": None,
            "matcher_fuzzy_compare": {"@misc": "spacy.levenshtein_compare.v1"},
            "validate": False,
            "overwrite": True,
            "scorer": {
                "@scorers": "spacy.overlapping_labeled_spans_scorer.v1",
                "spans_key": SPAN_RULER_DEFAULT_SPANS_KEY,
            },
        },
        default_score_weights={
            f"spans_{SPAN_RULER_DEFAULT_SPANS_KEY}_f": 1.0,
            f"spans_{SPAN_RULER_DEFAULT_SPANS_KEY}_p": 0.0,
            f"spans_{SPAN_RULER_DEFAULT_SPANS_KEY}_r": 0.0,
            f"spans_{SPAN_RULER_DEFAULT_SPANS_KEY}_per_type": None,
        },
    )(make_span_ruler)

    # trainable_lemmatizer
    Language.factory(
        "trainable_lemmatizer",
        assigns=["token.lemma"],
        requires=[],
        default_config={
            "model": DEFAULT_EDIT_TREE_LEMMATIZER_MODEL,
            "backoff": "orth",
            "min_tree_freq": 3,
            "overwrite": False,
            "top_k": 1,
            "scorer": {"@scorers": "spacy.lemmatizer_scorer.v1"},
        },
        default_score_weights={"lemma_acc": 1.0},
    )(make_edit_tree_lemmatizer)

    # textcat_multilabel
    Language.factory(
        "textcat_multilabel",
        assigns=["doc.cats"],
        default_config={
            "threshold": 0.5,
            "model": DEFAULT_MULTI_TEXTCAT_MODEL,
            "scorer": {"@scorers": "spacy.textcat_multilabel_scorer.v2"},
        },
        default_score_weights={
            "cats_score": 1.0,
            "cats_score_desc": None,
            "cats_micro_p": None,
            "cats_micro_r": None,
            "cats_micro_f": None,
            "cats_macro_p": None,
            "cats_macro_r": None,
            "cats_macro_f": None,
            "cats_macro_auc": None,
            "cats_f_per_type": None,
        },
    )(make_multilabel_textcat)

    # span_finder
    Language.factory(
        "span_finder",
        assigns=["doc.spans"],
        default_config={
            "threshold": 0.5,
            "model": DEFAULT_SPAN_FINDER_MODEL,
            "spans_key": DEFAULT_SPANS_KEY,
            "max_length": 25,
            "min_length": None,
            "scorer": {"@scorers": "spacy.span_finder_scorer.v1"},
        },
        default_score_weights={
            f"spans_{DEFAULT_SPANS_KEY}_f": 1.0,
            f"spans_{DEFAULT_SPANS_KEY}_p": 0.0,
            f"spans_{DEFAULT_SPANS_KEY}_r": 0.0,
        },
    )(make_span_finder)

    # ner
    Language.factory(
        "ner",
        assigns=["doc.ents", "token.ent_iob", "token.ent_type"],
        default_config={
            "moves": None,
            "update_with_oracle_cut_size": 100,
            "model": DEFAULT_NER_MODEL,
            "incorrect_spans_key": None,
            "scorer": {"@scorers": "spacy.ner_scorer.v1"},
        },
        default_score_weights={
            "ents_f": 1.0,
            "ents_p": 0.0,
            "ents_r": 0.0,
            "ents_per_type": None,
        },
    )(make_ner)

    # beam_ner
    Language.factory(
        "beam_ner",
        assigns=["doc.ents", "token.ent_iob", "token.ent_type"],
        default_config={
            "moves": None,
            "update_with_oracle_cut_size": 100,
            "model": DEFAULT_NER_MODEL,
            "beam_density": 0.01,
            "beam_update_prob": 0.5,
            "beam_width": 32,
            "incorrect_spans_key": None,
            "scorer": {"@scorers": "spacy.ner_scorer.v1"},
        },
        default_score_weights={
            "ents_f": 1.0,
            "ents_p": 0.0,
            "ents_r": 0.0,
            "ents_per_type": None,
        },
    )(make_beam_ner)

    # parser
    Language.factory(
        "parser",
        assigns=["token.dep", "token.head", "token.is_sent_start", "doc.sents"],
        default_config={
            "moves": None,
            "update_with_oracle_cut_size": 100,
            "learn_tokens": False,
            "min_action_freq": 30,
            "model": DEFAULT_PARSER_MODEL,
            "scorer": {"@scorers": "spacy.parser_scorer.v1"},
        },
        default_score_weights={
            "dep_uas": 0.5,
            "dep_las": 0.5,
            "dep_las_per_type": None,
            "sents_p": None,
            "sents_r": None,
            "sents_f": 0.0,
        },
    )(make_parser)

    # beam_parser
    Language.factory(
        "beam_parser",
        assigns=["token.dep", "token.head", "token.is_sent_start", "doc.sents"],
        default_config={
            "moves": None,
            "update_with_oracle_cut_size": 100,
            "learn_tokens": False,
            "min_action_freq": 30,
            "beam_width": 8,
            "beam_density": 0.0001,
            "beam_update_prob": 0.5,
            "model": DEFAULT_PARSER_MODEL,
            "scorer": {"@scorers": "spacy.parser_scorer.v1"},
        },
        default_score_weights={
            "dep_uas": 0.5,
            "dep_las": 0.5,
            "dep_las_per_type": None,
            "sents_p": None,
            "sents_r": None,
            "sents_f": 0.0,
        },
    )(make_beam_parser)

    # tagger
    Language.factory(
        "tagger",
        assigns=["token.tag"],
        default_config={
            "model": DEFAULT_TAGGER_MODEL,
            "overwrite": False,
            "scorer": {"@scorers": "spacy.tagger_scorer.v1"},
            "neg_prefix": "!",
            "label_smoothing": 0.0,
        },
        default_score_weights={
            "tag_acc": 1.0,
            "pos_acc": 0.0,
            "tag_micro_p": None,
            "tag_micro_r": None,
            "tag_micro_f": None,
        },
    )(make_tagger)

    # nn_labeller
    Language.factory(
        "nn_labeller",
        default_config={
            "labels": None,
            "target": "dep_tag_offset",
            "model": DEFAULT_MT_MODEL,
        },
    )(make_nn_labeller)

    # sentencizer
    Language.factory(
        "sentencizer",
        assigns=["token.is_sent_start", "doc.sents"],
        default_config={
            "punct_chars": None,
            "overwrite": False,
            "scorer": {"@scorers": "spacy.senter_scorer.v1"},
        },
        default_score_weights={"sents_f": 1.0, "sents_p": 0.0, "sents_r": 0.0},
    )(make_sentencizer)

    # Set the flag to indicate that all factories have been registered
    FACTORIES_REGISTERED = True


# We can't have function implementations for these factories in Cython, because
# we need to build a Pydantic model for them dynamically, reading their argument
# structure from the signature. In Cython 3, this doesn't work because the
# from __future__ import annotations semantics are used, which means the types
# are stored as strings.
def make_sentencizer(
    nlp: Language,
    name: str,
    punct_chars: Optional[List[str]],
    overwrite: bool,
    scorer: Optional[Callable],
):
    return Sentencizer(
        name, punct_chars=punct_chars, overwrite=overwrite, scorer=scorer
    )


def make_attribute_ruler(
    nlp: Language, name: str, validate: bool, scorer: Optional[Callable]
):
    return AttributeRuler(nlp.vocab, name, validate=validate, scorer=scorer)


def make_entity_linker(
    nlp: Language,
    name: str,
    model: Model,
    *,
    labels_discard: Iterable[str],
    n_sents: int,
    incl_prior: bool,
    incl_context: bool,
    entity_vector_length: int,
    get_candidates: Callable[[KnowledgeBase, Span], Iterable[Candidate]],
    get_candidates_batch: Callable[
        [KnowledgeBase, Iterable[Span]], Iterable[Iterable[Candidate]]
    ],
    generate_empty_kb: Callable[[Vocab, int], KnowledgeBase],
    overwrite: bool,
    scorer: Optional[Callable],
    use_gold_ents: bool,
    candidates_batch_size: int,
    threshold: Optional[float] = None,
):

    if not model.attrs.get("include_span_maker", False):
        # The only difference in arguments here is that use_gold_ents and threshold aren't available.
        return EntityLinker_v1(
            nlp.vocab,
            model,
            name,
            labels_discard=labels_discard,
            n_sents=n_sents,
            incl_prior=incl_prior,
            incl_context=incl_context,
            entity_vector_length=entity_vector_length,
            get_candidates=get_candidates,
            overwrite=overwrite,
            scorer=scorer,
        )
    return EntityLinker(
        nlp.vocab,
        model,
        name,
        labels_discard=labels_discard,
        n_sents=n_sents,
        incl_prior=incl_prior,
        incl_context=incl_context,
        entity_vector_length=entity_vector_length,
        get_candidates=get_candidates,
        get_candidates_batch=get_candidates_batch,
        generate_empty_kb=generate_empty_kb,
        overwrite=overwrite,
        scorer=scorer,
        use_gold_ents=use_gold_ents,
        candidates_batch_size=candidates_batch_size,
        threshold=threshold,
    )


def make_lemmatizer(
    nlp: Language,
    model: Optional[Model],
    name: str,
    mode: str,
    overwrite: bool,
    scorer: Optional[Callable],
):
    return Lemmatizer(
        nlp.vocab, model, name, mode=mode, overwrite=overwrite, scorer=scorer
    )


def make_textcat(
    nlp: Language,
    name: str,
    model: Model[List[Doc], List[Floats2d]],
    threshold: float,
    scorer: Optional[Callable],
) -> TextCategorizer:
    return TextCategorizer(nlp.vocab, model, name, threshold=threshold, scorer=scorer)


def make_token_splitter(
    nlp: Language, name: str, *, min_length: int = 0, split_length: int = 0
):
    return TokenSplitter(min_length=min_length, split_length=split_length)


def make_doc_cleaner(nlp: Language, name: str, *, attrs: Dict[str, Any], silent: bool):
    return DocCleaner(attrs, silent=silent)


def make_tok2vec(nlp: Language, name: str, model: Model) -> Tok2Vec:
    return Tok2Vec(nlp.vocab, model, name)


def make_spancat(
    nlp: Language,
    name: str,
    suggester: Suggester,
    model: Model[Tuple[List[Doc], Ragged], Floats2d],
    spans_key: str,
    scorer: Optional[Callable],
    threshold: float,
    max_positive: Optional[int],
) -> SpanCategorizer:
    return SpanCategorizer(
        nlp.vocab,
        model=model,
        suggester=suggester,
        name=name,
        spans_key=spans_key,
        negative_weight=None,
        allow_overlap=True,
        max_positive=max_positive,
        threshold=threshold,
        scorer=scorer,
        add_negative_label=False,
    )


def make_spancat_singlelabel(
    nlp: Language,
    name: str,
    suggester: Suggester,
    model: Model[Tuple[List[Doc], Ragged], Floats2d],
    spans_key: str,
    negative_weight: float,
    allow_overlap: bool,
    scorer: Optional[Callable],
) -> SpanCategorizer:
    return SpanCategorizer(
        nlp.vocab,
        model=model,
        suggester=suggester,
        name=name,
        spans_key=spans_key,
        negative_weight=negative_weight,
        allow_overlap=allow_overlap,
        max_positive=1,
        add_negative_label=True,
        threshold=None,
        scorer=scorer,
    )


def make_future_entity_ruler(
    nlp: Language,
    name: str,
    phrase_matcher_attr: Optional[Union[int, str]],
    matcher_fuzzy_compare: Callable,
    validate: bool,
    overwrite_ents: bool,
    scorer: Optional[Callable],
    ent_id_sep: str,
):
    if overwrite_ents:
        ents_filter = prioritize_new_ents_filter
    else:
        ents_filter = prioritize_existing_ents_filter
    return SpanRuler(
        nlp,
        name,
        spans_key=None,
        spans_filter=None,
        annotate_ents=True,
        ents_filter=ents_filter,
        phrase_matcher_attr=phrase_matcher_attr,
        matcher_fuzzy_compare=matcher_fuzzy_compare,
        validate=validate,
        overwrite=False,
        scorer=scorer,
    )


def make_entity_ruler(
    nlp: Language,
    name: str,
    phrase_matcher_attr: Optional[Union[int, str]],
    matcher_fuzzy_compare: Callable,
    validate: bool,
    overwrite_ents: bool,
    ent_id_sep: str,
    scorer: Optional[Callable],
):
    return EntityRuler(
        nlp,
        name,
        phrase_matcher_attr=phrase_matcher_attr,
        matcher_fuzzy_compare=matcher_fuzzy_compare,
        validate=validate,
        overwrite_ents=overwrite_ents,
        ent_id_sep=ent_id_sep,
        scorer=scorer,
    )


def make_span_ruler(
    nlp: Language,
    name: str,
    spans_key: Optional[str],
    spans_filter: Optional[Callable[[Iterable[Span], Iterable[Span]], Iterable[Span]]],
    annotate_ents: bool,
    ents_filter: Callable[[Iterable[Span], Iterable[Span]], Iterable[Span]],
    phrase_matcher_attr: Optional[Union[int, str]],
    matcher_fuzzy_compare: Callable,
    validate: bool,
    overwrite: bool,
    scorer: Optional[Callable],
):
    return SpanRuler(
        nlp,
        name,
        spans_key=spans_key,
        spans_filter=spans_filter,
        annotate_ents=annotate_ents,
        ents_filter=ents_filter,
        phrase_matcher_attr=phrase_matcher_attr,
        matcher_fuzzy_compare=matcher_fuzzy_compare,
        validate=validate,
        overwrite=overwrite,
        scorer=scorer,
    )


def make_edit_tree_lemmatizer(
    nlp: Language,
    name: str,
    model: Model,
    backoff: Optional[str],
    min_tree_freq: int,
    overwrite: bool,
    top_k: int,
    scorer: Optional[Callable],
):
    return EditTreeLemmatizer(
        nlp.vocab,
        model,
        name,
        backoff=backoff,
        min_tree_freq=min_tree_freq,
        overwrite=overwrite,
        top_k=top_k,
        scorer=scorer,
    )


def make_multilabel_textcat(
    nlp: Language,
    name: str,
    model: Model[List[Doc], List[Floats2d]],
    threshold: float,
    scorer: Optional[Callable],
) -> MultiLabel_TextCategorizer:
    return MultiLabel_TextCategorizer(
        nlp.vocab, model, name, threshold=threshold, scorer=scorer
    )


def make_span_finder(
    nlp: Language,
    name: str,
    model: Model[Iterable[Doc], Floats2d],
    spans_key: str,
    threshold: float,
    max_length: Optional[int],
    min_length: Optional[int],
    scorer: Optional[Callable],
) -> SpanFinder:
    return SpanFinder(
        nlp,
        model=model,
        threshold=threshold,
        name=name,
        scorer=scorer,
        max_length=max_length,
        min_length=min_length,
        spans_key=spans_key,
    )


def make_ner(
    nlp: Language,
    name: str,
    model: Model,
    moves: Optional[TransitionSystem],
    update_with_oracle_cut_size: int,
    incorrect_spans_key: Optional[str],
    scorer: Optional[Callable],
):
    return EntityRecognizer(
        nlp.vocab,
        model,
        name=name,
        moves=moves,
        update_with_oracle_cut_size=update_with_oracle_cut_size,
        incorrect_spans_key=incorrect_spans_key,
        scorer=scorer,
    )


def make_beam_ner(
    nlp: Language,
    name: str,
    model: Model,
    moves: Optional[TransitionSystem],
    update_with_oracle_cut_size: int,
    beam_width: int,
    beam_density: float,
    beam_update_prob: float,
    incorrect_spans_key: Optional[str],
    scorer: Optional[Callable],
):
    return EntityRecognizer(
        nlp.vocab,
        model,
        name=name,
        moves=moves,
        update_with_oracle_cut_size=update_with_oracle_cut_size,
        beam_width=beam_width,
        beam_density=beam_density,
        beam_update_prob=beam_update_prob,
        incorrect_spans_key=incorrect_spans_key,
        scorer=scorer,
    )


def make_parser(
    nlp: Language,
    name: str,
    model: Model,
    moves: Optional[TransitionSystem],
    update_with_oracle_cut_size: int,
    learn_tokens: bool,
    min_action_freq: int,
    scorer: Optional[Callable],
):
    return DependencyParser(
        nlp.vocab,
        model,
        name=name,
        moves=moves,
        update_with_oracle_cut_size=update_with_oracle_cut_size,
        learn_tokens=learn_tokens,
        min_action_freq=min_action_freq,
        scorer=scorer,
    )


def make_beam_parser(
    nlp: Language,
    name: str,
    model: Model,
    moves: Optional[TransitionSystem],
    update_with_oracle_cut_size: int,
    learn_tokens: bool,
    min_action_freq: int,
    beam_width: int,
    beam_density: float,
    beam_update_prob: float,
    scorer: Optional[Callable],
):
    return DependencyParser(
        nlp.vocab,
        model,
        name=name,
        moves=moves,
        update_with_oracle_cut_size=update_with_oracle_cut_size,
        learn_tokens=learn_tokens,
        min_action_freq=min_action_freq,
        beam_width=beam_width,
        beam_density=beam_density,
        beam_update_prob=beam_update_prob,
        scorer=scorer,
    )


def make_tagger(
    nlp: Language,
    name: str,
    model: Model,
    overwrite: bool,
    scorer: Optional[Callable],
    neg_prefix: str,
    label_smoothing: float,
):
    return Tagger(
        nlp.vocab,
        model,
        name=name,
        overwrite=overwrite,
        scorer=scorer,
        neg_prefix=neg_prefix,
        label_smoothing=label_smoothing,
    )


def make_nn_labeller(
    nlp: Language, name: str, model: Model, labels: Optional[dict], target: str
):
    return MultitaskObjective(nlp.vocab, model, name, target=target)


def make_morphologizer(
    nlp: Language,
    model: Model,
    name: str,
    overwrite: bool,
    extend: bool,
    label_smoothing: float,
    scorer: Optional[Callable],
):
    return Morphologizer(
        nlp.vocab,
        model,
        name,
        overwrite=overwrite,
        extend=extend,
        label_smoothing=label_smoothing,
        scorer=scorer,
    )


def make_senter(
    nlp: Language, name: str, model: Model, overwrite: bool, scorer: Optional[Callable]
):
    return SentenceRecognizer(
        nlp.vocab, model, name, overwrite=overwrite, scorer=scorer
    )
