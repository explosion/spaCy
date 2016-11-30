from __future__ import unicode_literals
from copy import copy

from ..tokens.doc cimport Doc
from spacy.attrs import DEP, HEAD


def ancestors(tokenid, heads):
    # returns all words going from the word up the path to the root
    # the path to root cannot be longer than the number of words in the sentence
    # this function ends after at most len(heads) steps 
    # because it would otherwise loop indefinitely on cycles
    head = tokenid
    cnt = 0
    while heads[head] != head and cnt < len(heads):
        head = heads[head]
        cnt += 1
        yield head
        if head == None:
            break


def contains_cycle(heads):
    # in an acyclic tree, the path from each word following
    # the head relation upwards always ends at the root node
    for tokenid in range(len(heads)):
        seen = set([tokenid])
        for ancestor in ancestors(tokenid,heads):
            if ancestor in seen:
                return seen
            seen.add(ancestor)
    return None


def is_nonproj_arc(tokenid, heads):
    # definition (e.g. Havelka 2007): an arc h -> d, h < d is non-projective
    # if there is a token k, h < k < d such that h is not
    # an ancestor of k. Same for h -> d, h > d
    head = heads[tokenid]
    if head == tokenid: # root arcs cannot be non-projective
        return False
    elif head == None: # unattached tokens cannot be non-projective
        return False

    start, end = (head+1, tokenid) if head < tokenid else (tokenid+1, head)
    for k in range(start,end):
        for ancestor in ancestors(k,heads):
            if ancestor == None: # for unattached tokens/subtrees
                break
            elif ancestor == head: # normal case: k dominated by h
                break
        else: # head not in ancestors: d -> h is non-projective
            return True
    return False


def is_nonproj_tree(heads):
    # a tree is non-projective if at least one arc is non-projective
    return any( is_nonproj_arc(word,heads) for word in range(len(heads)) )


class PseudoProjectivity:
    # implements the projectivize/deprojectivize mechanism in Nivre & Nilsson 2005
    # for doing pseudo-projective parsing
    # implementation uses the HEAD decoration scheme

    delimiter = '||'

    @classmethod
    def decompose(cls, label):
        return label.partition(cls.delimiter)[::2]

    @classmethod
    def is_decorated(cls, label):
        return label.find(cls.delimiter) != -1

    @classmethod
    def preprocess_training_data(cls, gold_tuples, label_freq_cutoff=30):
        preprocessed = []
        freqs = {}
        for raw_text, sents in gold_tuples:
            prepro_sents = []
            for (ids, words, tags, heads, labels, iob), ctnts in sents:
                proj_heads,deco_labels = cls.projectivize(heads,labels)
                # set the label to ROOT for each root dependent
                deco_labels = [ 'ROOT' if head == i else deco_labels[i] for i,head in enumerate(proj_heads) ]
                # count label frequencies
                if label_freq_cutoff > 0:
                    for label in deco_labels:
                        if cls.is_decorated(label):
                            freqs[label] = freqs.get(label,0) + 1
                prepro_sents.append(((ids,words,tags,proj_heads,deco_labels,iob), ctnts))
            preprocessed.append((raw_text, prepro_sents))

        if label_freq_cutoff > 0:
            return cls._filter_labels(preprocessed,label_freq_cutoff,freqs)
        return preprocessed


    @classmethod
    def projectivize(cls, heads, labels):
        # use the algorithm by Nivre & Nilsson 2005
        # assumes heads to be a proper tree, i.e. connected and cycle-free
        # returns a new pair (heads,labels) which encode
        # a projective and decorated tree
        proj_heads = copy(heads)
        smallest_np_arc = cls._get_smallest_nonproj_arc(proj_heads)
        if smallest_np_arc == None: # this sentence is already projective
            return proj_heads, copy(labels)
        while smallest_np_arc != None:
            cls._lift(smallest_np_arc, proj_heads)
            smallest_np_arc = cls._get_smallest_nonproj_arc(proj_heads)
        deco_labels = cls._decorate(heads, proj_heads, labels)
        return proj_heads, deco_labels


    @classmethod
    def deprojectivize(cls, tokens):
        # reattach arcs with decorated labels (following HEAD scheme)
        # for each decorated arc X||Y, search top-down, left-to-right,
        # breadth-first until hitting a Y then make this the new head
        #parse = tokens.to_array([HEAD, DEP])
        for token in tokens:
            if cls.is_decorated(token.dep_):
                newlabel,headlabel = cls.decompose(token.dep_)
                newhead = cls._find_new_head(token,headlabel)
                token.head = newhead
                token.dep_ = newlabel

                # tokens.attach(token,newhead,newlabel)
                #parse[token.i,1] = tokens.vocab.strings[newlabel]
                #parse[token.i,0] = newhead.i - token.i
        #tokens.from_array([HEAD, DEP],parse)


    @classmethod
    def _decorate(cls, heads, proj_heads, labels):
        # uses decoration scheme HEAD from Nivre & Nilsson 2005
        assert(len(heads) == len(proj_heads) == len(labels))
        deco_labels = []
        for tokenid,head in enumerate(heads):
            if head != proj_heads[tokenid]:
                deco_labels.append('%s%s%s' % (labels[tokenid],cls.delimiter,labels[head]))
            else:
                deco_labels.append(labels[tokenid])
        return deco_labels


    @classmethod
    def _get_smallest_nonproj_arc(cls, heads):
        # return the smallest non-proj arc or None
        # where size is defined as the distance between dep and head
        # and ties are broken left to right
        smallest_size = float('inf')
        smallest_np_arc = None
        for tokenid,head in enumerate(heads):
            size = abs(tokenid-head)
            if size < smallest_size and is_nonproj_arc(tokenid,heads):
                smallest_size = size
                smallest_np_arc = tokenid
        return smallest_np_arc


    @classmethod
    def _lift(cls, tokenid, heads):
        # reattaches a word to it's grandfather
        head = heads[tokenid]
        ghead = heads[head]
        # attach to ghead if head isn't attached to root else attach to root
        heads[tokenid] = ghead if head != ghead else tokenid


    @classmethod
    def _find_new_head(cls, token, headlabel):
        # search through the tree starting from the head of the given token
        # returns the id of the first descendant with the given label
        # if there is none, return the current head (no change)
        queue = [token.head]
        while queue:
            next_queue = []
            for qtoken in queue:
                for child in qtoken.children:
                    if child.is_space: continue                        
                    if child == token: continue
                    if child.dep_ == headlabel:
                        return child
                    next_queue.append(child)
            queue = next_queue
        return token.head


    @classmethod
    def _filter_labels(cls, gold_tuples, cutoff, freqs):
        # throw away infrequent decorated labels
        # can't learn them reliably anyway and keeps label set smaller
        filtered = []
        for raw_text, sents in gold_tuples:
            filtered_sents = []
            for (ids, words, tags, heads, labels, iob), ctnts in sents:
                filtered_labels = [ cls.decompose(label)[0] if freqs.get(label,cutoff) < cutoff else label for label in labels ]
                filtered_sents.append(((ids,words,tags,heads,filtered_labels,iob), ctnts))
            filtered.append((raw_text, filtered_sents))
        return filtered


