from copy import copy
from collections import Counter

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


class PseudoProjective:
    # implements the projectivize/deprojectivize mechanism in Nivre & Nilsson 2005
    # for doing pseudo-projective parsing
    # implementation uses the HEAD decoration scheme

    def preprocess_training_data(self, labeled_trees, label_freq_cutoff=30):
        # expects a sequence of pairs of head arrays and labels
        preprocessed = []
        for heads,labels in labeled_trees:
            proj_heads,deco_labels = self.projectivize(heads,labels)
            # set the label to ROOT for each root dependent
            deco_labels = [ 'ROOT' if head == i else deco_labels[i] for i,head in enumerate(proj_heads) ]
            preprocessed.append((proj_heads,deco_labels))

        if label_freq_cutoff > 0:
            return self._filter_labels(preprocessed,label_freq_cutoff)
        return preprocessed


    def projectivize(self, heads, labels):
        # use the algorithm by Nivre & Nilsson 2005
        # assumes heads to be a proper tree, i.e. connected and cycle-free
        # returns a new pair (heads,labels) which encode
        # a projective and decorated tree
        proj_heads = copy(heads)
        smallest_np_arc = self._get_smallest_nonproj_arc(proj_heads)
        if smallest_np_arc == None: # this sentence is already projective
            return proj_heads, copy(labels)
        while smallest_np_arc != None:
            self._lift(smallest_np_arc, proj_heads)
            smallest_np_arc = self._get_smallest_nonproj_arc(proj_heads)
        deco_labels = self._decorate(heads, proj_heads, labels)
        return proj_heads, deco_labels


    def deprojectivize(self, heads, labels):
        # reattach arcs with decorated labels (following HEAD scheme)
        # for each decorated arc X||Y, search top-down, left-to-right,
        # breadth-first until hitting a Y then make this the new head
        newheads, newlabels = copy(heads), copy(labels)
        spans = None
        for tokenid, head in enumerate(heads):
            if labels[tokenid].find('||') != -1:
                newlabel,_,headlabel = labels[tokenid].partition('||')
                newhead = self._find_new_head(head,tokenid,headlabel,heads,labels,spans=spans)
                newheads[tokenid] = newhead
                newlabels[tokenid] = newlabel
        return newheads, newlabels


    def _decorate(self, heads, proj_heads, labels):
        # uses decoration scheme HEAD from Nivre & Nilsson 2005
        assert(len(heads) == len(proj_heads) == len(labels))
        deco_labels = []
        for tokenid,head in enumerate(heads):
            if head != proj_heads[tokenid]:
                deco_labels.append('%s||%s' % (labels[tokenid],labels[head]))
            else:
                deco_labels.append(labels[tokenid])
        return deco_labels


    def _get_smallest_nonproj_arc(self, heads):
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


    def _lift(self, tokenid, heads):
        # reattaches a word to it's grandfather
        head = heads[tokenid]
        ghead = heads[head]
        # attach to ghead if head isn't attached to root else attach to root
        heads[tokenid] = ghead if head != ghead else tokenid


    def _find_new_head(self, rootid, tokenid, headlabel, heads, labels, spans=None):
        # search through the tree starting from root
        # returns the id of the first descendant with the given label
        # if there is none, return the current head (no change)
        if not spans:
            spans = self._make_span_index(heads)
        queue = spans.get(rootid,[])
        queue.remove(tokenid) # don't search in the subtree of the nonproj arc
        while queue:
            next_queue = []
            for idx in queue:
                if labels[idx] == headlabel:
                    return idx
                next_queue.extend(spans.get(idx,[]))
            queue = next_queue
        return heads[tokenid]


    def _make_span_index(self, heads):
        # stores the direct dependents for each token
        # for searching top-down through a tree
        spans = {}
        for tokenid, head in enumerate(heads):
            if tokenid == head: # root
                continue
            if head not in spans:
                spans[head] = []
            spans[head].append(tokenid)
        return spans


    def _filter_labels(self, labeled_trees, cutoff):
        # throw away infrequent decorated labels
        # can't learn them reliably anyway and keeps label set smaller
        freqs = Counter([ label for _,labels in labeled_trees for label in labels if label.find('||') != -1 ])
        filtered = []
        for proj_heads,deco_labels in labeled_trees:
            filtered_labels = [ label.partition('||')[0] if freqs.get(label,cutoff) < cutoff else label for label in deco_labels ]
            filtered.append((proj_heads,filtered_labels))
        return filtered
