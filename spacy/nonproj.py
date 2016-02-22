

def ancestors(word, heads):
    # returns all words going from the word up the path to the root
    # the path to root cannot be longer than the number of words in the sentence
    # this function ends after at most len(heads) steps 
    # because it would otherwise loop indefinitely on cycles
    head = word
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
    for word in range(len(heads)):
        seen = set([word])
        for ancestor in ancestors(word,heads):
            if ancestor in seen:
                return seen
            seen.add(ancestor)
    return None


def is_non_projective_arc(word, heads):
    # definition (e.g. Havelka 2007): an arc h -> d, h < d is non-projective
    # if there is a word k, h < k < d such that h is not
    # an ancestor of k. Same for h -> d, h > d
    head = heads[word]
    if head == word: # root arcs cannot be non-projective
        return False
    elif head == None: # unattached tokens cannot be non-projective
        return False

    start, end = (head+1, word) if head < word else (word+1, head)
    for k in range(start,end):
        for ancestor in ancestors(k,heads):
            if ancestor == None: # for unattached tokens/subtrees
                break
            elif ancestor == head: # normal case: k dominated by h
                break
        else: # head not in ancestors: d -> h is non-projective
            return True
    return False


def is_non_projective_tree(heads):
    # a tree is non-projective if at least one arc is non-projective
    return any( is_non_projective_arc(word,heads) for word in range(len(heads)) )

