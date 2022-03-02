from typing import Dict, List, Optional, Union, cast
import wasabi
from wasabi.util import supports_ansi
from spacy.tokens import Span, Token, Doc

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
        permitted_vals: Optional[tuple] = None,
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
        permitted_vals:         a tuple of values of the attribute that should be displayed. If
                                    permitted_values is not None and a value of the attribute is not
                                    in permitted_values, the empty string is rendered instead of the value.
        value_dep_fg_colors:    a dictionary from values to foreground colors that should be used to display those values.
        value_dep_bg_colors:    a dictionary from values to background colors that should be used to display those values.
        """
        self.attribute = attribute
        self.name = name
        self.aligns = aligns
        self.max_width = max_width
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.permitted_vals = permitted_vals
        self.value_dep_fg_colors = value_dep_fg_colors
        self.value_dep_bg_colors = value_dep_bg_colors
        self.printer = wasabi.Printer(no_print=True)

    def render(
        self,
        token: Token,
        *,
        right_pad_to_len: Optional[int] = None,
        ignore_colors: bool = False,
        render_all_colors_in_vals: bool = False,
        whole_row_fg_color: Union[int, str, None] = None,
        whole_row_bg_color: Union[int, str, None] = None,
    ) -> str:
        """
        right_pad_to_len:           the width to which values should be right-padded, or 'None' for no right-padding.
        ignore_colors:              no colors should be rendered, typically because the values are required to calculate widths
        render_all_colors_in_vals:  when rendering a table, self.fg_color and self.bg_color are rendered in Wasabi.
                                    This argument is set to True when rendering a text to signal that colors should be rendered here.
        whole_row_fg_color:         a foreground color used for the whole row. This takes precedence over value_dependent_fg_colors.
        whole_row_bg_color:         a background color used for the whole row. This takes precedence over value_dependent_bg_colors.
        """
        obj = token
        parts = self.attribute.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        value = str(getattr(obj, parts[-1]))
        if self.permitted_vals is not None and value not in (
            str(v) for v in self.permitted_vals
        ):
            return ""
        if self.max_width is not None:
            value = value[: self.max_width]
        fg_color = None
        bg_color = None
        if right_pad_to_len is not None:
            right_padding = " " * (right_pad_to_len - len(value))
        else:
            right_padding = ""
        if SUPPORTS_ANSI and not ignore_colors and len(value) > 0:
            if whole_row_fg_color is not None:
                fg_color = whole_row_fg_color
            elif self.value_dep_fg_colors is not None:
                fg_color = self.value_dep_fg_colors.get(value, None)
            if fg_color is None and render_all_colors_in_vals:
                fg_color = self.fg_color
            if self.value_dep_bg_colors is not None:
                bg_color = self.value_dep_bg_colors.get(value, None)
            if whole_row_bg_color is not None:
                bg_color = whole_row_bg_color
            elif bg_color is None and render_all_colors_in_vals:
                bg_color = self.bg_color
        if fg_color is not None or bg_color is not None:
            value = self.printer.text(value, color=fg_color, bg_color=bg_color)
        return value + right_padding


class Visualizer:
    @staticmethod
    def render_dep_tree(sent: Span, root_right: bool) -> List[str]:
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
                        max(
                            [
                                horiz_line_lens[i]
                                for i in children_lists[working_token_ind]
                            ]
                        )
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
                        inbetween_ind
                        in children_lists[cast(int, heads[working_token_ind])]
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
                    char_matrix[head_token_ind][
                        working_horiz_pos
                    ] |= FULL_HORIZONTAL_LINE

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

    def render_table(self, doc: Doc, cols: List[AttributeFormat], spacing: int) -> str:
        """Renders a document as a table.
        TODO: specify a specific portion of the document to display.

        cols:       the attribute formats of the columns to display.
                        tree_right and tree_left are magic values for the
                        attributes that render dependency trees where the
                        roots are on the left or right respectively.
        spacing:    the number of spaces between each column in the table.
        """
        return_str = ""
        for sent in doc.sents:
            if "tree_right" in (c.attribute for c in cols):
                tree_right = self.render_dep_tree(sent, True)
            if "tree_left" in (c.attribute for c in cols):
                tree_left = self.render_dep_tree(sent, False)
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
                    aligns=aligns,
                    widths=widths,
                    fg_colors=fg_colors,
                    bg_colors=bg_colors,
                    spacing=spacing,
                )
                + "\n"
            )
        return return_str

    def render_text(self, doc: Doc, attrs: List[AttributeFormat]) -> str:
        """Renders a text interspersed with attribute labels.
        TODO: specify a specific portion of the document to display.

        """
        return_str = ""
        text_attrs = [a for a in attrs if a.attribute == "text"]
        text_attr = text_attrs[0] if len(text_attrs) > 0 else AttributeFormat("text")
        for token in doc:
            this_token_strs = [""]
            for attr in (a for a in attrs if a.attribute != "text"):
                attr_text = attr.render(token, render_all_colors_in_vals=True)
                if attr_text is not None and len(attr_text) > 0:
                    this_token_strs.append(" " + attr_text)
            if len(this_token_strs) == 1:
                this_token_strs[0] = token.text
            else:
                this_token_strs[0] = text_attr.render(
                    token, render_all_colors_in_vals=True
                )
            this_token_strs.append(token.whitespace_)
            return_str += "".join(this_token_strs)
        return return_str

    def render_instances(
        self,
        doc: Doc,
        *,
        search_attrs: List[AttributeFormat],
        display_cols: List[AttributeFormat],
        group: bool,
        spacing: int,
        surrounding_tokens_height: int,
        surrounding_tokens_fg_color: Union[str, int],
        surrounding_tokens_bg_color: Union[str, int],
    ) -> str:
        """Shows all tokens in a document with specific attribute(s), e.g. entity labels, or attribute value(s), e.g. 'GPE'.
        TODO: specify a specific portion of the document to display.

        search_attrs:                   the attribute(s) or attribute value(s) that cause a row to be displayed for a token.
        display_cols:                   the attributes that should be displayed in each row.
        group:                          True if the rows should be ordered by the search attribute values,
                                            False if they should retain their in-document order.
        spacing:                        the number of spaces between each column.
        surrounding_tokens_height:      a number of rows that should be displayed with information about tokens
                                            before and after matched tokens. Consecutive matching tokens, e.g.
                                            tokens belonging to the same named entity, are rendered together as a single group.
        surrounding_tokens_fg_color:    a foreground color to use for surrounding token rows.
        surrounding_tokens_bg_color:    a background color to use for surrounding token rows.
                                            Note that if surrounding_tokens_bg_color is None, any background color defined for the attribute
                                            will be used instead, which is unlikely to be the desired result.
        """

        def filter(token: Token) -> bool:
            for attr in search_attrs:
                value = attr.render(token, ignore_colors=True)
                if len(value) == 0:
                    return False
            return True

        matched_tokens = [token for token in doc if filter(token)]
        tokens_to_display_inds: List[int] = []
        for token in matched_tokens:
            for ind in range(
                token.i - surrounding_tokens_height,
                token.i + surrounding_tokens_height + 1,
            ):
                if ind >= 0 and ind < len(doc):
                    tokens_to_display_inds.append(ind)
        widths = []
        for col in display_cols:
            if len(tokens_to_display_inds) > 0:
                width = max(
                    len(col.render(doc[i], ignore_colors=True))
                    for i in tokens_to_display_inds
                )
            else:
                width = 0
            if col.max_width is not None:
                width = min(width, col.max_width)
            width = max(width, len(col.name))
            widths.append(width)
        if group:
            matched_tokens.sort(
                key=(
                    lambda token: [
                        attr.render(token, ignore_colors=True) for attr in search_attrs
                    ]
                )
            )

        rows = []
        token_ind_to_display = -1
        for matched_token_ind, matched_token in enumerate(matched_tokens):
            if surrounding_tokens_height > 0:
                surrounding_start_ind = max(
                    0, matched_token.i - surrounding_tokens_height
                )
                if token_ind_to_display + 1 == matched_token.i:
                    surrounding_start_ind = token_ind_to_display + 1
                surrounding_end_ind = min(
                    len(doc), matched_token.i + surrounding_tokens_height + 1
                )
                if (
                    matched_token_ind + 1 < len(matched_tokens)
                    and matched_token.i + 1 == matched_tokens[matched_token_ind + 1].i
                ):
                    surrounding_end_ind = matched_token.i + 1

            else:
                surrounding_start_ind = matched_token.i
                surrounding_end_ind = surrounding_start_ind + 1
            for token_ind_to_display in range(
                surrounding_start_ind, surrounding_end_ind
            ):
                if token_ind_to_display == matched_token.i:
                    rows.append(
                        [
                            col.render(
                                matched_token,
                                right_pad_to_len=widths[col_ind],
                            )
                            for col_ind, col in enumerate(display_cols)
                        ]
                    )
                else:
                    rows.append(
                        [
                            col.render(
                                doc[token_ind_to_display],
                                whole_row_fg_color=surrounding_tokens_fg_color,
                                whole_row_bg_color=surrounding_tokens_bg_color,
                                right_pad_to_len=widths[col_ind],
                            )
                            for col_ind, col in enumerate(display_cols)
                        ]
                    )
            if (
                matched_token_ind + 1 < len(matched_tokens)
                and token_ind_to_display + 1 != matched_tokens[matched_token_ind + 1].i
            ):
                rows.append([])
        header: Optional[List[str]]
        if len([1 for c in display_cols if len(c.name) > 0]) > 0:
            header = [c.name for c in display_cols]
        else:
            header = None
        aligns = [c.aligns for c in display_cols]
        fg_colors = [c.fg_color for c in display_cols]
        bg_colors = [c.bg_color for c in display_cols]
        return wasabi.table(
            rows,
            header=header,
            divider=True,
            aligns=aligns,
            widths=widths,
            fg_colors=fg_colors,
            bg_colors=bg_colors,
            spacing=spacing,
        )
