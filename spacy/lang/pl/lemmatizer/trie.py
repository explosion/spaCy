import re
import time
import sre_yield
import string
from ...char_classes import LATIN_LOWER

# ALPHABET_SIZE = ord('z') - ord('a') + 1 + len(polish_special_chars)
# charset = LATIN_LOWER.encode().decode('unicode-escape')
charset = string.ascii_lowercase + "ąężźćńółęąś"
ALPHABET_SIZE = len(charset)


class Trie:
    def __init__(self):
        self.root = Node()

    def insert(self, word, rule):
        self.root.insert(word, rule)

    def get_rules(self, word):
        return self.root.get_rules(word)

    def __contains__(self, word):
        return word in self.root


class Node:
    def __init__(self):
        self.is_end = False
        self.children = {}
        self.rules = []

    def insert(self, word, rule):
        if word == "":
            self.is_end = True
            self.rules += [rule]
        else:
            child = self.children.get(word[-1])
            if child is None:
                child = Node()
                self.children[word[-1]] = child
            child.insert(word[:-1], rule)

    def get_rules(self, word):
        res = []
        if self.is_end:
            res += [self.rules]
        if word == "":
            return res
        head = word[-1]
        tail = word[:-1]
        if self.children.get(head) is None:
            return res
        return res + self.children[head].get_rules(tail)

    def __contains__(self, word):
        if word == "":
            return self.is_end
        head = word[-1]
        tail = word[:-1]
        if self.children.get(head) is None:
            return False
        return tail in self.children[head]


def trie_from_rules(rules):
    # rules are expected to be in format:
    # [(suffix, (regex, replacement))]
    expanded_rules = []
    for rule in rules:
        replacement = rule[1]
        regex = rule[0]
        suffixes = list(sre_yield.AllStrings(rule[0], charset=charset))
        expanded_rules += [(suf, regex, replacement) for suf in suffixes]

    trie = Trie()
    for suf, regex, replacement in expanded_rules:
        trie.insert(suf, (regex, replacement))

    return trie


def trie_from_words(words):
    trie = Trie()
    for word in words:
        trie.insert(word, None)

    return trie
