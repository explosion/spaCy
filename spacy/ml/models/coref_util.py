from thinc.types import Ints2d
from spacy.tokens import Doc
from typing import List, Tuple, Callable, Any
from ...util import registry

# type alias to make writing this less tedious
MentionClusters = List[List[Tuple[int, int]]]

DEFAULT_CLUSTER_PREFIX = "coref_clusters"


def doc2clusters(doc: Doc, prefix=DEFAULT_CLUSTER_PREFIX) -> MentionClusters:
    """Given a doc, give the mention clusters.

    This is useful for scoring.
    """
    out = []
    for name, val in doc.spans.items():
        if not name.startswith(prefix):
            continue

        cluster = []
        for mention in val:
            cluster.append((mention.start, mention.end))
        out.append(cluster)
    return out


def topk(xp, arr, k, axis=None):
    """Given and array and a k value, give the top values and idxs for each row."""

    part = xp.argpartition(arr, -k, axis=1)
    idxs = xp.flip(part)[:, :k]

    vals = xp.take_along_axis(arr, idxs, axis=1)

    sidxs = xp.argsort(vals, axis=1)
    # map these idxs back to the original
    oidxs = xp.take_along_axis(idxs, sidxs, axis=1)
    svals = xp.take_along_axis(vals, sidxs, axis=1)
    return svals, oidxs


def logsumexp(xp, arr, axis=None):
    """Emulate torch.logsumexp by returning the log of summed exponentials
    along each row in the given dimension.

    Reduces a 2d array to 1d."""
    # from slide 5 here:
    # https://www.slideshare.net/ryokuta/cupy

    # Note: this was added to reproduce loss calculation in coref-hoi. If loss
    # can be calculated using another method this is not necessary.
    hi = arr.max(axis=axis)
    hi = xp.expand_dims(hi, 1)
    return hi.squeeze() + xp.log(xp.exp(arr - hi).sum(axis=axis))


# from model.py, refactored to be non-member
def get_predicted_antecedents(xp, antecedent_idx, antecedent_scores):
    """Get the ID of the antecedent for each span. -1 if no antecedent."""
    predicted_antecedents = []
    for i, idx in enumerate(xp.argmax(antecedent_scores, axis=1) - 1):
        if idx < 0:
            predicted_antecedents.append(-1)
        else:
            predicted_antecedents.append(antecedent_idx[i][idx])
    return predicted_antecedents


# from model.py, refactored to be non-member
def get_predicted_clusters(
    xp, span_starts, span_ends, antecedent_idx, antecedent_scores
):
    """Convert predictions to usable cluster data.

    return values:

    clusters: a list of spans (i, j) that are a cluster

    Note that not all spans will be in the final output; spans with no
    antecedent or referrent are omitted from clusters and mention2cluster.
    """
    # Get predicted antecedents
    predicted_antecedents = get_predicted_antecedents(
        xp, antecedent_idx, antecedent_scores
    )

    # Get predicted clusters
    mention_to_cluster_id = {}
    predicted_clusters = []
    for i, predicted_idx in enumerate(predicted_antecedents):
        if predicted_idx < 0:
            continue
        assert i > predicted_idx, f"span idx: {i}; antecedent idx: {predicted_idx}"
        # Check antecedent's cluster
        antecedent = (int(span_starts[predicted_idx]), int(span_ends[predicted_idx]))
        antecedent_cluster_id = mention_to_cluster_id.get(antecedent, -1)
        if antecedent_cluster_id == -1:
            antecedent_cluster_id = len(predicted_clusters)
            predicted_clusters.append([antecedent])
            mention_to_cluster_id[antecedent] = antecedent_cluster_id
        # Add mention to cluster
        mention = (int(span_starts[i]), int(span_ends[i]))
        predicted_clusters[antecedent_cluster_id].append(mention)
        mention_to_cluster_id[mention] = antecedent_cluster_id

    predicted_clusters = [tuple(c) for c in predicted_clusters]
    return predicted_clusters


