from typing import Dict, List, Optional, Union, cast
import wasabi
from wasabi.util import supports_ansi

SUPPORTS_ANSI = supports_ansi()

SPACE = 0
HALF_HORIZONTAL_LINE = 1  # the half is the half further away from the root
FULL_HORIZONTAL_LINE = 3
UPPER_HALF_VERTICAL_LINE = 4
LOWER_HALF_VERTICAL_LINE = 8
FULL_VERTICAL_LINE = 12
ARROWHEAD = 16

ROOT_RIGHT_CHARS = {
    SPACE: " ",
    FULL_HORIZONTAL_LINE: "═",
    UPPER_HALF_VERTICAL_LINE + HALF_HORIZONTAL_LINE: "╝",
    UPPER_HALF_VERTICAL_LINE + FULL_HORIZONTAL_LINE: "╩",
    LOWER_HALF_VERTICAL_LINE + HALF_HORIZONTAL_LINE: "╗",
    LOWER_HALF_VERTICAL_LINE + FULL_HORIZONTAL_LINE: "╦",
    FULL_VERTICAL_LINE: "║",
    FULL_VERTICAL_LINE + HALF_HORIZONTAL_LINE: "╣",
    FULL_VERTICAL_LINE + FULL_HORIZONTAL_LINE: "╬",
    ARROWHEAD: "<",
}

ROOT_LEFT_CHARS = {
    SPACE: " ",
    FULL_HORIZONTAL_LINE: "═",
    UPPER_HALF_VERTICAL_LINE + HALF_HORIZONTAL_LINE: "╚",
    UPPER_HALF_VERTICAL_LINE + FULL_HORIZONTAL_LINE: "╩",
    LOWER_HALF_VERTICAL_LINE + HALF_HORIZONTAL_LINE: "╔",
    LOWER_HALF_VERTICAL_LINE + FULL_HORIZONTAL_LINE: "╦",
    FULL_VERTICAL_LINE: "║",
    FULL_VERTICAL_LINE + HALF_HORIZONTAL_LINE: "╠",
    FULL_VERTICAL_LINE + FULL_HORIZONTAL_LINE: "╬",
    ARROWHEAD: ">",
}


class AttributeFormat:
    """
    Instructions for rendering information about a token property, e.g. lemma_, ent_type_.
    """

    def __init__(
        self,
        attribute: str,
        *,
        name: str = "",
        aligns: str = "l",
        max_width: Optional[int] = None,
        fg_color: Optional[Union[str, int]] = None,
        bg_color: Optional[Union[str, int]] = None,
        value_dep_fg_colors: Optional[Dict[str, Union[str, int]]] = None,
        value_dep_bg_colors: Optional[Dict[str, Union[str, int]]] = None,
    ):
        """
        attribute:              the token attribute, e.g. lemma_, ._.holmes.lemma
        name:                   the name to display e.g. in column headers
        aligns:                 where appropriate the column alignment 'l' (left,
                                    default), 'r' (right) or 'c' (center).
        max_width:              a maximum width to which values of the attribute should be truncated.
        fg_color:               the foreground color that should be used to display instances of the attribute
        bg_color:               the background color that should be used to display instances of the attribute
        value_dep_fg_colors:    a dictionary from values to foreground colors that should be used to display those values.
        value_dep_bg_colors:    a dictionary from values to background colors that should be used to display those values.
        """
        self.attribute = attribute
        self.name = name
        self.aligns = aligns
        self.max_width = max_width
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.value_dep_fg_colors = (
            value_dep_fg_colors if value_dep_fg_colors is not None else {}
        )
        self.value_dep_bg_colors = (
            value_dep_bg_colors if value_dep_bg_colors is not None else {}
        )
        self.printer = wasabi.Printer(no_print=True)

    def render(
        self,
        token,
        *,
        right_pad_to_len: Optional[int] = None,
        ignore_colors: bool = False,
    ) -> str:
        """
        right_pad_to_len:           the width to which values should be right-padded, or 'None' for no right-padding.
        ignore_colors:              no colors should be rendered, typically because the values are required to calculate widths
        """
        value = _get_token_value(token, self.attribute)
        if self.max_width is not None:
            value = value[: self.max_width]
        fg_color = None
        bg_color = None
        if right_pad_to_len is not None:
            right_padding = " " * (right_pad_to_len - len(value))
        else:
            right_padding = ""
        if SUPPORTS_ANSI and not ignore_colors and len(value) > 0:
            if len(self.value_dep_fg_colors) > 0:
                fg_color = self.value_dep_fg_colors.get(value, None)
            if len(self.value_dep_bg_colors) > 0:
                bg_color = self.value_dep_bg_colors.get(value, None)
        if fg_color is not None or bg_color is not None:
            value = self.printer.text(value, color=fg_color, bg_color=bg_color)
        return value + right_padding


