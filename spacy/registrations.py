"""Centralized registry population for spaCy components.

This module centralizes registry decorations to prevent circular import issues
with Cython annotation changes from __future__ import annotations. Functions
remain in their original locations, but decoration is moved here.
"""
from typing import Dict, Any, Callable, Iterable, List, Optional, Union

# Global flag to track if registry has been populated
REGISTRY_POPULATED = False

# Global flag to track if factories have been registered
FACTORIES_REGISTERED = False

def populate_registry() -> None:
    """Populate the registry with all necessary components.
    
    This function should be called before accessing the registry, to ensure 
    it's populated. The function uses a global flag to prevent repopulation.
    """
    global REGISTRY_POPULATED
    if REGISTRY_POPULATED:
        return
    
    # Import all necessary modules
    from .util import registry, make_first_longest_spans_filter
    
    # Import all pipeline components that were using registry decorators
    from .pipeline.tagger import make_tagger_scorer
    from .pipeline.ner import make_ner_scorer
    from .pipeline.lemmatizer import make_lemmatizer_scorer
    from .pipeline.span_finder import make_span_finder_scorer
    from .pipeline.spancat import make_spancat_scorer, build_ngram_suggester, build_ngram_range_suggester, build_preset_spans_suggester
    from .pipeline.entityruler import make_entity_ruler_scorer as make_entityruler_scorer
    from .pipeline.sentencizer import senter_score as make_sentencizer_scorer
    from .pipeline.senter import make_senter_scorer
    from .pipeline.textcat import make_textcat_scorer
    from .pipeline.textcat_multilabel import make_textcat_multilabel_scorer
    
    # Register miscellaneous components 
    registry.misc("spacy.first_longest_spans_filter.v1")(make_first_longest_spans_filter)
    registry.misc("spacy.ngram_suggester.v1")(build_ngram_suggester)
    registry.misc("spacy.ngram_range_suggester.v1")(build_ngram_range_suggester)
    registry.misc("spacy.preset_spans_suggester.v1")(build_preset_spans_suggester)
    
    # Need to get references to the existing functions in registry by importing the function that is there
    # For the registry that was previously decorated
    
    # Import ML components that use registry
    from .ml.models.tok2vec import tok2vec_listener_v1, build_hash_embed_cnn_tok2vec, build_Tok2Vec_model, MultiHashEmbed, CharacterEmbed, MaxoutWindowEncoder, MishWindowEncoder, BiLSTMEncoder
    
    # Register scorers
    registry.scorers("spacy.tagger_scorer.v1")(make_tagger_scorer)
    registry.scorers("spacy.ner_scorer.v1")(make_ner_scorer)
    # span_ruler_scorer removed as it's not in span_ruler.py
    registry.scorers("spacy.entity_ruler_scorer.v1")(make_entityruler_scorer)
    registry.scorers("spacy.sentencizer_scorer.v1")(make_sentencizer_scorer)
    registry.scorers("spacy.senter_scorer.v1")(make_senter_scorer)
    registry.scorers("spacy.textcat_scorer.v1")(make_textcat_scorer)
    registry.scorers("spacy.textcat_scorer.v2")(make_textcat_scorer)
    registry.scorers("spacy.textcat_multilabel_scorer.v1")(make_textcat_multilabel_scorer)
    registry.scorers("spacy.textcat_multilabel_scorer.v2")(make_textcat_multilabel_scorer)
    registry.scorers("spacy.lemmatizer_scorer.v1")(make_lemmatizer_scorer)
    registry.scorers("spacy.span_finder_scorer.v1")(make_span_finder_scorer)
    registry.scorers("spacy.spancat_scorer.v1")(make_spancat_scorer)
    
    # Register tok2vec architectures we've modified
    registry.architectures("spacy.Tok2VecListener.v1")(tok2vec_listener_v1)
    registry.architectures("spacy.HashEmbedCNN.v2")(build_hash_embed_cnn_tok2vec)
    registry.architectures("spacy.Tok2Vec.v2")(build_Tok2Vec_model)
    registry.architectures("spacy.MultiHashEmbed.v2")(MultiHashEmbed)
    registry.architectures("spacy.CharacterEmbed.v2")(CharacterEmbed)
    registry.architectures("spacy.MaxoutWindowEncoder.v2")(MaxoutWindowEncoder)
    registry.architectures("spacy.MishWindowEncoder.v2")(MishWindowEncoder)
    registry.architectures("spacy.TorchBiLSTMEncoder.v1")(BiLSTMEncoder)
    
    # Register factory components
    register_factories()
    
    # Set the flag to indicate that the registry has been populated
    REGISTRY_POPULATED = True


