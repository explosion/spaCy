#!/usr/bin/env python
# flake8: noqa

# CoNLL 2017 UD Parsing evaluation script.
#
# Compatible with Python 2.7 and 3.2+, can be used either as a module
# or a standalone executable.
#
# Copyright 2017 Institute of Formal and Applied Linguistics (UFAL),
# Faculty of Mathematics and Physics, Charles University, Czech Republic.
#
# Changelog:
# - [02 Jan 2017] Version 0.9: Initial release
# - [25 Jan 2017] Version 0.9.1: Fix bug in LCS alignment computation
# - [10 Mar 2017] Version 1.0: Add documentation and test
#                              Compare HEADs correctly using aligned words
#                              Allow evaluation with errorneous spaces in forms
#                              Compare forms in LCS case insensitively
#                              Detect cycles and multiple root nodes
#                              Compute AlignedAccuracy

# Command line usage
# ------------------
# conll17_ud_eval.py [-v] [-w weights_file] gold_conllu_file system_conllu_file
#
# - if no -v is given, only the CoNLL17 UD Shared Task evaluation LAS metrics
#   is printed
# - if -v is given, several metrics are printed (as precision, recall, F1 score,
#   and in case the metric is computed on aligned words also accuracy on these):
#   - Tokens: how well do the gold tokens match system tokens
#   - Sentences: how well do the gold sentences match system sentences
#   - Words: how well can the gold words be aligned to system words
#   - UPOS: using aligned words, how well does UPOS match
#   - XPOS: using aligned words, how well does XPOS match
#   - Feats: using aligned words, how well does FEATS match
#   - AllTags: using aligned words, how well does UPOS+XPOS+FEATS match
#   - Lemmas: using aligned words, how well does LEMMA match
#   - UAS: using aligned words, how well does HEAD match
#   - LAS: using aligned words, how well does HEAD+DEPREL(ignoring subtypes) match
# - if weights_file is given (with lines containing deprel-weight pairs),
#   one more metric is shown:
#   - WeightedLAS: as LAS, but each deprel (ignoring subtypes) has different weight

# API usage
# ---------
# - load_conllu(file)
#   - loads CoNLL-U file from given file object to an internal representation
#   - the file object should return str on both Python 2 and Python 3
#   - raises UDError exception if the given file cannot be loaded
# - evaluate(gold_ud, system_ud)
#   - evaluate the given gold and system CoNLL-U files (loaded with load_conllu)
#   - raises UDError if the concatenated tokens of gold and system file do not match
#   - returns a dictionary with the metrics described above, each metrics having
#     four fields: precision, recall, f1 and aligned_accuracy (when using aligned
#     words, otherwise this is None)

# Description of token matching
# -----------------------------
# In order to match tokens of gold file and system file, we consider the text
# resulting from concatenation of gold tokens and text resulting from
# concatenation of system tokens. These texts should match -- if they do not,
# the evaluation fails.
#
# If the texts do match, every token is represented as a range in this original
# text, and tokens are equal only if their range is the same.

# Description of word matching
# ----------------------------
# When matching words of gold file and system file, we first match the tokens.
# The words which are also tokens are matched as tokens, but words in multi-word
# tokens have to be handled differently.
#
# To handle multi-word tokens, we start by finding "multi-word spans".
# Multi-word span is a span in the original text such that
# - it contains at least one multi-word token
# - all multi-word tokens in the span (considering both gold and system ones)
#   are completely inside the span (i.e., they do not "stick out")
# - the multi-word span is as small as possible
#
# For every multi-word span, we align the gold and system words completely
# inside this span using LCS on their FORMs. The words not intersecting
# (even partially) any multi-word span are then aligned as tokens.


from __future__ import division
from __future__ import print_function

import argparse
import io
import sys
import unittest

# CoNLL-U column names
ID, FORM, LEMMA, UPOS, XPOS, FEATS, HEAD, DEPREL, DEPS, MISC = range(10)

# UD Error is used when raising exceptions in this module
class UDError(Exception):
    pass