def render_dep_tree(sent, root_right: bool) -> List[str]:
    """
    Returns an ASCII rendering of the document with a dependency tree for each sentence. The
    dependency tree output for a given token has the same index within the output list of
    strings as that token within the input document.

    root_right: True if the tree should be rendered with the root on the right-hand side,
                False if the tree should be rendered with the root on the left-hand side.

    Algorithm adapted from https://github.com/KoichiYasuoka/deplacy
    """

    # Check sent is really a sentence
    if sent.start != sent[0].sent.start or sent.end != sent[0].sent.end:
        raise ValueError(f"Span is not a sentence: '{sent}'")
    heads: List[Optional[int]] = []
    for token in sent:
        if token.dep_.lower() == "root" or token.head.i == token.i:
            heads.append(None)
        else:
            heads.append(token.head.i - sent.start)
    # Check there are no head references outside the sentence
    heads_outside_sent = [
        1 for h in heads if h is not None and (h < 0 or h > sent.end - sent.start)
    ]
    if len(heads_outside_sent) > 0:
        raise ValueError(f"Head reference outside sentence in sentence '{sent}'")
    children_lists: List[List[int]] = [[] for _ in range(sent.end - sent.start)]
    for child, head in enumerate(heads):
        if head is not None:
            children_lists[head].append(child)
    all_ind_ord_by_col: List[int] = []
    # start with the root column
    inds_in_this_col = [i for i, h in enumerate(heads) if h is None]
    while len(inds_in_this_col) > 0:
        all_ind_ord_by_col = inds_in_this_col + all_ind_ord_by_col
        inds_in_next_col = []
        # The calculation order of the horizontal lengths of the children
        # on either given side of a head must ensure that children
        # closer to the head are processed first.
        for ind_in_this_col in inds_in_this_col:
            following_child_inds = [
                i for i in children_lists[ind_in_this_col] if i > ind_in_this_col
            ]
            inds_in_next_col.extend(following_child_inds)
            preceding_child_inds = [
                i for i in children_lists[ind_in_this_col] if i < ind_in_this_col
            ]
            preceding_child_inds.reverse()
            inds_in_next_col.extend(preceding_child_inds)
        inds_in_this_col = inds_in_next_col
    horiz_line_lens: List[int] = []
    for i in range(sent.end - sent.start):
        if heads[i] is None:
            horiz_line_lens.append(-1)
        elif len(children_lists[i]) == 0 and abs(cast(int, heads[i]) - i) == 1:
            # governed by direct neighbour and has no children itself
            horiz_line_lens.append(1)
        else:
            horiz_line_lens.append(0)
    while 0 in horiz_line_lens:
        for working_token_ind in (
            i for i in all_ind_ord_by_col if horiz_line_lens[i] == 0
        ):
            # render relation between this token and its head
            first_ind_in_rel = min(
                working_token_ind,
                cast(int, heads[working_token_ind]),
            )
            second_ind_in_rel = max(
                working_token_ind,
                cast(int, heads[working_token_ind]),
            )
            # If this token has children, they will already have been rendered.
            # The line needs to be one character longer than the longest of the
            # children's lines.
            if len(children_lists[working_token_ind]) > 0:
                horiz_line_lens[working_token_ind] = (
                    max([horiz_line_lens[i] for i in children_lists[working_token_ind]])
                    + 1
                )
            else:
                horiz_line_lens[working_token_ind] = 1
            for inbetween_ind in (
                i
                for i in range(first_ind_in_rel + 1, second_ind_in_rel)
                if horiz_line_lens[i] != 0
            ):
                alt_ind: int
                if (
                    inbetween_ind in children_lists[cast(int, heads[working_token_ind])]
                    and inbetween_ind not in children_lists[working_token_ind]
                ):
                    alt_ind = horiz_line_lens[inbetween_ind]
                else:
                    alt_ind = horiz_line_lens[inbetween_ind] + 1
                if alt_ind > horiz_line_lens[working_token_ind]:
                    horiz_line_lens[working_token_ind] = alt_ind
    max_horiz_line_len = max(horiz_line_lens)
    char_matrix = [
        [SPACE] * max_horiz_line_len * 2 for _ in range(sent.start, sent.end)
    ]
    for working_token_ind in range(sent.end - sent.start):
        head_token_ind = heads[working_token_ind]
        if head_token_ind is None:
            continue
        first_ind_in_rel = min(working_token_ind, head_token_ind)
        second_ind_in_rel = max(working_token_ind, head_token_ind)
        char_horiz_line_len = 2 * horiz_line_lens[working_token_ind]

        # Draw the corners of the relation
        char_matrix[first_ind_in_rel][char_horiz_line_len - 1] |= (
            HALF_HORIZONTAL_LINE + LOWER_HALF_VERTICAL_LINE
        )
        char_matrix[second_ind_in_rel][char_horiz_line_len - 1] |= (
            HALF_HORIZONTAL_LINE + UPPER_HALF_VERTICAL_LINE
        )

        # Draw the horizontal line for the governing token
        for working_horiz_pos in range(char_horiz_line_len - 1):
            if char_matrix[head_token_ind][working_horiz_pos] != FULL_VERTICAL_LINE:
                char_matrix[head_token_ind][working_horiz_pos] |= FULL_HORIZONTAL_LINE

        # Draw the vertical line for the relation
        for working_vert_pos in range(first_ind_in_rel + 1, second_ind_in_rel):
            if (
                char_matrix[working_vert_pos][char_horiz_line_len - 1]
                != FULL_HORIZONTAL_LINE
            ):
                char_matrix[working_vert_pos][
                    char_horiz_line_len - 1
                ] |= FULL_VERTICAL_LINE
    for working_token_ind in (
        i for i in range(sent.end - sent.start) if heads[i] is not None
    ):
        for working_horiz_pos in range(
            2 * horiz_line_lens[working_token_ind] - 2, -1, -1
        ):
            if (
                (
                    char_matrix[working_token_ind][working_horiz_pos]
                    == FULL_VERTICAL_LINE
                )
                and working_horiz_pos > 1
                and char_matrix[working_token_ind][working_horiz_pos - 2] == SPACE
            ):
                # Cross over the existing vertical line, which is owing to a non-projective tree
                continue
            if char_matrix[working_token_ind][working_horiz_pos] != SPACE:
                # Draw the arrowhead to the right of what is already there
                char_matrix[working_token_ind][working_horiz_pos + 1] = ARROWHEAD
                break
            if working_horiz_pos == 0:
                # Draw the arrowhead at the boundary of the diagram
                char_matrix[working_token_ind][working_horiz_pos] = ARROWHEAD
            else:
                # Fill in the horizontal line for the governed token
                char_matrix[working_token_ind][
                    working_horiz_pos
                ] |= FULL_HORIZONTAL_LINE
    if root_right:
        return [
            "".join(
                ROOT_RIGHT_CHARS[char_matrix[vert_pos][horiz_pos]]
                for horiz_pos in range((max_horiz_line_len * 2))
            )
            for vert_pos in range(sent.end - sent.start)
        ]
    else:
        return [
            "".join(
                ROOT_LEFT_CHARS[char_matrix[vert_pos][horiz_pos]]
                for horiz_pos in range((max_horiz_line_len * 2))
            )[::-1]
            for vert_pos in range(sent.end - sent.start)
        ]


