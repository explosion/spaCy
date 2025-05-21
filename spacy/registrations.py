"""Centralized registry population for spaCy config

This module centralizes registry decorations to prevent circular import issues
with Cython annotation changes from __future__ import annotations. Functions
remain in their original locations, but decoration is moved here.

Component definitions and registrations are in spacy/pipeline/factories.py
"""
# Global flag to track if registry has been populated
REGISTRY_POPULATED = False


def populate_registry() -> None:
    """Populate the registry with all necessary components.

    This function should be called before accessing the registry, to ensure
    it's populated. The function uses a global flag to prevent repopulation.
    """
    global REGISTRY_POPULATED
    if REGISTRY_POPULATED:
        return

    # Import all necessary modules
    from .lang.ja import create_tokenizer as create_japanese_tokenizer
    from .lang.ko import create_tokenizer as create_korean_tokenizer
    from .lang.th import create_thai_tokenizer
    from .lang.vi import create_vietnamese_tokenizer
    from .lang.zh import create_chinese_tokenizer
    from .language import load_lookups_data
    from .matcher.levenshtein import make_levenshtein_compare
    from .ml.models.entity_linker import (
        create_candidates,
        create_candidates_batch,
        empty_kb,
        empty_kb_for_config,
        load_kb,
    )
    from .pipeline.attributeruler import make_attribute_ruler_scorer
    from .pipeline.dep_parser import make_parser_scorer

    # Import the functions we refactored by removing direct registry decorators
    from .pipeline.entity_linker import make_entity_linker_scorer
    from .pipeline.entityruler import (
        make_entity_ruler_scorer as make_entityruler_scorer,
    )
    from .pipeline.lemmatizer import make_lemmatizer_scorer
    from .pipeline.morphologizer import make_morphologizer_scorer
    from .pipeline.ner import make_ner_scorer
    from .pipeline.senter import make_senter_scorer
    from .pipeline.span_finder import make_span_finder_scorer
    from .pipeline.span_ruler import (
        make_overlapping_labeled_spans_scorer,
        make_preserve_existing_ents_filter,
        make_prioritize_new_ents_filter,
    )
    from .pipeline.spancat import (
        build_ngram_range_suggester,
        build_ngram_suggester,
        build_preset_spans_suggester,
        make_spancat_scorer,
    )

    # Import all pipeline components that were using registry decorators
    from .pipeline.tagger import make_tagger_scorer
    from .pipeline.textcat import make_textcat_scorer
    from .pipeline.textcat_multilabel import make_textcat_multilabel_scorer
    from .util import make_first_longest_spans_filter, registry

    # Register miscellaneous components
    registry.misc("spacy.first_longest_spans_filter.v1")(
        make_first_longest_spans_filter
    )
    registry.misc("spacy.ngram_suggester.v1")(build_ngram_suggester)
    registry.misc("spacy.ngram_range_suggester.v1")(build_ngram_range_suggester)
    registry.misc("spacy.preset_spans_suggester.v1")(build_preset_spans_suggester)
    registry.misc("spacy.prioritize_new_ents_filter.v1")(
        make_prioritize_new_ents_filter
    )
    registry.misc("spacy.prioritize_existing_ents_filter.v1")(
        make_preserve_existing_ents_filter
    )
    registry.misc("spacy.levenshtein_compare.v1")(make_levenshtein_compare)
    # KB-related registrations
    registry.misc("spacy.KBFromFile.v1")(load_kb)
    registry.misc("spacy.EmptyKB.v2")(empty_kb_for_config)
    registry.misc("spacy.EmptyKB.v1")(empty_kb)
    registry.misc("spacy.CandidateGenerator.v1")(create_candidates)
    registry.misc("spacy.CandidateBatchGenerator.v1")(create_candidates_batch)
    registry.misc("spacy.LookupsDataLoader.v1")(load_lookups_data)

    # Need to get references to the existing functions in registry by importing the function that is there
    # For the registry that was previously decorated

    # Import ML components that use registry
    from .language import create_tokenizer
    from .ml._precomputable_affine import PrecomputableAffine
    from .ml.callbacks import (
        create_models_and_pipes_with_nvtx_range,
        create_models_with_nvtx_range,
    )
    from .ml.extract_ngrams import extract_ngrams
    from .ml.extract_spans import extract_spans

    # Import decorator-removed ML components
    from .ml.featureextractor import FeatureExtractor
    from .ml.models.entity_linker import build_nel_encoder
    from .ml.models.multi_task import (
        create_pretrain_characters,
        create_pretrain_vectors,
    )
    from .ml.models.parser import build_tb_parser_model
    from .ml.models.span_finder import build_finder_model
    from .ml.models.spancat import (
        build_linear_logistic,
        build_mean_max_reducer,
        build_spancat_model,
    )
    from .ml.models.tagger import build_tagger_model
    from .ml.models.textcat import (
        build_bow_text_classifier,
        build_bow_text_classifier_v3,
        build_reduce_text_classifier,
        build_simple_cnn_text_classifier,
        build_text_classifier_lowdata,
        build_text_classifier_v2,
        build_textcat_parametric_attention_v1,
    )
    from .ml.models.tok2vec import (
        BiLSTMEncoder,
        CharacterEmbed,
        MaxoutWindowEncoder,
        MishWindowEncoder,
        MultiHashEmbed,
        build_hash_embed_cnn_tok2vec,
        build_Tok2Vec_model,
        tok2vec_listener_v1,
    )
    from .ml.staticvectors import StaticVectors
    from .ml.tb_framework import TransitionModel
    from .training.augment import (
        create_combined_augmenter,
        create_lower_casing_augmenter,
        create_orth_variants_augmenter,
    )
    from .training.batchers import (
        configure_minibatch,
        configure_minibatch_by_padded_size,
        configure_minibatch_by_words,
    )
    from .training.callbacks import create_copy_from_base_model
    from .training.loggers import console_logger, console_logger_v3

    # Register scorers
    registry.scorers("spacy.tagger_scorer.v1")(make_tagger_scorer)
    registry.scorers("spacy.ner_scorer.v1")(make_ner_scorer)
    # span_ruler_scorer removed as it's not in span_ruler.py
    registry.scorers("spacy.entity_ruler_scorer.v1")(make_entityruler_scorer)
    registry.scorers("spacy.senter_scorer.v1")(make_senter_scorer)
    registry.scorers("spacy.textcat_scorer.v1")(make_textcat_scorer)
    registry.scorers("spacy.textcat_scorer.v2")(make_textcat_scorer)
    registry.scorers("spacy.textcat_multilabel_scorer.v1")(
        make_textcat_multilabel_scorer
    )
    registry.scorers("spacy.textcat_multilabel_scorer.v2")(
        make_textcat_multilabel_scorer
    )
    registry.scorers("spacy.lemmatizer_scorer.v1")(make_lemmatizer_scorer)
    registry.scorers("spacy.span_finder_scorer.v1")(make_span_finder_scorer)
    registry.scorers("spacy.spancat_scorer.v1")(make_spancat_scorer)
    registry.scorers("spacy.entity_linker_scorer.v1")(make_entity_linker_scorer)
    registry.scorers("spacy.overlapping_labeled_spans_scorer.v1")(
        make_overlapping_labeled_spans_scorer
    )
    registry.scorers("spacy.attribute_ruler_scorer.v1")(make_attribute_ruler_scorer)
    registry.scorers("spacy.parser_scorer.v1")(make_parser_scorer)
    registry.scorers("spacy.morphologizer_scorer.v1")(make_morphologizer_scorer)

    # Register tokenizers
    registry.tokenizers("spacy.Tokenizer.v1")(create_tokenizer)
    registry.tokenizers("spacy.ja.JapaneseTokenizer")(create_japanese_tokenizer)
    registry.tokenizers("spacy.zh.ChineseTokenizer")(create_chinese_tokenizer)
    registry.tokenizers("spacy.ko.KoreanTokenizer")(create_korean_tokenizer)
    registry.tokenizers("spacy.vi.VietnameseTokenizer")(create_vietnamese_tokenizer)
    registry.tokenizers("spacy.th.ThaiTokenizer")(create_thai_tokenizer)

    # Register tok2vec architectures we've modified
    registry.architectures("spacy.Tok2VecListener.v1")(tok2vec_listener_v1)
    registry.architectures("spacy.HashEmbedCNN.v2")(build_hash_embed_cnn_tok2vec)
    registry.architectures("spacy.Tok2Vec.v2")(build_Tok2Vec_model)
    registry.architectures("spacy.MultiHashEmbed.v2")(MultiHashEmbed)
    registry.architectures("spacy.CharacterEmbed.v2")(CharacterEmbed)
    registry.architectures("spacy.MaxoutWindowEncoder.v2")(MaxoutWindowEncoder)
    registry.architectures("spacy.MishWindowEncoder.v2")(MishWindowEncoder)
    registry.architectures("spacy.TorchBiLSTMEncoder.v1")(BiLSTMEncoder)
    registry.architectures("spacy.EntityLinker.v2")(build_nel_encoder)
    registry.architectures("spacy.TextCatCNN.v2")(build_simple_cnn_text_classifier)
    registry.architectures("spacy.TextCatBOW.v2")(build_bow_text_classifier)
    registry.architectures("spacy.TextCatBOW.v3")(build_bow_text_classifier_v3)
    registry.architectures("spacy.TextCatEnsemble.v2")(build_text_classifier_v2)
    registry.architectures("spacy.TextCatLowData.v1")(build_text_classifier_lowdata)
    registry.architectures("spacy.TextCatParametricAttention.v1")(
        build_textcat_parametric_attention_v1
    )
    registry.architectures("spacy.TextCatReduce.v1")(build_reduce_text_classifier)
    registry.architectures("spacy.SpanCategorizer.v1")(build_spancat_model)
    registry.architectures("spacy.SpanFinder.v1")(build_finder_model)
    registry.architectures("spacy.TransitionBasedParser.v2")(build_tb_parser_model)
    registry.architectures("spacy.PretrainVectors.v1")(create_pretrain_vectors)
    registry.architectures("spacy.PretrainCharacters.v1")(create_pretrain_characters)
    registry.architectures("spacy.Tagger.v2")(build_tagger_model)

    # Register layers
    registry.layers("spacy.FeatureExtractor.v1")(FeatureExtractor)
    registry.layers("spacy.extract_spans.v1")(extract_spans)
    registry.layers("spacy.extract_ngrams.v1")(extract_ngrams)
    registry.layers("spacy.LinearLogistic.v1")(build_linear_logistic)
    registry.layers("spacy.mean_max_reducer.v1")(build_mean_max_reducer)
    registry.layers("spacy.StaticVectors.v2")(StaticVectors)
    registry.layers("spacy.PrecomputableAffine.v1")(PrecomputableAffine)
    registry.layers("spacy.CharEmbed.v1")(CharacterEmbed)
    registry.layers("spacy.TransitionModel.v1")(TransitionModel)

    # Register callbacks
    registry.callbacks("spacy.copy_from_base_model.v1")(create_copy_from_base_model)
    registry.callbacks("spacy.models_with_nvtx_range.v1")(create_models_with_nvtx_range)
    registry.callbacks("spacy.models_and_pipes_with_nvtx_range.v1")(
        create_models_and_pipes_with_nvtx_range
    )

    # Register loggers
    registry.loggers("spacy.ConsoleLogger.v2")(console_logger)
    registry.loggers("spacy.ConsoleLogger.v3")(console_logger_v3)

    # Register batchers
    registry.batchers("spacy.batch_by_padded.v1")(configure_minibatch_by_padded_size)
    registry.batchers("spacy.batch_by_words.v1")(configure_minibatch_by_words)
    registry.batchers("spacy.batch_by_sequence.v1")(configure_minibatch)

    # Register augmenters
    registry.augmenters("spacy.combined_augmenter.v1")(create_combined_augmenter)
    registry.augmenters("spacy.lower_case.v1")(create_lower_casing_augmenter)
    registry.augmenters("spacy.orth_variants.v1")(create_orth_variants_augmenter)

    # Set the flag to indicate that the registry has been populated
    REGISTRY_POPULATED = True
