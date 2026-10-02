ADPS = {
    "'n",
    "ag",
    "am",
    "ar",
    "arnaf",
    "at",
    "dan",
    "dros",
    "drwy",
    "gan",
    "gyda",
    "heb",
    "hyd",
    "i",
    "mewn",
    "o",
    "tros",
    "wedi",
    "wrth",
    "ym",
    "yn",
    "yng",
    "â",
}

ADVS = {
    "beth",
    "ble",
    "llawer",
    "lle",
    "yma",
    "yna",
}

AUXS = {
    "bod",
    "byddaf",
    "mae",
    "sy",
    "sydd",
    "ydwyf",
    "yw",
}

# Also content words: "maen" (a stone), "oes" (an age).
AMBIGS = {
    "maen",
    "oes",
}

CONJS = {
    "a",
    "ac",
    "fel",
    "neu",
    "ond",
    "os",
    "tra",
}

DETS = {
    "'r",
    "un",
    "y",
    "yr",
}

NOUNS = {
    "ôl",
    "tu",
}

PARTS = {
    "na",
    "nid",
    "nis",
}

PRONS = {
    "di",
    "dy",
    "ef",
    "ei",
    "eich",
    "ein",
    "eu",
    "fe",
    "fy",
    "hi",
    "hun",
    "hwy",
    "hyn",
    "i",
    "nhw",
    "ni",
    "pob",
}

STOP_WORDS = set(ADPS | ADVS | AUXS | AMBIGS | CONJS | DETS | NOUNS | PARTS | PRONS)
