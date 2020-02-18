# fmt: off
consonants = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "z"]
broad_vowels = ["a", "á", "o", "ó", "u", "ú"]
slender_vowels = ["e", "é", "i", "í"]
vowels = broad_vowels + slender_vowels
# fmt: on


def ends_dentals(word):
    if word != "" and word[-1] in ["d", "n", "t", "s"]:
        return True
    else:
        return False


def devoice(word):
    if len(word) > 2 and word[-2] == "s" and word[-1] == "d":
        return word[:-1] + "t"
    else:
        return word


def ends_with_vowel(word):
    return word != "" and word[-1] in vowels


def starts_with_vowel(word):
    return word != "" and word[0] in vowels


def deduplicate(word):
    if len(word) > 2 and word[-2] == word[-1] and word[-1] in consonants:
        return word[:-1]
    else:
        return word