# Load given CoNLL-U file into internal representation
def load_conllu(file, check_parse=True):
    # Internal representation classes
    class UDRepresentation:
        def __init__(self):
            # Characters of all the tokens in the whole file.
            # Whitespace between tokens is not included.
            self.characters = []
            # List of UDSpan instances with start&end indices into `characters`.
            self.tokens = []
            # List of UDWord instances.
            self.words = []
            # List of UDSpan instances with start&end indices into `characters`.
            self.sentences = []
    class UDSpan:
        def __init__(self, start, end, characters):
            self.start = start
            # Note that self.end marks the first position **after the end** of span,
            # so we can use characters[start:end] or range(start, end).
            self.end = end
            self.characters = characters

        @property
        def text(self):
            return ''.join(self.characters[self.start:self.end])

        def __str__(self):
            return self.text

        def __repr__(self):
            return self.text
    class UDWord:
        def __init__(self, span, columns, is_multiword):
            # Span of this word (or MWT, see below) within ud_representation.characters.
            self.span = span
            # 10 columns of the CoNLL-U file: ID, FORM, LEMMA,...
            self.columns = columns
            # is_multiword==True means that this word is part of a multi-word token.
            # In that case, self.span marks the span of the whole multi-word token.
            self.is_multiword = is_multiword
            # Reference to the UDWord instance representing the HEAD (or None if root).
            self.parent = None
            # Let's ignore language-specific deprel subtypes.
            self.columns[DEPREL] = columns[DEPREL].split(':')[0]

    ud = UDRepresentation()

    # Load the CoNLL-U file
    index, sentence_start = 0, None
    linenum = 0
    while True:
        line = file.readline()
        linenum += 1
        if not line:
            break
        line = line.rstrip("\r\n")

        # Handle sentence start boundaries
        if sentence_start is None:
            # Skip comments
            if line.startswith("#"):
                continue
            # Start a new sentence
            ud.sentences.append(UDSpan(index, 0, ud.characters))
            sentence_start = len(ud.words)
        if not line:
            # Add parent UDWord links and check there are no cycles
            def process_word(word):
                if word.parent == "remapping":
                    raise UDError("There is a cycle in a sentence")
                if word.parent is None:
                    head = int(word.columns[HEAD])
                    if head > len(ud.words) - sentence_start:
                        raise UDError("Line {}: HEAD '{}' points outside of the sentence".format(
                            linenum, word.columns[HEAD]))
                    if head:
                        parent = ud.words[sentence_start + head - 1]
                        word.parent = "remapping"
                        process_word(parent)
                        word.parent = parent

            for word in ud.words[sentence_start:]:
                process_word(word)

            # Check there is a single root node
            if check_parse:
                if len([word for word in ud.words[sentence_start:] if word.parent is None]) != 1:
                    raise UDError("There are multiple roots in a sentence")

            # End the sentence
            ud.sentences[-1].end = index
            sentence_start = None
            continue

        # Read next token/word
        columns = line.split("\t")
        if len(columns) != 10:
            raise UDError("The CoNLL-U line {} does not contain 10 tab-separated columns: '{}'".format(linenum, line))

        # Skip empty nodes
        if "." in columns[ID]:
            continue

        # Delete spaces from FORM so gold.characters == system.characters
        # even if one of them tokenizes the space.
        columns[FORM] = columns[FORM].replace(" ", "")
        if not columns[FORM]:
            raise UDError("There is an empty FORM in the CoNLL-U file -- line %d" % linenum)

        # Save token
        ud.characters.extend(columns[FORM])
        ud.tokens.append(UDSpan(index, index + len(columns[FORM]), ud.characters))
        index += len(columns[FORM])

        # Handle multi-word tokens to save word(s)
        if "-" in columns[ID]:
            try:
                start, end = map(int, columns[ID].split("-"))
            except:
                raise UDError("Cannot parse multi-word token ID '{}'".format(columns[ID]))

            for _ in range(start, end + 1):
                word_line = file.readline().rstrip("\r\n")
                word_columns = word_line.split("\t")
                if len(word_columns) != 10:
                    print(columns)
                    raise UDError("The CoNLL-U line {} does not contain 10 tab-separated columns: '{}'".format(linenum, word_line))
                ud.words.append(UDWord(ud.tokens[-1], word_columns, is_multiword=True))
        # Basic tokens/words
        else:
            try:
                word_id = int(columns[ID])
            except:
                raise UDError("Cannot parse word ID '{}'".format(columns[ID]))
            if word_id != len(ud.words) - sentence_start + 1:
                raise UDError("Incorrect word ID '{}' for word '{}', expected '{}'".format(columns[ID], columns[FORM], len(ud.words) - sentence_start + 1))

            try:
                head_id = int(columns[HEAD])
            except:
                raise UDError("Cannot parse HEAD '{}'".format(columns[HEAD]))
            if head_id < 0:
                raise UDError("HEAD cannot be negative")

            ud.words.append(UDWord(ud.tokens[-1], columns, is_multiword=False))

    if sentence_start is not None:
        raise UDError("The CoNLL-U file does not end with empty line")

    return ud

