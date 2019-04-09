import re
import time
import sre_yield
import string
from ...char_classes import LATIN_LOWER

# ALPHABET_SIZE = ord('z') - ord('a') + 1 + len(polish_special_chars)
charset = LATIN_LOWER.encode().decode('unicode-escape')
ALPHABET_SIZE = len(charset)

idx_map = {}
for i, char in enumerate(LATIN_LOWER):
    idx_map[char] = i

def reverse(string):
    return "".join(reversed(string))

def get_idx(c):
    print(charset)
    return charset.index(c)
    # return idx_map[c]

class Trie:
    def __init__(self):
        self.root = Node()

    def insert(self, word, rule):
        self.root.insert(word, rule)

    def get_rules(self, word):
        return self.root.get_rules(word)


class Node:
    def __init__(self):
        self.is_end = False
        self.children = ALPHABET_SIZE*[None]
        self.rules = []

    def insert(self, word, rule):
        if word == "":
            self.is_end = True
            self.rules += [rule]
        else:
            child = self.children[get_idx(word[0])]
            if child is None:
                child = Node()
                self.children[get_idx(word[0])] = child
            child.insert(word[1:], rule)

    def get_rules(self, word):
        res = []
        if self.is_end:
            res += [self.rules]
        if word == "":
            return res
        head = word[-1]
        tail = word[:-1]
        if self.children[get_idx(head)] is None:
            return res
        return res + self.children[get_idx(head)].get_rules(tail)

def trie_from_rules(rules):
    # rules are expected to be in format:
    # [(suffix, (regex, replacement))]
    expanded_rules = []
    for rule in rules:
        new_suf = rule[0]
        prefixes = list(sre_yield.AllStrings(rule[0], charset=charset))
        expanded_rules += [(pref, rule[0], new_suf) for pref in prefixes]

    trie = Trie()
    for suf, regexp, rule in expanded_rules:
        trie.insert(reverse(suf), (regexp, rule))

    return trie




