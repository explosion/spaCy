import pytest

import spacy
from spacy.lang.en import English
from spacy.pipeline import Sentencizer
from spacy.tokens import Doc


def test_sentencizer(en_vocab):
    doc = Doc(en_vocab, words=["Hello", "!", "This", "is", "a", "test", "."])
    sentencizer = Sentencizer(punct_chars=None)
    doc = sentencizer(doc)
    assert doc.has_annotation("SENT_START")
    sent_starts = [t.is_sent_start for t in doc]
    sent_ends = [t.is_sent_end for t in doc]
    assert sent_starts == [True, False, True, False, False, False, False]
    assert sent_ends == [False, True, False, False, False, False, True]
    assert len(list(doc.sents)) == 2


def test_sentencizer_pipe():
    texts = ["Hello! This is a test.", "Hi! This is a test."]
    nlp = English()
    nlp.add_pipe("sentencizer")
    for doc in nlp.pipe(texts):
        assert doc.has_annotation("SENT_START")
        sent_starts = [t.is_sent_start for t in doc]
        assert sent_starts == [True, False, True, False, False, False, False]
        assert len(list(doc.sents)) == 2
    for ex in nlp.pipe(texts):
        doc = ex.doc
        assert doc.has_annotation("SENT_START")
        sent_starts = [t.is_sent_start for t in doc]
        assert sent_starts == [True, False, True, False, False, False, False]
        assert len(list(doc.sents)) == 2


def test_sentencizer_empty_docs():
    one_empty_text = [""]
    many_empty_texts = ["", "", ""]
    some_empty_texts = ["hi", "", "This is a test. Here are two sentences.", ""]
    nlp = English()
    nlp.add_pipe("sentencizer")
    for texts in [one_empty_text, many_empty_texts, some_empty_texts]:
        for doc in nlp.pipe(texts):
            assert doc.has_annotation("SENT_START")
            sent_starts = [t.is_sent_start for t in doc]
            if len(doc) == 0:
                assert sent_starts == []
            else:
                assert len(sent_starts) > 0


@pytest.mark.parametrize(
    "words,sent_starts,sent_ends,n_sents",
    [
        # The expected result here is that the duplicate punctuation gets merged
        # onto the same sentence and no one-token sentence is created for them.
        (
            ["Hello", "!", ".", "Test", ".", ".", "ok"],
            [True, False, False, True, False, False, True],
            [False, False, True, False, False, True, True],
            3,
        ),
        # We also want to make sure ¡ and ¿ aren't treated as sentence end
        # markers, even though they're punctuation
        (
            ["¡", "Buen", "día", "!", "Hola", ",", "¿", "qué", "tal", "?"],
            [True, False, False, False, True, False, False, False, False, False],
            [False, False, False, True, False, False, False, False, False, True],
            2,
        ),
        # The Token.is_punct check ensures that quotes are handled as well
        (
            ['"', "Nice", "!", '"', "I", "am", "happy", "."],
            [True, False, False, False, True, False, False, False],
            [False, False, False, True, False, False, False, True],
            2,
        ),
    ],
)
def test_sentencizer_complex(en_vocab, words, sent_starts, sent_ends, n_sents):
    doc = Doc(en_vocab, words=words)
    sentencizer = Sentencizer(punct_chars=None)
    doc = sentencizer(doc)
    assert doc.has_annotation("SENT_START")
    assert [t.is_sent_start for t in doc] == sent_starts
    assert [t.is_sent_end for t in doc] == sent_ends
    assert len(list(doc.sents)) == n_sents


@pytest.mark.parametrize(
    "punct_chars,words,sent_starts,sent_ends,n_sents",
    [
        (
            ["~", "?"],
            ["Hello", "world", "~", "A", ".", "B", "."],
            [True, False, False, True, False, False, False],
            [False, False, True, False, False, False, True],
            2,
        ),
        # Even thought it's not common, the punct_chars should be able to
        # handle any tokens
        (
            [".", "ö"],
            ["Hello", ".", "Test", "ö", "Ok", "."],
            [True, False, True, False, True, False],
            [False, True, False, True, False, True],
            3,
        ),
    ],
)
def test_sentencizer_custom_punct(
    en_vocab, punct_chars, words, sent_starts, sent_ends, n_sents
):
    doc = Doc(en_vocab, words=words)
    sentencizer = Sentencizer(punct_chars=punct_chars)
    doc = sentencizer(doc)
    assert doc.has_annotation("SENT_START")
    assert [t.is_sent_start for t in doc] == sent_starts
    assert [t.is_sent_end for t in doc] == sent_ends
    assert len(list(doc.sents)) == n_sents


