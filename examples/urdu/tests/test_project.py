from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from convert_bio import convert_bio_jsonl  # noqa: E402
from convert_conllu import convert_conllu  # noqa: E402
from convert_ner import ConversionError, convert_jsonl, write_docbin  # noqa: E402
from overfit_ner import run_overfit  # noqa: E402
from split import (  # noqa: E402
    dedupe,
    load_jsonl,
    official_split_mode,
    preserve_official_splits,
    split_groups,
)


@pytest.fixture
def nlp():
    import spacy

    return spacy.blank("ur")


def test_ner_fixture_converts(nlp, tmp_path):
    docs, counts = convert_jsonl(
        ROOT / "fixtures" / "ner_train.jsonl",
        nlp,
        skip_invalid=False,
        require_token_alignment=True,
    )
    assert counts["kept"] == 3
    assert counts["invalid"] == 0
    assert counts["spans"] == 6
    assert counts["negatives"] == 0
    assert counts["labels"]["PER"] == 2
    assert docs[0].ents
    expected = "عمران خان نے اسلام آباد میں خطاب کیا۔"
    assert docs[0].text == expected
    out = tmp_path / "train.spacy"
    write_docbin(docs, out)
    from spacy.tokens import DocBin

    restored = list(DocBin().from_disk(out).get_docs(nlp.vocab))
    assert [(e.text, e.label_) for e in restored[0].ents] == [
        (e.text, e.label_) for e in docs[0].ents
    ]