def get_sentence_map(doc: Doc):
    """For the given span, return a list of sentence indexes."""
    if doc.is_sentenced:
        si = 0
        out = []
        for sent in doc.sents:
            for _ in sent:
                out.append(si)
            si += 1
        return out
    else:
        # If there are no sents then just return dummy values.
        # Shouldn't happen in general training, but typical in init.
        return [0] * len(doc)


def get_candidate_mentions(
    doc: Doc, max_span_width: int = 20
) -> Tuple[List[int], List[int]]:
    """Given a Doc, return candidate mentions.

    This isn't a trainable layer, it just returns raw candidates.
    """
    # XXX Note that in coref-hoi the indexes are designed so you actually want [i:j+1], but here
    # we're using [i:j], which is more natural.

    sentence_map = get_sentence_map(doc)

    begins = []
    ends = []
    for tok in doc:
        si = sentence_map[tok.i]  # sentence index
        for ii in range(1, max_span_width):
            ei = tok.i + ii  # end index
            if ei < len(doc) and sentence_map[ei] == si:
                begins.append(tok.i)
                ends.append(ei)

    return (begins, ends)


@registry.misc("spacy.CorefCandidateGenerator.v1")
def create_mention_generator() -> Any:
    return get_candidate_mentions


def select_non_crossing_spans(
    idxs: List[int], starts: List[int], ends: List[int], limit: int
) -> List[int]:
    """Given a list of spans sorted in descending order, return the indexes of
    spans to keep, discarding spans that cross.

    Nested spans are allowed.
    """
    # ported from Model._extract_top_spans
    selected = []
    start_to_max_end = {}
    end_to_min_start = {}

    for idx in idxs:
        if len(selected) >= limit or idx > len(starts):
            break

        start, end = starts[idx], ends[idx]
        cross = False

        for ti in range(start, end + 1):
            max_end = start_to_max_end.get(ti, -1)
            if ti > start and max_end > end:
                cross = True
                break

            min_start = end_to_min_start.get(ti, -1)
            if ti < end and 0 <= min_start < start:
                cross = True
                break

        if not cross:
            # this index will be kept
            # record it so we can exclude anything that crosses it
            selected.append(idx)
            max_end = start_to_max_end.get(start, -1)
            if end > max_end:
                start_to_max_end[start] = end
            min_start = end_to_min_start.get(end, -1)
            if start == -1 or start < min_start:
                end_to_min_start[end] = start

    # sort idxs by order in doc
    selected = sorted(selected, key=lambda idx: (starts[idx], ends[idx]))
    # This was causing many repetitive entities in the output - removed for now
    # while len(selected) < limit:
    #     selected.append(selected[0])  # this seems a bit weird?
    return selected


def get_clusters_from_doc(doc) -> List[List[Tuple[int, int]]]:
    """Given a Doc, convert the cluster spans to simple int tuple lists."""
    out = []
    for key, val in doc.spans.items():
        cluster = []
        for span in val:
            # TODO check that there isn't an off-by-one error here
            cluster.append((span.start, span.end))
        out.append(cluster)
    return out


def create_gold_scores(
    ments: Ints2d, clusters: List[List[Tuple[int, int]]]
) -> List[List[bool]]:
    """Given mentions considered for antecedents and gold clusters,
    construct a gold score matrix. This does not include the placeholder."""
    # make a mapping of mentions to cluster id
    # id is not important but equality will be
    ment2cid = {}
    for cid, cluster in enumerate(clusters):
        for ment in cluster:
            ment2cid[ment] = cid

    ll = len(ments)
    out = []
    # The .tolist() call is necessary with cupy but not numpy
    mentuples = [tuple(mm.tolist()) for mm in ments]
    for ii, ment in enumerate(mentuples):
        if ment not in ment2cid:
            # this is not in a cluster so it has no antecedent
            out.append([False] * ll)
            continue

        # this might change if no real antecedent is a candidate
        row = []
        cid = ment2cid[ment]
        for jj, ante in enumerate(mentuples):
            # antecedents must come first
            if jj >= ii:
                row.append(False)
                continue

            row.append(cid == ment2cid.get(ante, -1))

        out.append(row)

    # caller needs to convert to array, and add placeholder
    return out