# Evaluate the gold and system treebanks (loaded using load_conllu).
def evaluate(gold_ud, system_ud, deprel_weights=None, check_parse=True):
    class Score:
        def __init__(self, gold_total, system_total, correct, aligned_total=None, undersegmented=None, oversegmented=None):
            self.precision = correct / system_total if system_total else 0.0
            self.recall = correct / gold_total if gold_total else 0.0
            self.f1 = 2 * correct / (system_total + gold_total) if system_total + gold_total else 0.0
            self.aligned_accuracy = correct / aligned_total if aligned_total else aligned_total
            self.undersegmented = undersegmented
            self.oversegmented = oversegmented
            self.under_perc = len(undersegmented) / gold_total if gold_total and undersegmented else 0.0
            self.over_perc = len(oversegmented) / gold_total if gold_total and oversegmented else 0.0
    class AlignmentWord:
        def __init__(self, gold_word, system_word):
            self.gold_word = gold_word
            self.system_word = system_word
            self.gold_parent = None
            self.system_parent_gold_aligned = None
    class Alignment:
        def __init__(self, gold_words, system_words):
            self.gold_words = gold_words
            self.system_words = system_words
            self.matched_words = []
            self.matched_words_map = {}
        def append_aligned_words(self, gold_word, system_word):
            self.matched_words.append(AlignmentWord(gold_word, system_word))
            self.matched_words_map[system_word] = gold_word
        def fill_parents(self):
            # We represent root parents in both gold and system data by '0'.
            # For gold data, we represent non-root parent by corresponding gold word.
            # For system data, we represent non-root parent by either gold word aligned
            # to parent system nodes, or by None if no gold words is aligned to the parent.
            for words in self.matched_words:
                words.gold_parent = words.gold_word.parent if words.gold_word.parent is not None else 0
                words.system_parent_gold_aligned = self.matched_words_map.get(words.system_word.parent, None) \
                    if words.system_word.parent is not None else 0

    def lower(text):
        if sys.version_info < (3, 0) and isinstance(text, str):
            return text.decode("utf-8").lower()
        return text.lower()

    def spans_score(gold_spans, system_spans):
        correct, gi, si = 0, 0, 0
        undersegmented = []
        oversegmented = []
        combo = 0
        previous_end_si_earlier = False
        previous_end_gi_earlier = False
        while gi < len(gold_spans) and si < len(system_spans):
            previous_si = system_spans[si-1] if si > 0 else None
            previous_gi = gold_spans[gi-1] if gi > 0 else None
            if system_spans[si].start < gold_spans[gi].start:
                # avoid counting the same mistake twice
                if not previous_end_si_earlier:
                    combo += 1
                    oversegmented.append(str(previous_gi).strip())
                si += 1
            elif gold_spans[gi].start < system_spans[si].start:
                # avoid counting the same mistake twice
                if not previous_end_gi_earlier:
                    combo += 1
                    undersegmented.append(str(previous_si).strip())
                gi += 1
            else:
                correct += gold_spans[gi].end == system_spans[si].end
                if gold_spans[gi].end < system_spans[si].end:
                    undersegmented.append(str(system_spans[si]).strip())
                    previous_end_gi_earlier = True
                    previous_end_si_earlier = False
                elif gold_spans[gi].end > system_spans[si].end:
                    oversegmented.append(str(gold_spans[gi]).strip())
                    previous_end_si_earlier = True
                    previous_end_gi_earlier = False
                else:
                    previous_end_gi_earlier = False
                    previous_end_si_earlier = False
                si += 1
                gi += 1

        return Score(len(gold_spans), len(system_spans), correct, None, undersegmented, oversegmented)

    def alignment_score(alignment, key_fn, weight_fn=lambda w: 1):
        gold, system, aligned, correct = 0, 0, 0, 0

        for word in alignment.gold_words:
            gold += weight_fn(word)

        for word in alignment.system_words:
            system += weight_fn(word)

        for words in alignment.matched_words:
            aligned += weight_fn(words.gold_word)

        if key_fn is None:
            # Return score for whole aligned words
            return Score(gold, system, aligned)

        for words in alignment.matched_words:
            if key_fn(words.gold_word, words.gold_parent) == key_fn(words.system_word, words.system_parent_gold_aligned):
                correct += weight_fn(words.gold_word)

        return Score(gold, system, correct, aligned)

    def beyond_end(words, i, multiword_span_end):
        if i >= len(words):
            return True
        if words[i].is_multiword:
            return words[i].span.start >= multiword_span_end
        return words[i].span.end > multiword_span_end

    def extend_end(word, multiword_span_end):
        if word.is_multiword and word.span.end > multiword_span_end:
            return word.span.end
        return multiword_span_end

    def find_multiword_span(gold_words, system_words, gi, si):
        # We know gold_words[gi].is_multiword or system_words[si].is_multiword.
        # Find the start of the multiword span (gs, ss), so the multiword span is minimal.
        # Initialize multiword_span_end characters index.
        if gold_words[gi].is_multiword:
            multiword_span_end = gold_words[gi].span.end
            if not system_words[si].is_multiword and system_words[si].span.start < gold_words[gi].span.start:
                si += 1
        else: # if system_words[si].is_multiword
            multiword_span_end = system_words[si].span.end
            if not gold_words[gi].is_multiword and gold_words[gi].span.start < system_words[si].span.start:
                gi += 1
        gs, ss = gi, si

        # Find the end of the multiword span
        # (so both gi and si are pointing to the word following the multiword span end).
        while not beyond_end(gold_words, gi, multiword_span_end) or \
              not beyond_end(system_words, si, multiword_span_end):
            if gi < len(gold_words) and (si >= len(system_words) or
                                         gold_words[gi].span.start <= system_words[si].span.start):
                multiword_span_end = extend_end(gold_words[gi], multiword_span_end)
                gi += 1
            else:
                multiword_span_end = extend_end(system_words[si], multiword_span_end)
                si += 1
        return gs, ss, gi, si

    def compute_lcs(gold_words, system_words, gi, si, gs, ss):
        lcs = [[0] * (si - ss) for i in range(gi - gs)]
        for g in reversed(range(gi - gs)):
            for s in reversed(range(si - ss)):
                if lower(gold_words[gs + g].columns[FORM]) == lower(system_words[ss + s].columns[FORM]):
                    lcs[g][s] = 1 + (lcs[g+1][s+1] if g+1 < gi-gs and s+1 < si-ss else 0)
                lcs[g][s] = max(lcs[g][s], lcs[g+1][s] if g+1 < gi-gs else 0)
                lcs[g][s] = max(lcs[g][s], lcs[g][s+1] if s+1 < si-ss else 0)
        return lcs

    def align_words(gold_words, system_words):
        alignment = Alignment(gold_words, system_words)

        gi, si = 0, 0
        while gi < len(gold_words) and si < len(system_words):
            if gold_words[gi].is_multiword or system_words[si].is_multiword:
                # A: Multi-word tokens => align via LCS within the whole "multiword span".
                gs, ss, gi, si = find_multiword_span(gold_words, system_words, gi, si)

                if si > ss and gi > gs:
                    lcs = compute_lcs(gold_words, system_words, gi, si, gs, ss)

                    # Store aligned words
                    s, g = 0, 0
                    while g < gi - gs and s < si - ss:
                        if lower(gold_words[gs + g].columns[FORM]) == lower(system_words[ss + s].columns[FORM]):
                            alignment.append_aligned_words(gold_words[gs+g], system_words[ss+s])
                            g += 1
                            s += 1
                        elif lcs[g][s] == (lcs[g+1][s] if g+1 < gi-gs else 0):
                            g += 1
                        else:
                            s += 1
            else:
                # B: No multi-word token => align according to spans.
                if (gold_words[gi].span.start, gold_words[gi].span.end) == (system_words[si].span.start, system_words[si].span.end):
                    alignment.append_aligned_words(gold_words[gi], system_words[si])
                    gi += 1
                    si += 1
                elif gold_words[gi].span.start <= system_words[si].span.start:
                    gi += 1
                else:
                    si += 1

        alignment.fill_parents()

        return alignment

    # Check that underlying character sequences do match
    if gold_ud.characters != system_ud.characters:
        index = 0
        while gold_ud.characters[index] == system_ud.characters[index]:
            index += 1

        raise UDError(
            "The concatenation of tokens in gold file and in system file differ!\n" +
            "First 20 differing characters in gold file: '{}' and system file: '{}'".format(
                "".join(gold_ud.characters[index:index + 20]),
                "".join(system_ud.characters[index:index + 20])
            )
        )

    # Align words
    alignment = align_words(gold_ud.words, system_ud.words)

    # Compute the F1-scores
    if check_parse:
        result = {
            "Tokens": spans_score(gold_ud.tokens, system_ud.tokens),
            "Sentences": spans_score(gold_ud.sentences, system_ud.sentences),
            "Words": alignment_score(alignment, None),
            "UPOS": alignment_score(alignment, lambda w, parent: w.columns[UPOS]),
            "XPOS": alignment_score(alignment, lambda w, parent: w.columns[XPOS]),
            "Feats": alignment_score(alignment, lambda w, parent: w.columns[FEATS]),
            "AllTags": alignment_score(alignment, lambda w, parent: (w.columns[UPOS], w.columns[XPOS], w.columns[FEATS])),
            "Lemmas": alignment_score(alignment, lambda w, parent: w.columns[LEMMA]),
            "UAS": alignment_score(alignment, lambda w, parent: parent),
            "LAS": alignment_score(alignment, lambda w, parent: (parent, w.columns[DEPREL])),
        }
    else:
        result = {
            "Tokens": spans_score(gold_ud.tokens, system_ud.tokens),
            "Sentences": spans_score(gold_ud.sentences, system_ud.sentences),
            "Words": alignment_score(alignment, None),
            "Feats": alignment_score(alignment, lambda w, parent: w.columns[FEATS]),
            "Lemmas": alignment_score(alignment, lambda w, parent: w.columns[LEMMA]),
        }


    # Add WeightedLAS if weights are given
    if deprel_weights is not None:
        def weighted_las(word):
            return deprel_weights.get(word.columns[DEPREL], 1.0)
        result["WeightedLAS"] = alignment_score(alignment, lambda w, parent: (parent, w.columns[DEPREL]), weighted_las)

    return result

