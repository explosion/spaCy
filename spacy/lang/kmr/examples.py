"""
Example sentences to test spaCy and its language models.

>>> from spacy.lang.kmr.examples import sentences
>>> docs = nlp.pipe(sentences)
"""

sentences = [
    "Berê mirovan her tim li geşedana pêşerojê ye",  # People's gaze is always on the development of the future
    "Kawa Nemir di 14 salan de Ulysses wergerand Kurmancî.",  # Kawa Nemir translated Ulysses into Kurmanji in 14 years.
    "Mem Ararat hunermendekî Kurd yê bi nav û deng e.",  # Mem Ararat is a famous Kurdish artist
    "Firat Cewerî 40 sal e pirtûkên Kurdî dinivîsîne.",  # Firat Ceweri has been writing Kurdish books for 40 years
    "Rojnamegerê ciwan nûçeyeke balkêş li ser rewşa aborî nivîsand",  # The young journalist wrote an interesting news article about the economic situation
    "Sektora çandiniyê beşeke giring a belavkirina gaza serayê li seranserê cîhanê pêk tîne",  # The agricultural sector constitutes an important part of greenhouse gas emissions worldwide
    "Xwendekarên jêhatî di pêşbaziya matematîkê de serkeftî bûn",  # Talented students succeeded in the mathematics competition
    "Ji ber ji tunebûnê bavê min xwişkeke min nedan xwendin ew ji min re bû derd û kulek.",  # Because of poverty, my father didn't send my sister to school, which became a pain and sorrow for me
]
