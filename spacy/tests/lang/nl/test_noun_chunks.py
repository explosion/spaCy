import pytest


def test_need_dep(nl_tokenizer):
    """
    Test that noun_chunks raises Value Error for 'nl' language if Doc is not parsed.
    """
    txt = "Haar vriend lacht luid."
    doc = nl_tokenizer(txt)

    with pytest.raises(ValueError):
        list(doc.noun_chunks)


def test_chunking(nl_tokenizer):
    """
    Test the noun chunks of a sample text. Uses a sample.
    The sample text was made as a Doc object with nl_core_news_md loaded. The Doc object was serialized with
    the to_bytes() method.
    """
    # TEXT :
    # Haar vriend lacht luid. We kregen alweer ruzie toen we de supermarkt ingingen.
    # Aan het begin van de supermarkt is al het fruit en de groentes. Uiteindelijk hebben we dan ook
    # geen avondeten gekocht.
    # Using frog https://github.com/LanguageMachines/frog/ we obtain the following NOUN-PHRASES:
    # fmt: off
    expected = ["haar vriend", "we", "ruzie", "we", "de supermarkt", "het begin", "de supermarkt", "het fruit",
                "de groentes", "we", "geen avondeten"]

    doc = nl_tokenizer("")
    with open("sample.bin", "rb") as src:
        doc.from_bytes(src.read())

    chunks = [s.text.lower() for s in doc.noun_chunks]

    assert chunks == expected
