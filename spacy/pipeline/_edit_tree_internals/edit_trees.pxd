from libc.stdint cimport uint32_t, uint64_t
from libcpp.unordered_map cimport unordered_map
from libcpp.vector cimport vector

from ...strings cimport StringStore
from ...typedefs cimport attr_t, hash_t, len_t


cdef extern from "<algorithm>" namespace "std" nogil:
    void swap[T](T& a, T& b) except +  # Only available in Cython 3.

# An edit tree (Müller et al., 2015) is a tree structure that consists of
# edit operations. The two types of operations are string matches
# and string substitutions. Given an input string s and an output string t,
# subsitution and match nodes should be interpreted as follows:
#
# * Substitution node: consists of an original string and substitute string.
#   If s matches the original string, then t is the substitute. Otherwise,
#   the node does not apply.
# * Match node: consists of a prefix length, suffix length, prefix edit tree,
#   and suffix edit tree. If s is composed of a prefix, middle part, and suffix
#   with the given suffix and prefix lengths, then t is the concatenation
#   prefix_tree(prefix) + middle + suffix_tree(suffix).
#
# For efficiency, we represent strings in substitution nodes as integers, with
# the actual strings stored in a StringStore. Subtrees in match nodes are stored
# as tree identifiers (rather than pointers) to simplify serialization.

cdef uint32_t NULL_TREE_ID

cdef struct MatchNodeC:
    len_t prefix_len
    len_t suffix_len
    uint32_t prefix_tree
    uint32_t suffix_tree

cdef struct SubstNodeC:
    attr_t orig
    attr_t subst

cdef union NodeC:
    MatchNodeC match_node
    SubstNodeC subst_node

cdef struct EditTreeC:
    bint is_match_node
    NodeC inner

cdef inline EditTreeC edittree_new_match(
    len_t prefix_len,
    len_t suffix_len,
    uint32_t prefix_tree,
    uint32_t suffix_tree
):
    cdef MatchNodeC match_node = MatchNodeC(
        prefix_len=prefix_len,
        suffix_len=suffix_len,
        prefix_tree=prefix_tree,
        suffix_tree=suffix_tree
    )
    cdef NodeC inner = NodeC(match_node=match_node)
    return EditTreeC(is_match_node=True, inner=inner)

cdef inline EditTreeC edittree_new_subst(attr_t orig, attr_t subst):
    cdef EditTreeC node
    cdef SubstNodeC subst_node = SubstNodeC(orig=orig, subst=subst)
    cdef NodeC inner = NodeC(subst_node=subst_node)
    return EditTreeC(is_match_node=False, inner=inner)

cdef inline uint64_t edittree_hash(EditTreeC tree):
    cdef MatchNodeC match_node
    cdef SubstNodeC subst_node

    if tree.is_match_node:
        match_node = tree.inner.match_node
        return hash((match_node.prefix_len, match_node.suffix_len, match_node.prefix_tree, match_node.suffix_tree))
    else:
        subst_node = tree.inner.subst_node
        return hash((subst_node.orig, subst_node.subst))

cdef struct LCS:
    int source_begin
    int source_end
    int target_begin
    int target_end

cdef inline bint lcs_is_empty(LCS lcs):
    return lcs.source_begin == 0 and lcs.source_end == 0 and lcs.target_begin == 0 and lcs.target_end == 0

cdef class EditTrees:
    cdef vector[EditTreeC] trees
    cdef unordered_map[hash_t, uint32_t] map
    cdef StringStore strings

    cpdef uint32_t add(self, str form, str lemma)
    cpdef str apply(self, uint32_t tree_id, str form)
    cpdef unicode tree_to_str(self, uint32_t tree_id)

    cdef uint32_t _add(self, str form, str lemma)
    cdef _apply(self, uint32_t tree_id, str form_part, list lemma_pieces)
    cdef uint32_t _tree_id(self, EditTreeC tree)