def render_table(
    doc,
    cols: List[AttributeFormat],
    spacing: int = 3,
    search_attr_name: Optional[str] = None,
    search_attr_value: Optional[str] = None,
    start_i: int = 0,
    length: Optional[int] = None,
) -> str:
    """Renders a document as a table, allowing the caller to specify various
        display options.

    doc:                the document.
    cols:               the attribute formats of the columns to display.
                            tree_right and tree_left are magic values for the
                            attributes that render dependency trees where the
                            roots are on the left or right respectively.
    spacing:            the number of spaces between each column in the table.
    search_attr_name:   the name of an attribute to search for in order to
                            determine where to start rendering, e.g. "lemma_",
                            or *None* if no search is to be carried out. If either
                            of *search_attr_name* and *search_attr_value* is *None*,
                            the behaviour is as if both were *None*.
    search_attr_value:  the value of an attribute to search for in order to
                            determine where to start rendering, e.g. "be",
                            or *None* if no search is to be carried out. If either
                            of *search_attr_name* and *search_attr_value* is *None*,
                            the behaviour is as if both were *None*.
    start_i:            the token index at which to start searching, or at
                            whose sentence to start rendering. Default: 0.
    length:             the number of tokens after *start_i* at whose sentence
                            to stop rendering. If *None*, the rest of the
                            document is rendered.
    """
    return_str = ""
    if (
        search_attr_name is not None
        and search_attr_name not in ("tree_right", "tree_left")
        and search_attr_value is not None
    ):
        adj_start_i = _get_adjusted_start_i(
            doc, start_i, cols, search_attr_name, search_attr_value
        )
    else:
        adj_start_i = start_i
    if adj_start_i >= len(doc):
        return return_str
    end_i = len(doc) - 1
    if length is not None:
        end_i = min(end_i, adj_start_i + length)
    elif start_i > 0 or (
        search_attr_name is not None and search_attr_value is not None
    ):
        end_i = adj_start_i
    adj_start_i = doc[adj_start_i].sent.start
    end_i = doc[end_i].sent.end
    for sent in doc[adj_start_i:end_i].sents:
        if "tree_right" in (c.attribute for c in cols):
            tree_right = render_dep_tree(sent, True)
        if "tree_left" in (c.attribute for c in cols):
            tree_left = render_dep_tree(sent, False)
        widths = []
        for col in cols:
            # get the values without any color codes
            if col.attribute == "tree_left":
                width = len(tree_left[0])  # type: ignore
            elif col.attribute == "tree_right":
                width = len(tree_right[0])  # type: ignore
            else:
                if len(sent) > 0:
                    width = max(
                        len(col.render(token, ignore_colors=True)) for token in sent
                    )
                else:
                    width = 0
                if col.max_width is not None:
                    width = min(width, col.max_width)
            width = max(width, len(col.name))
            widths.append(width)
        data: List[List[str]] = []
        for token_index, token in enumerate(sent):
            inner_data: List[str] = []
            for col_index, col in enumerate(cols):
                if col.attribute == "tree_right":
                    inner_data.append(tree_right[token_index])
                elif col.attribute == "tree_left":
                    inner_data.append(tree_left[token_index])
                else:
                    inner_data.append(
                        col.render(token, right_pad_to_len=widths[col_index])
                    )
            data.append(inner_data)
        header: Optional[List[str]]
        if len([1 for c in cols if len(c.name) > 0]) > 0:
            header = [c.name for c in cols]
        else:
            header = None
        aligns = [c.aligns for c in cols]
        fg_colors = [c.fg_color for c in cols]
        bg_colors = [c.bg_color for c in cols]
        return_str += (
            wasabi.table(
                data,
                header=header,
                divider=True,
                aligns=aligns,  # type:ignore[arg-type]
                widths=widths,
                fg_colors=fg_colors,
                bg_colors=bg_colors,
                spacing=spacing,
            )
            + "\n"
        )
    return return_str