def test_sentencizer_serialize_bytes(en_vocab):
    punct_chars = [".", "~", "+"]
    sentencizer = Sentencizer(punct_chars=punct_chars)
    assert sentencizer.punct_chars == set(punct_chars)
    bytes_data = sentencizer.to_bytes()
    new_sentencizer = Sentencizer(punct_chars=None).from_bytes(bytes_data)
    assert new_sentencizer.punct_chars == set(punct_chars)


@pytest.mark.parametrize(
    # fmt: off
    "lang,text",
    [
        ('bn', 'বাংলা ভাষা (বাঙলা, বাঙ্গলা, তথা বাঙ্গালা নামগুলোতেও পরিচিত) একটি ইন্দো-আর্য ভাষা, যা দক্ষিণ এশিয়ার বাঙালি জাতির প্রধান কথ্য ও লেখ্য ভাষা। মাতৃভাষীর সংখ্যায় বাংলা ইন্দো-ইউরোপীয় ভাষা পরিবারের চতুর্থ ও বিশ্বের ষষ্ঠ বৃহত্তম ভাষা।[৫] মোট ব্যবহারকারীর সংখ্যা অনুসারে বাংলা বিশ্বের সপ্তম বৃহত্তম ভাষা। বাংলা সার্বভৌম ভাষাভিত্তিক জাতিরাষ্ট্র বাংলাদেশের একমাত্র রাষ্ট্রভাষা তথা সরকারি ভাষা[৬] এবং ভারতের পশ্চিমবঙ্গ, ত্রিপুরা, আসামের বরাক উপত্যকার সরকারি ভাষা। বঙ্গোপসাগরে অবস্থিত আন্দামান দ্বীপপুঞ্জের প্রধান কথ্য ভাষা বাংলা। এছাড়া ভারতের ঝাড়খণ্ড, বিহার, মেঘালয়, মিজোরাম, উড়িষ্যা রাজ্যগুলোতে উল্লেখযোগ্য পরিমাণে বাংলাভাষী জনগণ রয়েছে। ভারতে হিন্দির পরেই সর্বাধিক প্রচলিত ভাষা বাংলা।[৭][৮] এছাড়াও মধ্য প্রাচ্য, আমেরিকা ও ইউরোপে উল্লেখযোগ্য পরিমাণে বাংলাভাষী অভিবাসী রয়েছে।[৯] সারা বিশ্বে সব মিলিয়ে ২৬ কোটির অধিক লোক দৈনন্দিন জীবনে বাংলা ব্যবহার করে।[২] বাংলাদেশের জাতীয় সঙ্গীত এবং ভারতের জাতীয় সঙ্গীত ও স্তোত্র বাংলাতে রচিত।'),
        ('de', 'Die deutsche Sprache bzw. Deutsch ([dɔʏ̯t͡ʃ]; abgekürzt dt. oder dtsch.) ist eine westgermanische Sprache. Ihr Sprachraum umfasst Deutschland, Österreich, die Deutschschweiz, Liechtenstein, Luxemburg, Ostbelgien, Südtirol, das Elsass und Lothringen sowie Nordschleswig. Außerdem ist sie eine Minderheitensprache in einigen europäischen und außereuropäischen Ländern, z. B. in Rumänien und Südafrika, sowie Nationalsprache im afrikanischen Namibia.'),
        ('hi', 'हिन्दी विश्व की एक प्रमुख भाषा है एवं भारत की राजभाषा है। केन्द्रीय स्तर पर भारत में दूसरी आधिकारिक भाषा अंग्रेजी है। यह हिंदुस्तानी भाषा की एक मानकीकृत रूप है जिसमें संस्कृत के तत्सम तथा तद्भव शब्दों का प्रयोग अधिक है और अरबी-फ़ारसी शब्द कम हैं। हिंदी संवैधानिक रूप से भारत की राजभाषा और भारत की सबसे अधिक बोली और समझी जाने वाली भाषा है। हालाँकि, हिन्दी भारत की राष्ट्रभाषा नहीं है,[3] क्योंकि भारत के संविधान में कोई भी भाषा को ऐसा दर्जा नहीं दिया गया था।[4][5] चीनी के बाद यह विश्व में सबसे अधिक बोली जाने वाली भाषा भी है। विश्व आर्थिक मंच की गणना के अनुसार यह विश्व की दस शक्तिशाली भाषाओं में से एक है।[6]'),
        ('kn', 'ದ್ರಾವಿಡ ಭಾಷೆಗಳಲ್ಲಿ ಪ್ರಾಮುಖ್ಯವುಳ್ಳ ಭಾಷೆಯೂ ಭಾರತದ ಪುರಾತನವಾದ ಭಾಷೆಗಳಲ್ಲಿ ಒಂದೂ ಆಗಿರುವ ಕನ್ನಡ ಭಾಷೆಯನ್ನು ಅದರ ವಿವಿಧ ರೂಪಗಳಲ್ಲಿ ಸುಮಾರು ೪೫ ದಶಲಕ್ಷ ಜನರು ಆಡು ನುಡಿಯಾಗಿ ಬಳಸುತ್ತಲಿದ್ದಾರೆ. ಕನ್ನಡ ಕರ್ನಾಟಕ ರಾಜ್ಯದ ಆಡಳಿತ ಭಾಷೆ.[೧೧] ಜಗತ್ತಿನಲ್ಲಿ ಅತ್ಯಂತ ಹೆಚ್ಚು ಮಂದಿ ಮಾತನಾಡುವ ಭಾಷೆಯೆಂಬ ನೆಲೆಯಲ್ಲಿ ಇಪ್ಪತೊಂಬತ್ತನೆಯ ಸ್ಥಾನ ಕನ್ನಡಕ್ಕಿದೆ. ೨೦೧೧ರ ಜನಗಣತಿಯ ಪ್ರಕಾರ ಜಗತ್ತಿನಲ್ಲಿ ೬.೪ ಕೋಟಿ ಜನಗಳು ಕನ್ನಡ ಮಾತನಾಡುತ್ತಾರೆ ಎಂದು ತಿಳಿದುಬಂದಿದೆ. ಇವರಲ್ಲಿ ೫.೫ ಕೋಟಿ ಜನಗಳ ಮಾತೃಭಾಷೆ ಕನ್ನಡವಾಗಿದೆ. ಬ್ರಾಹ್ಮಿ ಲಿಪಿಯಿಂದ ರೂಪುಗೊಂಡ ಕನ್ನಡ ಲಿಪಿಯನ್ನು ಉಪಯೋಗಿಸಿ ಕನ್ನಡ ಭಾಷೆಯನ್ನು ಬರೆಯಲಾಗುತ್ತದೆ. ಕನ್ನಡ ಬರಹದ ಮಾದರಿಗಳಿಗೆ ಸಾವಿರದ ಐನೂರು ವರುಷಗಳ ಚರಿತ್ರೆಯಿದೆ. ಕ್ರಿ.ಶ. ಆರನೆಯ ಶತಮಾನದ ಪಶ್ಚಿಮ ಗಂಗ ಸಾಮ್ರಾಜ್ಯದ ಕಾಲದಲ್ಲಿ [೧೨] ಮತ್ತು ಒಂಬತ್ತನೆಯ ಶತಮಾನದ ರಾಷ್ಟ್ರಕೂಟ ಸಾಮ್ರಾಜ್ಯದ ಕಾಲದಲ್ಲಿ ಹಳಗನ್ನಡ ಸಾಹಿತ್ಯ ಅತ್ಯಂತ ಹೆಚ್ಚಿನ ರಾಜಾಶ್ರಯ ಪಡೆಯಿತು.[೧೩][೧೪] ಅದಲ್ಲದೆ ಸಾವಿರ ವರುಷಗಳ ಸಾಹಿತ್ಯ ಪರಂಪರೆ ಕನ್ನಡಕ್ಕಿದೆ.[೧೫]ವಿನೋಬಾ ಭಾವೆ ಕನ್ನಡ ಲಿಪಿಯನ್ನು ಲಿಪಿಗಳ ರಾಣಿಯೆಂದು ಹೊಗಳಿದ್ದಾರೆ.[ಸೂಕ್ತ ಉಲ್ಲೇಖನ ಬೇಕು]'),
        ('si', 'ශ්‍රී ලංකාවේ ප්‍රධාන ජාතිය වන සිංහල ජනයාගේ මව් බස සිංහල වෙයි. අද වන විට මිලියන 20 කට අධික සිංහල සහ මිලියන 3කට අධික සිංහල නොවන ජනගහනයක් සිංහල භාෂාව භාවිත කරති. සිංහල‍ ඉන්දු-යුරෝපීය භාෂාවල උප ගණයක් වන ඉන්දු-ආර්ය භාෂා ගණයට අයිති වන අතර මාල දිවයින භාවිත කරන දිවෙහි භාෂාව සිංහලයෙන් පැවත එන්නකි. සිංහල ශ්‍රී ලංකාවේ නිල භාෂාවයි .'),
        ('ta', 'தமிழ் மொழி (Tamil language) தமிழர்களினதும், தமிழ் பேசும் பலரதும் தாய்மொழி ஆகும். தமிழ் திராவிட மொழிக் குடும்பத்தின் முதன்மையான மொழிகளில் ஒன்றும் செம்மொழியும் ஆகும். இந்தியா, இலங்கை, மலேசியா, சிங்கப்பூர் ஆகிய நாடுகளில் அதிக அளவிலும், ஐக்கிய அரபு அமீரகம், தென்னாப்பிரிக்கா, மொரிசியசு, பிஜி, ரீயூனியன், டிரினிடாட் போன்ற நாடுகளில் சிறிய அளவிலும் தமிழ் பேசப்படுகிறது. 1997ஆம் ஆண்டுப் புள்ளி விவரப்படி உலகம் முழுவதிலும் 8 கோடி (80 மில்லியன்) மக்களால் பேசப்படும் தமிழ்[13], ஒரு மொழியைத் தாய்மொழியாகக் கொண்டு பேசும் மக்களின் எண்ணிக்கை அடிப்படையில் பதினெட்டாவது இடத்தில் உள்ளது.[14] இணையத்தில் அதிகம் பயன்படுத்தப்படும் இந்திய மொழிகளில் தமிழ் முதன்மையாக உள்ளதாக 2017 ஆவது ஆண்டில் நடைபெற்ற கூகுள் கணக்கெடுப்பில் தெரிய வந்தது.[15]'),
        ('te', 'ఆంధ్ర ప్రదేశ్, తెలంగాణ రాష్ట్రాల అధికార భాష తెలుగు. భారత దేశంలో తెలుగు మాతృభాషగా మాట్లాడే 8.7 కోట్ల (2001) జనాభాతో [1] ప్రాంతీయ భాషలలో మొదటి స్థానంలో ఉంది. ప్రపంచంలోని ప్రజలు అత్యధికముగా మాట్లాడే భాషలలో 15 స్థానములోనూ, భారత దేశములో హిందీ, తర్వాత స్థానములోనూ నిలుస్తుంది. పాతవైన ప్రపంచ భాష గణాంకాల (ఎథ్నోలాగ్) ప్రకారం ప్రపంచవ్యాప్తంగా 7.4 కోట్లు మందికి మాతృభాషగా ఉంది.[2] మొదటి భాషగా మాట్లాడతారు. అతి ప్రాచీన దేశ భాషలలో సంస్కృతము తమిళముతో బాటు తెలుగు భాషను 2008 అక్టోబరు 31న భారత ప్రభుత్వము గుర్తించింది.'),
        ('ur', 'اُردُو لشکری زبان[8] (یا جدید معیاری اردو) برصغیر کی معیاری زبانوں میں سے ایک ہے۔ یہ پاکستان کی قومی اور رابطہ عامہ کی زبان ہے، جبکہ بھارت کی چھے ریاستوں کی دفتری زبان کا درجہ رکھتی ہے۔ آئین ہند کے مطابق اسے 22 دفتری شناخت زبانوں میں شامل کیا جاچکا ہے۔ 2001ء کی مردم شماری کے مطابق اردو کو بطور مادری زبان بھارت میں 5.01% فیصد لوگ بولتے ہیں اور اس لحاظ سے یہ بھارت کی چھٹی بڑی زبان ہے جبکہ پاکستان میں اسے بطور مادری زبان 7.59% فیصد لوگ استعمال کرتے ہیں، یہ پاکستان کی پانچویں بڑی زبان ہے۔ اردو تاریخی طور پر ہندوستان کی مسلم آبادی سے جڑی ہے۔[حوالہ درکار] بعض ذخیرہ الفاظ کے علاوہ یہ زبان معیاری ہندی سے قابل فہم ہے جو اس خطے کی ہندوؤں سے منسوب ہے۔[حوالہ درکار] زبانِ اردو کو پہچان و ترقی اس وقت ملی جب برطانوی دور میں انگریز حکمرانوں نے اسے فارسی کی بجائے انگریزی کے ساتھ شمالی ہندوستان کے علاقوں اور جموں و کشمیر میں اسے سنہ 1846ء اور پنجاب میں سنہ 1849ء میں بطور دفتری زبان نافذ کیا۔ اس کے علاوہ خلیجی، یورپی، ایشیائی اور امریکی علاقوں میں اردو بولنے والوں کی ایک بڑی تعداد آباد ہے جو بنیادی طور پر جنوبی ایشیاء سے کوچ کرنے والے اہلِ اردو ہیں۔ 1999ء کے اعداد وشمار کے مطابق اردو زبان کے مجموعی متکلمین کی تعداد دس کروڑ ساٹھ لاکھ کے لگ بھگ تھی۔ اس لحاظ سے یہ دنیا کی نویں بڑی زبان ہے۔'),
    ],
    # fmt: on
)
def test_sentencizer_across_scripts(lang, text):
    nlp = spacy.blank(lang)
    nlp.add_pipe("sentencizer")
    doc = nlp(text)
    assert len(list(doc.sents)) > 1