def load_deprel_weights(weights_file):
    if weights_file is None:
        return None

    deprel_weights = {}
    for line in weights_file:
        # Ignore comments and empty lines
        if line.startswith("#") or not line.strip():
            continue

        columns = line.rstrip("\r\n").split()
        if len(columns) != 2:
            raise ValueError("Expected two columns in the UD Relations weights file on line '{}'".format(line))

        deprel_weights[columns[0]] = float(columns[1])

    return deprel_weights

def load_conllu_file(path):
    _file = open(path, mode="r", **({"encoding": "utf-8"} if sys.version_info >= (3, 0) else {}))
    return load_conllu(_file)

def evaluate_wrapper(args):
    # Load CoNLL-U files
    gold_ud = load_conllu_file(args.gold_file)
    system_ud = load_conllu_file(args.system_file)

    # Load weights if requested
    deprel_weights = load_deprel_weights(args.weights)

    return evaluate(gold_ud, system_ud, deprel_weights)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("gold_file", type=str,
                        help="Name of the CoNLL-U file with the gold data.")
    parser.add_argument("system_file", type=str,
                        help="Name of the CoNLL-U file with the predicted data.")
    parser.add_argument("--weights", "-w", type=argparse.FileType("r"), default=None,
                        metavar="deprel_weights_file",
                        help="Compute WeightedLAS using given weights for Universal Dependency Relations.")
    parser.add_argument("--verbose", "-v", default=0, action="count",
                        help="Print all metrics.")
    args = parser.parse_args()

    # Use verbose if weights are supplied
    if args.weights is not None and not args.verbose:
        args.verbose = 1

    # Evaluate
    evaluation = evaluate_wrapper(args)

    # Print the evaluation
    if not args.verbose:
        print("LAS F1 Score: {:.2f}".format(100 * evaluation["LAS"].f1))
    else:
        metrics = ["Tokens", "Sentences", "Words", "UPOS", "XPOS", "Feats", "AllTags", "Lemmas", "UAS", "LAS"]
        if args.weights is not None:
            metrics.append("WeightedLAS")

        print("Metrics    | Precision |    Recall |  F1 Score | AligndAcc")
        print("-----------+-----------+-----------+-----------+-----------")
        for metric in metrics:
            print("{:11}|{:10.2f} |{:10.2f} |{:10.2f} |{}".format(
                metric,
                100 * evaluation[metric].precision,
                100 * evaluation[metric].recall,
                100 * evaluation[metric].f1,
                "{:10.2f}".format(100 * evaluation[metric].aligned_accuracy) if evaluation[metric].aligned_accuracy is not None else ""
            ))