def register_factories() -> None:
    """Register all factories with the registry.
    
    This function registers all pipeline component factories, centralizing
    the registrations that were previously done with @Language.factory decorators.
    """
    global FACTORIES_REGISTERED
    if FACTORIES_REGISTERED:
        return
    
    from .language import Language
    
    # Import factory default configurations
    from .pipeline.entity_linker import DEFAULT_NEL_MODEL
    from .pipeline.entityruler import DEFAULT_ENT_ID_SEP
    from .pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL
    from .pipeline.senter import DEFAULT_SENTER_MODEL
    from .pipeline.morphologizer import DEFAULT_MORPH_MODEL
    from .pipeline.spancat import DEFAULT_SPANCAT_MODEL, DEFAULT_SPANCAT_SINGLELABEL_MODEL, DEFAULT_SPANS_KEY
    from .pipeline.span_ruler import DEFAULT_SPANS_KEY as SPAN_RULER_DEFAULT_SPANS_KEY
    from .pipeline.edit_tree_lemmatizer import DEFAULT_EDIT_TREE_LEMMATIZER_MODEL
    from .pipeline.textcat_multilabel import DEFAULT_MULTI_TEXTCAT_MODEL
    from .pipeline.span_finder import DEFAULT_SPAN_FINDER_MODEL
    from .pipeline.ner import DEFAULT_NER_MODEL
    from .pipeline.dep_parser import DEFAULT_PARSER_MODEL
    from .pipeline.tagger import DEFAULT_TAGGER_MODEL
    from .pipeline.multitask import DEFAULT_MT_MODEL
    
    # Import all factory functions
    from .pipeline.attributeruler import make_attribute_ruler
    from .pipeline.entity_linker import make_entity_linker
    from .pipeline.entityruler import make_entity_ruler
    from .pipeline.lemmatizer import make_lemmatizer
    from .pipeline.textcat import make_textcat, DEFAULT_SINGLE_TEXTCAT_MODEL
    from .pipeline.functions import make_token_splitter, make_doc_cleaner
    from .pipeline.tok2vec import make_tok2vec
    from .pipeline.senter import make_senter
    from .pipeline.morphologizer import make_morphologizer
    from .pipeline.spancat import make_spancat, make_spancat_singlelabel
    from .pipeline.span_ruler import make_entity_ruler as make_span_entity_ruler, make_span_ruler
    from .pipeline.edit_tree_lemmatizer import make_edit_tree_lemmatizer
    from .pipeline.textcat_multilabel import make_multilabel_textcat
    from .pipeline.span_finder import make_span_finder
    from .pipeline.ner import make_ner, make_beam_ner
    from .pipeline.dep_parser import make_parser, make_beam_parser
    from .pipeline.tagger import make_tagger
    from .pipeline.multitask import make_nn_labeller
    from .pipeline.sentencizer import make_sentencizer
    
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
        default_config={"model": DEFAULT_TOK2VEC_MODEL}
    )(make_tok2vec)
    
    # senter
    Language.factory(
        "senter",
        assigns=["token.is_sent_start"],
        default_config={"model": DEFAULT_SENTER_MODEL, "overwrite": False, "scorer": {"@scorers": "spacy.senter_scorer.v1"}},
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
            "label_smoothing": 0.0
        },
        default_score_weights={"pos_acc": 0.5, "morph_acc": 0.5, "morph_per_feat": None},
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
    )(make_span_entity_ruler)
    
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
        default_score_weights={"ents_f": 1.0, "ents_p": 0.0, "ents_r": 0.0, "ents_per_type": None},
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
        default_score_weights={"ents_f": 1.0, "ents_p": 0.0, "ents_r": 0.0, "ents_per_type": None},
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
        default_config={"model": DEFAULT_TAGGER_MODEL, "overwrite": False, "scorer": {"@scorers": "spacy.tagger_scorer.v1"}, "neg_prefix": "!", "label_smoothing": 0.0},
        default_score_weights={"tag_acc": 1.0, "pos_acc": 0.0, "tag_micro_p": None, "tag_micro_r": None, "tag_micro_f": None},
    )(make_tagger)
    
    # nn_labeller
    Language.factory(
        "nn_labeller",
        default_config={"labels": None, "target": "dep_tag_offset", "model": DEFAULT_MT_MODEL}
    )(make_nn_labeller)
    
    # sentencizer
    Language.factory(
        "sentencizer",
        assigns=["token.is_sent_start", "doc.sents"],
        default_config={"punct_chars": None, "overwrite": False, "scorer": {"@scorers": "spacy.senter_scorer.v1"}},
        default_score_weights={"sents_f": 1.0, "sents_p": 0.0, "sents_r": 0.0},
    )(make_sentencizer)
    
    # Set the flag to indicate that all factories have been registered
    FACTORIES_REGISTERED = True