def test_ner_rejects_overlap(nlp, tmp_path):
    path = tmp_path / "overlap.jsonl"
    path.write_text(
        json.dumps(
            {
                "id": "bad-overlap",
                "text": "عمران خان اسلام آباد",
                "entities": [
                    {"start": 0, "end": 9, "label": "PER"},
                    {"start": 3, "end": 9, "label": "PER"},
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ConversionError, match="overlapping"):
        convert_jsonl(path, nlp, skip_invalid=False, require_token_alignment=True)


def test_ner_skip_invalid_records_count(nlp, tmp_path):
    path = tmp_path / "mixed.jsonl"
    good = {
        "id": "ok",
        "text": "کراچی",
        "entities": [{"start": 0, "end": 5, "label": "LOC"}],
    }
    bad = {
        "id": "bad",
        "text": "کراچی",
        "entities": [{"start": -1, "end": 2, "label": "LOC"}],
    }
    path.write_text(
        json.dumps(good, ensure_ascii=False)
        + "\n"
        + json.dumps(bad, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    docs, counts = convert_jsonl(
        path, nlp, skip_invalid=True, require_token_alignment=True
    )
    assert counts["kept"] == 1
    assert counts["invalid"] == 1
    assert docs[0].user_data["id"] == "ok"


def test_ner_rejects_unaligned_span(nlp, tmp_path):
    path = tmp_path / "unaligned.jsonl"
    path.write_text(
        json.dumps(
            {
                "id": "unaligned",
                "text": "اسلام آباد",
                "entities": [{"start": 1, "end": 4, "label": "LOC"}],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ConversionError, match="aligned"):
        convert_jsonl(path, nlp, skip_invalid=False, require_token_alignment=True)


def test_split_keeps_source_groups_disjoint():
    rows = [
        {"id": "a1", "source_id": "A", "text": "aaa one"},
        {"id": "a2", "source_id": "A", "text": "aaa two"},
        {"id": "b1", "source_id": "B", "text": "bbb one"},
        {"id": "c1", "source_id": "C", "text": "ccc one"},
        {"id": "d1", "source_id": "D", "text": "ddd one"},
        {"id": "e1", "source_id": "E", "text": "eee one"},
    ]
    kept, dropped = dedupe(rows)
    assert dropped == 0
    splits = split_groups(kept, seed=0, train_frac=0.5, dev_frac=0.2)
    by_split = {
        name: {row["source_id"] for row in items} for name, items in splits.items()
    }
    assert by_split["train"].isdisjoint(by_split["dev"])
    assert by_split["train"].isdisjoint(by_split["test"])
    assert by_split["dev"].isdisjoint(by_split["test"])
    # Same article does not appear in two splits.
    assert "A" not in (by_split["train"] & by_split["dev"] & by_split["test"])


def test_split_dedupes_near_duplicates():
    rows = [
        {"id": "1", "text": "ایک جملہ"},
        {"id": "2", "text": "ایک   جملہ"},
    ]
    kept, dropped = dedupe(rows)
    assert dropped == 1
    assert len(kept) == 1


def test_conllu_keeps_underscore_surface(tmp_path):
    docs, counts = convert_conllu(
        ROOT / "fixtures" / "syntax_train.conllu",
        n_sents=1,
        merge_subtokens=False,
        skip_invalid=False,
    )
    assert counts["kept"] == 2
    underscore_doc = next(doc for doc in docs if any("_" in t.text for t in doc))
    assert "بات_چیت" in [t.text for t in underscore_doc]
    assert "بات چیت" not in underscore_doc.text
    assert underscore_doc.user_data["reconstructed"] is True
    out = tmp_path / "syntax.spacy"
    from spacy.tokens import DocBin

    DocBin(docs=docs, store_user_data=True).to_disk(out)
    assert out.exists()


def test_conllu_rejects_missing_root(tmp_path):
    bad = tmp_path / "bad.conllu"
    bad.write_text(
        """
1	یہ	یہ	PRON	PRP	_	2	nsubj	_	_
2	ہے	ہے	VERB	VM	_	2	aux	_	_
""".strip()
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="ROOT"):
        convert_conllu(bad, n_sents=1, merge_subtokens=False, skip_invalid=False)


def test_ner_config_exists():
    text = (ROOT / "configs" / "ner.cfg").read_text(encoding="utf-8")
    assert 'lang = "ur"' in text
    assert 'pipeline = ["tok2vec", "ner"]' in text
    assert "seed = 0" in text


def test_syntax_config_component_order():
    text = (ROOT / "configs" / "syntax.cfg").read_text(encoding="utf-8")
    assert (
        'pipeline = ["tok2vec", "morphologizer", "parser", "trainable_lemmatizer"]'
        in text
    )


def test_trf_config_is_xlm_roberta_not_bert():
    text = (ROOT / "configs" / "ner_trf.cfg").read_text(encoding="utf-8")
    assert "spacy-transformers.TransformerModel.v3" in text
    assert "FacebookAI/xlm-roberta-base" in text
    assert "spacy-transformers.TransformerListener.v1" in text
    assert "strided_spans.v1" in text
    assert "window = 128" in text
    assert "stride = 96" in text
    assert "discard_oversize = false" in text
    assert "e73636d4f797dec63c3081bb6ed5c7b0bb3f2089" in text
    assert "spacy-curated-transformers.TransformerModel" not in text


def test_trf_factory_optional():
    pytest.importorskip("spacy_transformers")
    from spacy.language import Language

    assert "transformer" in Language.factories


def test_syntax_config_keeps_parser_min_action_freq_and_no_sentencizer():
    text = (ROOT / "configs" / "syntax.cfg").read_text(encoding="utf-8")
    assert "min_action_freq = 30" in text
    assert "sentencizer" not in text
    assert "senter" not in text


def test_ner_missing_entities_key_is_not_a_negative(nlp, tmp_path):
    path = tmp_path / "missing.jsonl"
    path.write_text(
        json.dumps({"id": "no-ents", "text": "آج موسم اچھا ہے۔"}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ConversionError, match="missing entities"):
        convert_jsonl(path, nlp, skip_invalid=False, require_token_alignment=True)


def test_ner_empty_entities_is_negative(nlp):
    docs, counts = convert_jsonl(
        ROOT / "fixtures" / "ner_negative.jsonl",
        nlp,
        skip_invalid=False,
        require_token_alignment=True,
    )
    assert counts["kept"] == 1
    assert counts["negatives"] == 1
    assert counts["spans"] == 0
    assert list(docs[0].ents) == []


def test_ner_empty_file_errors(nlp, tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("\n", encoding="utf-8")
    with pytest.raises(ConversionError, match="no JSONL records"):
        convert_jsonl(path, nlp, skip_invalid=False, require_token_alignment=True)


def test_ner_missing_file_errors(nlp, tmp_path):
    with pytest.raises(ConversionError, match="missing input file"):
        convert_jsonl(
            tmp_path / "absent.jsonl",
            nlp,
            skip_invalid=False,
            require_token_alignment=True,
        )


def test_ner_skip_all_invalid_errors(nlp, tmp_path):
    path = tmp_path / "all-bad.jsonl"
    path.write_text(
        json.dumps(
            {
                "id": "bad",
                "text": "کراچی",
                "entities": [{"start": -1, "end": 2, "label": "LOC"}],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ConversionError, match="no valid documents"):
        convert_jsonl(path, nlp, skip_invalid=True, require_token_alignment=True)


def test_split_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="missing input file"):
        load_jsonl(tmp_path / "absent.jsonl")


def test_split_empty_file_errors(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="no JSONL records"):
        load_jsonl(path)


def test_split_preserves_official_and_quarantines_contamination():
    rows = [
        {
            "id": "t1",
            "source_id": "A",
            "split": "train",
            "text": "train only",
        },
        {
            "id": "d1",
            "source_id": "B",
            "split": "dev",
            "text": "dev only",
        },
        {
            "id": "e1",
            "source_id": "C",
            "split": "test",
            "text": "test only",
        },
        {
            "id": "leak-train",
            "source_id": "LEAK",
            "split": "train",
            "text": "same article text",
        },
        {
            "id": "leak-test",
            "source_id": "LEAK",
            "split": "test",
            "text": "same article text",
        },
    ]
    assert official_split_mode(rows)
    splits, quarantined = preserve_official_splits(rows)
    assert {row["id"] for row in splits["train"]} == {"t1"}
    assert {row["id"] for row in splits["dev"]} == {"d1"}
    assert {row["id"] for row in splits["test"]} == {"e1"}
    assert {row["id"] for row in quarantined} == {"leak-train", "leak-test"}


def test_split_rejects_partial_official_field():
    rows = [
        {"id": "t1", "text": "aaa", "split": "train"},
        {"id": "x1", "text": "bbb"},
    ]
    with pytest.raises(ValueError, match="mix official"):
        official_split_mode(rows)


def test_bio_fixture_is_reconstructed(nlp):
    docs, counts = convert_bio_jsonl(
        ROOT / "fixtures" / "bio_train.jsonl", nlp, skip_invalid=False
    )
    assert counts["kept"] == 2
    assert counts["negatives"] == 1
    assert counts["spans"] == 2
    assert docs[0].user_data["reconstructed"] is True
    assert docs[0].text == "عمران خان کراچی گئے ۔"
    assert [(ent.text, ent.label_) for ent in docs[0].ents] == [
        ("عمران خان", "PER"),
        ("کراچی", "LOC"),
    ]


def test_bio_rejects_i_without_b(nlp, tmp_path):
    path = tmp_path / "bad-bio.jsonl"
    path.write_text(
        json.dumps(
            {
                "id": "bad-bio",
                "tokens": ["خان", "گئے"],
                "tags": ["I-PER", "O"],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ConversionError, match="invalid BIO"):
        convert_bio_jsonl(path, nlp, skip_invalid=False)


def test_conllu_empty_file_errors(tmp_path):
    path = tmp_path / "empty.conllu"
    path.write_text("\n", encoding="utf-8")
    with pytest.raises(ValueError, match="empty CoNLL-U"):
        convert_conllu(path, n_sents=1, merge_subtokens=False, skip_invalid=False)


def test_conllu_missing_file_errors(tmp_path):
    with pytest.raises(ValueError, match="missing input file"):
        convert_conllu(
            tmp_path / "absent.conllu",
            n_sents=1,
            merge_subtokens=False,
            skip_invalid=False,
        )


def test_conllu_sentence_starts_are_gold_annotation():
    docs, counts = convert_conllu(
        ROOT / "fixtures" / "syntax_train.conllu",
        n_sents=1,
        merge_subtokens=False,
        skip_invalid=False,
    )
    assert counts["kept"] == 2
    assert counts["injected_sentence_starts"] in {0, 2}
    for doc in docs:
        assert doc.has_annotation("SENT_START")
        assert doc.has_annotation("LEMMA")
        assert doc.has_annotation("MORPH")
        assert len(list(doc.sents)) == 1
        assert doc.user_data["sentence_starts"] in {
            "injected_single_sentence",
            "from_treebank",
        }
        assert doc.user_data["reconstructed"] is True
    lemma_doc = next(doc for doc in docs if "بات_چیت" in [t.text for t in doc])
    assert lemma_doc[1].lemma_ == "ہونا"


def test_ner_overfit_learns_training_fixture():
    result = run_overfit(
        ROOT / "fixtures" / "ner_overfit.jsonl",
        seed=0,
        max_steps=40,
        min_f=1.0,
    )
    assert result["ents_f"] >= 1.0
    assert result["after"] != result["before"]
    assert all(math.isfinite(value) for value in result["losses"].values())
