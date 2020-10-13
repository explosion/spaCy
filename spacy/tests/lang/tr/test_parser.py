from spacy.tokens import Doc


def test_tr_noun_chunks_amod_simple(tr_tokenizer):
    text = "sarı kedi"
    heads = [1, 1]
    deps = ["amod", "ROOT"]
    pos = ["ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "sarı kedi "


def test_tr_noun_chunks_nmod_simple(tr_tokenizer):
    text = "arkadaşımın kedisi"  # my friend's cat
    heads = [1, 1]
    deps = ["nmod", "ROOT"]
    pos = ["NOUN", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "arkadaşımın kedisi "


def test_tr_noun_chunks_determiner_simple(tr_tokenizer):
    text = "O kedi"  # that cat
    heads = [1, 1]
    deps = ["det", "ROOT"]
    pos = ["DET", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "O kedi "


def test_tr_noun_chunks_nmod_amod(tr_tokenizer):
    text = "okulun eski müdürü"
    heads = [2, 2, 2]
    deps = ["nmod", "amod", "ROOT"]
    pos = ["NOUN", "ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "okulun eski müdürü "


def test_tr_noun_chunks_one_det_one_adj_simple(tr_tokenizer):
    text = "O sarı kedi"
    heads = [2, 2, 2]
    deps = ["det", "amod", "ROOT"]
    pos = ["DET", "ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "O sarı kedi "


def test_tr_noun_chunks_two_adjs_simple(tr_tokenizer):
    text = "beyaz tombik kedi"
    heads = [2, 2, 2]
    deps = ["amod", "amod", "ROOT"]
    pos = ["ADJ", "ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "beyaz tombik kedi "


def test_tr_noun_chunks_one_det_two_adjs_simple(tr_tokenizer):
    text = "o beyaz tombik kedi"
    heads = [3, 3, 3, 3]
    deps = ["det", "amod", "amod", "ROOT"]
    pos = ["DET", "ADJ", "ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "o beyaz tombik kedi "


def test_tr_noun_chunks_nmod_two(tr_tokenizer):
    text = "kızın saçının rengi"
    heads = [1, 2, 2]
    deps = ["nmod", "nmod", "ROOT"]
    pos = ["NOUN", "NOUN", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "kızın saçının rengi "


def test_tr_noun_chunks_chain_nmod_with_adj(tr_tokenizer):
    text = "ev sahibinin tatlı köpeği"
    heads = [1, 3, 3, 3]
    deps = ["nmod", "nmod", "amod", "ROOT"]
    pos = ["NOUN", "NOUN", "ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "ev sahibinin tatlı köpeği "


def test_tr_noun_chunks_chain_nmod_with_acl(tr_tokenizer):
    text = "ev sahibinin gelen köpeği"
    heads = [1, 3, 3, 3]
    deps = ["nmod", "nmod", "acl", "ROOT"]
    pos = ["NOUN", "NOUN", "VERB", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "ev sahibinin gelen köpeği "


def test_tr_noun_chunks_chain_nmod_head_with_amod_acl(tr_tokenizer):
    text = "arabanın kırdığım sol aynası"
    heads = [3, 3, 3, 3]
    deps = ["nmod", "acl", "amod", "ROOT"]
    pos = ["NOUN", "VERB", "ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "arabanın kırdığım sol aynası "


def test_tr_noun_chunks_nmod_three(tr_tokenizer):
    text = "güney Afrika ülkelerinden Mozambik"
    heads = [1, 2, 3, 3]
    deps = ["nmod", "nmod", "nmod", "ROOT"]
    pos = ["NOUN", "PROPN", "NOUN", "PROPN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "güney Afrika ülkelerinden Mozambik "


def test_tr_noun_chunks_det_amod_nmod(tr_tokenizer):
    text = "bazı eski oyun kuralları"
    heads = [3, 3, 3, 3]
    deps = ["det", "nmod", "nmod", "ROOT"]
    pos = ["DET", "ADJ", "NOUN", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "bazı eski oyun kuralları "


def test_tr_noun_chunks_acl_simple(tr_tokenizer):
    text = "bahçesi olan okul"
    heads = [2, 0, 2]
    deps = ["acl", "cop", "ROOT"]
    pos = ["NOUN", "AUX", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "bahçesi olan okul "


def test_tr_noun_chunks_acl_verb(tr_tokenizer):
    text = "sevdiğim sanatçılar"
    heads = [1, 1]
    deps = ["acl", "ROOT"]
    pos = ["VERB", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "sevdiğim sanatçılar "


def test_tr_noun_chunks_acl_nmod(tr_tokenizer):
    text = "en sevdiğim ses sanatçısı"
    heads = [1, 3, 3, 3]
    deps = ["advmod", "acl", "nmod", "ROOT"]
    pos = ["ADV", "VERB", "NOUN", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "en sevdiğim ses sanatçısı "


def test_tr_noun_chunks_acl_nmod2(tr_tokenizer):
    text = "bildiğim bir turizm şirketi"
    heads = [3, 3, 3, 3]
    deps = ["acl", "det", "nmod", "ROOT"]
    pos = ["VERB", "DET", "NOUN", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "bildiğim bir turizm şirketi "


def test_tr_noun_chunks_np_recursive_nsubj_to_root(tr_tokenizer):
    text = "Simge'nin okuduğu kitap"
    heads = [1, 2, 2]
    deps = ["nsubj", "acl", "ROOT"]
    pos = ["PROPN", "VERB", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "Simge'nin okuduğu kitap "


def test_tr_noun_chunks_np_recursive_nsubj_attached_to_pron_root(tr_tokenizer):
    text = "Simge'nin konuşabileceği birisi"
    heads = [1, 2, 2]
    deps = ["nsubj", "acl", "ROOT"]
    pos = ["PROPN", "VERB", "PRON"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "Simge'nin konuşabileceği birisi "


def test_tr_noun_chunks_np_recursive_nsubj_in_subnp(tr_tokenizer):
    text = "Simge'nin yarın gideceği yer"
    heads = [2, 2, 3, 3]
    deps = ["nsubj", "obl", "acl", "ROOT"]
    pos = ["PROPN", "NOUN", "VERB", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "Simge'nin yarın gideceği yer "


def test_tr_noun_chunks_np_recursive_two_nmods(tr_tokenizer):
    text = "ustanın kapısını degiştireceği çamasır makinası"
    heads = [2, 2, 4, 4, 4]
    deps = ["nsubj", "obj", "acl", "nmod", "ROOT"]
    pos = ["NOUN", "NOUN", "VERB", "NOUN", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "ustanın kapısını degiştireceği çamasır makinası "


def test_tr_noun_chunks_np_recursive_four_nouns(tr_tokenizer):
    text = "kızına piyano dersi verdiğim hanım"
    heads = [3, 2, 3, 4, 4]
    deps = ["obl", "nmod", "obj", "acl", "ROOT"]
    pos = ["NOUN", "NOUN", "NOUN", "VERB", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "kızına piyano dersi verdiğim hanım "


def test_tr_noun_chunks_np_recursive_no_nmod(tr_tokenizer):
    text = "içine birkaç çiçek konmuş olan bir vazo"
    heads = [3, 2, 3, 6, 3, 6, 6]
    deps = ["obl", "det", "nsubj", "acl", "aux", "det", "ROOT"]
    pos = ["ADP", "DET", "NOUN", "VERB", "AUX", "DET", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "içine birkaç çiçek konmuş olan bir vazo "


def test_tr_noun_chunks_np_recursive_long_two_acls(tr_tokenizer):
    text = "içine Simge'nin bahçesinden toplanmış birkaç çiçeğin konmuş olduğu bir vazo"
    heads = [6, 2, 3, 5, 5, 6, 9, 6, 9, 9]
    deps = ["obl", "nmod", "obl", "acl", "det", "nsubj", "acl", "aux", "det", "ROOT"]
    pos = ["ADP", "PROPN", "NOUN", "VERB", "DET", "NOUN", "VERB", "AUX", "DET", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert (
        chunks[0].text_with_ws
        == "içine Simge'nin bahçesinden toplanmış birkaç çiçeğin konmuş olduğu bir vazo "
    )


def test_tr_noun_chunks_two_nouns_in_nmod(tr_tokenizer):
    text = "kız ve erkek çocuklar"
    heads = [3, 2, 0, 3]
    deps = ["nmod", "cc", "conj", "ROOT"]
    pos = ["NOUN", "CCONJ", "NOUN", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "kız ve erkek çocuklar "


def test_tr_noun_chunks_two_nouns_in_nmod2(tr_tokenizer):
    text = "tatlı ve gürbüz çocuklar"
    heads = [3, 2, 0, 3]
    deps = ["amod", "cc", "conj", "ROOT"]
    pos = ["ADJ", "CCONJ", "NOUN", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "tatlı ve gürbüz çocuklar "


def test_tr_noun_chunks_conj_simple(tr_tokenizer):
    text = "Sen ya da ben"
    heads = [0, 3, 1, 0]
    deps = ["ROOT", "cc", "fixed", "conj"]
    pos = ["PRON", "CCONJ", "CCONJ", "PRON"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "ben "
    assert chunks[1].text_with_ws == "Sen "


def test_tr_noun_chunks_conj_three(tr_tokenizer):
    text = "sen, ben ve ondan"
    heads = [0, 2, 0, 4, 0]
    deps = ["ROOT", "punct", "conj", "cc", "conj"]
    pos = ["PRON", "PUNCT", "PRON", "CCONJ", "PRON"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 3
    assert chunks[0].text_with_ws == "ondan "
    assert chunks[1].text_with_ws == "ben "
    assert chunks[2].text_with_ws == "sen "


def test_tr_noun_chunks_conj_three2(tr_tokenizer):
    text = "ben ya da sen ya da onlar"
    heads = [0, 3, 1, 0, 6, 4, 3]
    deps = ["ROOT", "cc", "fixed", "conj", "cc", "fixed", "conj"]
    pos = ["PRON", "CCONJ", "CCONJ", "PRON", "CCONJ", "CCONJ", "PRON"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 3
    assert chunks[0].text_with_ws == "onlar "
    assert chunks[1].text_with_ws == "sen "
    assert chunks[2].text_with_ws == "ben "


def test_tr_noun_chunks_conj_and_adj_phrase(tr_tokenizer):
    text = "ben ve akıllı çocuk"
    heads = [0, 3, 3, 0]
    deps = ["ROOT", "cc", "amod", "conj"]
    pos = ["PRON", "CCONJ", "ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "akıllı çocuk "
    assert chunks[1].text_with_ws == "ben "


def test_tr_noun_chunks_conj_fixed_adj_phrase(tr_tokenizer):
    text = "ben ya da akıllı çocuk"
    heads = [0, 4, 1, 4, 0]
    deps = ["ROOT", "cc", "fixed", "amod", "conj"]
    pos = ["PRON", "CCONJ", "CCONJ", "ADJ", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "akıllı çocuk "
    assert chunks[1].text_with_ws == "ben "


def test_tr_noun_chunks_conj_subject(tr_tokenizer):
    text = "Sen ve ben iyi anlaşıyoruz"
    heads = [4, 2, 0, 2, 4]
    deps = ["nsubj", "cc", "conj", "adv", "ROOT"]
    pos = ["PRON", "CCONJ", "PRON", "ADV", "VERB"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "ben "
    assert chunks[1].text_with_ws == "Sen "


def test_tr_noun_chunks_conj_noun_head_verb(tr_tokenizer):
    text = "Simge babasını görmüyormuş, annesini değil"
    heads = [2, 2, 2, 4, 2, 4]
    deps = ["nsubj", "obj", "ROOT", "punct", "conj", "aux"]
    pos = ["PROPN", "NOUN", "VERB", "PUNCT", "NOUN", "AUX"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 3
    assert chunks[0].text_with_ws == "annesini "
    assert chunks[1].text_with_ws == "babasını "
    assert chunks[2].text_with_ws == "Simge "


def test_tr_noun_chunks_flat_simple(tr_tokenizer):
    text = "New York"
    heads = [0, 0]
    deps = ["ROOT", "flat"]
    pos = ["PROPN", "PROPN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "New York "


def test_tr_noun_chunks_flat_names_and_title(tr_tokenizer):
    text = "Gazi Mustafa Kemal"
    heads = [1, 1, 1]
    deps = ["nmod", "ROOT", "flat"]
    pos = ["PROPN", "PROPN", "PROPN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "Gazi Mustafa Kemal "


def test_tr_noun_chunks_flat_names_and_title2(tr_tokenizer):
    text = "Ahmet Vefik Paşa"
    heads = [2, 0, 2]
    deps = ["nmod", "flat", "ROOT"]
    pos = ["PROPN", "PROPN", "PROPN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "Ahmet Vefik Paşa "


def test_tr_noun_chunks_flat_name_lastname_and_title(tr_tokenizer):
    text = "Cumhurbaşkanı Ahmet Necdet Sezer"
    heads = [1, 1, 1, 1]
    deps = ["nmod", "ROOT", "flat", "flat"]
    pos = ["NOUN", "PROPN", "PROPN", "PROPN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "Cumhurbaşkanı Ahmet Necdet Sezer "


def test_tr_noun_chunks_flat_in_nmod(tr_tokenizer):
    text = "Ahmet Sezer adında bir ögrenci"
    heads = [2, 0, 4, 4, 4]
    deps = ["nmod", "flat", "nmod", "det", "ROOT"]
    pos = ["PROPN", "PROPN", "NOUN", "DET", "NOUN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "Ahmet Sezer adında bir ögrenci "


def test_tr_noun_chunks_flat_and_chain_nmod(tr_tokenizer):
    text = "Batı Afrika ülkelerinden Sierra Leone"
    heads = [1, 2, 3, 3, 3]
    deps = ["nmod", "nmod", "nmod", "ROOT", "flat"]
    pos = ["NOUN", "PROPN", "NOUN", "PROPN", "PROPN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 1
    assert chunks[0].text_with_ws == "Batı Afrika ülkelerinden Sierra Leone "


def test_tr_noun_chunks_two_flats_conjed(tr_tokenizer):
    text = "New York ve Sierra Leone"
    heads = [0, 0, 3, 0, 3]
    deps = ["ROOT", "flat", "cc", "conj", "flat"]
    pos = ["PROPN", "PROPN", "CCONJ", "PROPN", "PROPN"]
    tokens = tr_tokenizer(text)
    doc = Doc(
        tokens.vocab, words=[t.text for t in tokens], pos=pos, heads=heads, deps=deps
    )
    chunks = list(doc.noun_chunks)
    assert len(chunks) == 2
    assert chunks[0].text_with_ws == "Sierra Leone "
    assert chunks[1].text_with_ws == "New York "