if __name__ == "__main__":
    main()

# Tests, which can be executed with `python -m unittest conll17_ud_eval`.
class TestAlignment(unittest.TestCase):
    @staticmethod
    def _load_words(words):
        """Prepare fake CoNLL-U files with fake HEAD to prevent multiple roots errors."""
        lines, num_words = [], 0
        for w in words:
            parts = w.split(" ")
            if len(parts) == 1:
                num_words += 1
                lines.append("{}\t{}\t_\t_\t_\t_\t{}\t_\t_\t_".format(num_words, parts[0], int(num_words>1)))
            else:
                lines.append("{}-{}\t{}\t_\t_\t_\t_\t_\t_\t_\t_".format(num_words + 1, num_words + len(parts) - 1, parts[0]))
                for part in parts[1:]:
                    num_words += 1
                    lines.append("{}\t{}\t_\t_\t_\t_\t{}\t_\t_\t_".format(num_words, part, int(num_words>1)))
        return load_conllu((io.StringIO if sys.version_info >= (3, 0) else io.BytesIO)("\n".join(lines+["\n"])))

    def _test_exception(self, gold, system):
        self.assertRaises(UDError, evaluate, self._load_words(gold), self._load_words(system))

    def _test_ok(self, gold, system, correct):
        metrics = evaluate(self._load_words(gold), self._load_words(system))
        gold_words = sum((max(1, len(word.split(" ")) - 1) for word in gold))
        system_words = sum((max(1, len(word.split(" ")) - 1) for word in system))
        self.assertEqual((metrics["Words"].precision, metrics["Words"].recall, metrics["Words"].f1),
                         (correct / system_words, correct / gold_words, 2 * correct / (gold_words + system_words)))

    def test_exception(self):
        self._test_exception(["a"], ["b"])

    def test_equal(self):
        self._test_ok(["a"], ["a"], 1)
        self._test_ok(["a", "b", "c"], ["a", "b", "c"], 3)

    def test_equal_with_multiword(self):
        self._test_ok(["abc a b c"], ["a", "b", "c"], 3)
        self._test_ok(["a", "bc b c", "d"], ["a", "b", "c", "d"], 4)
        self._test_ok(["abcd a b c d"], ["ab a b", "cd c d"], 4)
        self._test_ok(["abc a b c", "de d e"], ["a", "bcd b c d", "e"], 5)

    def test_alignment(self):
        self._test_ok(["abcd"], ["a", "b", "c", "d"], 0)
        self._test_ok(["abc", "d"], ["a", "b", "c", "d"], 1)
        self._test_ok(["a", "bc", "d"], ["a", "b", "c", "d"], 2)
        self._test_ok(["a", "bc b c", "d"], ["a", "b", "cd"], 2)
        self._test_ok(["abc a BX c", "def d EX f"], ["ab a b", "cd c d", "ef e f"], 4)
        self._test_ok(["ab a b", "cd bc d"], ["a", "bc", "d"], 2)
        self._test_ok(["a", "bc b c", "d"], ["ab AX BX", "cd CX a"], 1)
