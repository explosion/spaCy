import pytest
from spacy.lang.ta import Tamil

# Wikipedia excerpt: https://en.wikipedia.org/wiki/Chennai (Tamil Language)
TAMIL_BASIC_TOKENIZER_SENTENCIZER_TEST_TEXT = """சென்னை (Chennai) தமிழ்நாட்டின் தலைநகரமும், இந்தியாவின் நான்காவது பெரிய நகரமும் ஆகும். 1996 ஆம் ஆண்டுக்கு முன்னர் இந்நகரம், மதராசு பட்டினம், மெட்ராஸ் (Madras) மற்றும் சென்னப்பட்டினம் என்றும் அழைக்கப்பட்டு வந்தது. சென்னை, வங்காள விரிகுடாவின் கரையில் அமைந்த துறைமுக நகரங்களுள் ஒன்று. சுமார் 10 மில்லியன் (ஒரு கோடி) மக்கள் வாழும் இந்நகரம், உலகின் 35 பெரிய மாநகரங்களுள் ஒன்று. 17ஆம் நூற்றாண்டில் ஆங்கிலேயர் சென்னையில் கால் பதித்தது முதல், சென்னை நகரம் ஒரு முக்கிய நகரமாக வளர்ந்து வந்திருக்கிறது. சென்னை தென்னிந்தியாவின் வாசலாகக் கருதப்படுகிறது. சென்னை நகரில் உள்ள மெரினா கடற்கரை உலகின் நீளமான கடற்கரைகளுள் ஒன்று. சென்னை கோலிவுட் (Kollywood) என அறியப்படும் தமிழ்த் திரைப்படத் துறையின் தாயகம் ஆகும். பல விளையாட்டு அரங்கங்கள் உள்ள சென்னையில் பல விளையாட்டுப் போட்டிகளும் நடைபெறுகின்றன."""


@pytest.mark.parametrize(
    "text, num_tokens",
    [(TAMIL_BASIC_TOKENIZER_SENTENCIZER_TEST_TEXT, 23 + 90)],  # Punctuation + rest
)
def test_long_text(ta_tokenizer, text, num_tokens):
    tokens = ta_tokenizer(text)
    assert len(tokens) == num_tokens


@pytest.mark.parametrize(
    "text, num_sents", [(TAMIL_BASIC_TOKENIZER_SENTENCIZER_TEST_TEXT, 9)]
)
def test_ta_sentencizer(text, num_sents):
    nlp = Tamil()
    nlp.add_pipe("sentencizer")

    doc = nlp(text)
    assert len(list(doc.sents)) == num_sents