def render_document(
    doc,
    search_attr_name: Optional[str] = None,
    search_attr_value: Optional[str] = None,
    *,
    start_i: int = 0,
    length: Optional[int] = None,
) -> str:
    """Renders a document as a table using standard display options.

    doc:                the document.
    search_attr_name:   the name of an attribute to search for in order to
                            determine where to start rendering, e.g. "lemma_",
                            or *None* if no search is to be carried out. If either
                            of *search_attr_name* and *search_attr_value* is *None*,
                            the behaviour is as if both were *None*.
    search_attr_value:  the value of an attribute to search for in order to
                            determine where to start rendering, e.g. "be",
                            or *None* if no search is to be carried out. If either
                            of *search_attr_name* and *search_attr_value* is *None*,
                            the behaviour is as if both were *None*.
    start_i:            the token index at which to start searching, or at
                            whose sentence to start rendering. Default: 0.
    length:             the number of tokens after *start_i* at whose sentence
                            to stop rendering. If *None*, the rest of the
                            document is rendered.
    """
    cols = [
        AttributeFormat("tree_left", name="tree", aligns="r", fg_color=4),
        AttributeFormat("dep_", name="dep_"),
        AttributeFormat("ent_type_", name="ent_type_"),
        AttributeFormat("i", name="index", aligns="r"),
        AttributeFormat("text", name="text", max_width=30),
        AttributeFormat("lemma_", name="lemma_", max_width=30),
        AttributeFormat("pos_", name="pos_"),
        AttributeFormat("tag_", name="tag_"),
        AttributeFormat("morph", name="morph", max_width=80),
    ]
    if search_attr_name is not None and search_attr_value is not None:
        for col in cols:
            if col.attribute == search_attr_name or col.name == search_attr_name:
                col.value_dep_fg_colors[search_attr_value] = 1
    return render_table(
        doc=doc,
        cols=cols,
        spacing=3,
        search_attr_name=search_attr_name,
        search_attr_value=search_attr_value,
        start_i=start_i,
        length=length,
    )


def _get_token_value(token, attribute: str) -> str:
    """
    Get value *token.x.y.z*.

    token: the token
    attribute: the attribute name, e.g. *x.y.z*.
    """
    obj = token
    parts = attribute.split(".")
    for part in parts[:-1]:
        obj = getattr(obj, part)
    return str(getattr(obj, parts[-1])).strip()


def _get_adjusted_start_i(
    doc,
    start_i: int,
    cols: List[AttributeFormat],
    search_attr_name: str,
    search_attr_value: str,
):
    """
    Get the position at which to start rendering a document, which may be
    adjusted by a search for a specific attribute value.

    doc: the document
    start_i: the user-specified start index
    cols: the list of attribute columns being displayed
    search_attr_name: the name of the attribute for which values are being searched,
        i.e. *x.y.z* for token attribute *token.x.y.z*, or *None* if no search is to be performed.
    search_attr_value: the attribute value for which to search.

    """
    for col in cols:
        if col.name == search_attr_name or col.attribute == search_attr_name:
            for token in doc[start_i:]:
                if _get_token_value(token, col.attribute) == search_attr_value:
                    return token.i
    else:
        return len(doc)
