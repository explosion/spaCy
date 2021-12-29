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
        fg_color: Union[str, int, None] = None,
        bg_color: Union[str, int, None] = None,
        permitted_values: Optional[tuple] = None,
        value_dependent_fg_colors: Optional[Dict[str, Union[str, int]]] = None,
        value_dependent_bg_colors: Optional[Dict[str, Union[str, int]]] = None,
    ):
        """
        attribute:                  the token attribute, e.g. lemma_, ._.holmes.lemma
        name:                       the name to display e.g. in column headers
        aligns:                     where appropriate the column alignment 'l' (left,
                                        default), 'r' (right) or 'c' (center).
        max_width:                  a maximum width to which values of the attribute should be truncated.
        fg_color:                   the foreground color that should be used to display instances of the attribute
        bg_color:                   the background color that should be used to display instances of the attribute
        permitted_values:           a tuple of values of the attribute that should be displayed. If
                                        permitted_values is not None and a value of the attribute is not
                                        in permitted_values, the empty string is rendered instead of the value.
        value_dependent_fg_colors:  a dictionary from values to foreground colors that should be used to display those values.
        value_dependent_bg_colors:  a dictionary from values to background colors that should be used to display those values.
        """
        self.attribute = attribute
        self.name = name
        self.aligns = aligns
        self.max_width = max_width
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.permitted_values = permitted_values
        self.value_dependent_fg_colors = value_dependent_fg_colors
        self.value_dependent_bg_colors = value_dependent_bg_colors
        self.printer = wasabi.Printer(no_print=True)

    def render(
        self,
        token: Token,
        *,
        right_pad_to_length: Optional[int] = None,
        ignore_colors: bool = False,
        render_all_colors_within_values: bool = False,
        whole_row_fg_color: Union[int, str, None] = None,
        whole_row_bg_color: Union[int, str, None] = None,
    ) -> str:
        """
        ignore_colors:                      no colors should be rendered, typically because the values are required to calculate widths
        render_all_colors_within_values:    when rendering a table, self.fg_color and self.bg_color are rendered in Wasabi.
                                                This argument is set to True when rendering a text to signal that colors should be rendered here.
        whole_row_fg_color:                 a foreground color used for the whole row. This takes precedence over value_dependent_fg_colors.
        whole_row_bg_color:                 a background color used for the whole row. This takes precedence over value_dependent_bg_colors.
        """
        obj = token
        parts = self.attribute.split(".")
        for part in parts[:-1]:
            obj = getattr(obj, part)
        value = str(getattr(obj, parts[-1]))
        if self.permitted_values is not None and value not in (
            str(v) for v in self.permitted_values
        ):
            return ""
        if self.max_width is not None:
            value = value[: self.max_width]
        fg_color = None
        bg_color = None
        if right_pad_to_length is not None:
            right_padding = " " * (right_pad_to_length - len(value))
        else:
            right_padding = ""
        if SUPPORTS_ANSI and not ignore_colors and len(value) > 0:
            if whole_row_fg_color is not None:
                fg_color = whole_row_fg_color
            elif self.value_dependent_fg_colors is not None:
                fg_color = self.value_dependent_fg_colors.get(value, None)
            if fg_color is None and render_all_colors_within_values:
                fg_color = self.fg_color
            if self.value_dependent_bg_colors is not None:
                bg_color = self.value_dependent_bg_colors.get(value, None)
            if whole_row_bg_color is not None:
                bg_color = whole_row_bg_color
            elif bg_color is None and render_all_colors_within_values:
                bg_color = self.bg_color
        if fg_color is not None or bg_color is not None:
            value = self.printer.text(value, color=fg_color, bg_color=bg_color)
        return value + right_padding


class Visualizer:
    @staticmethod
    def render_dependency_tree(sent: Span, root_right: bool) -> List[str]:
        """
        Returns an ASCII rendering of the document with a dependency tree for each sentence. The
        dependency tree output for a given token has the same index within the output list of
        strings as that token within the input document.

        root_right: True if the tree should be rendered with the root on the right-hand side,
                    False if the tree should be rendered with the root on the left-hand side.

        Algorithm adapted from https://github.com/KoichiYasuoka/deplacy
        """

        # Check sent is really a sentence
        assert sent.start == sent[0].sent.start
        assert sent.end == sent[0].sent.end
        heads: List[Optional[int]] = [
            None
            if token.dep_.lower() == "root" or token.head.i == token.i
            else token.head.i - sent.start
            for token in sent
        ]
        # Check there are no head references outside the sentence
        assert (
            len(
                [
                    head
                    for head in heads
                    if head is not None and (head < 0 or head > sent.end - sent.start)
                ]
            )
            == 0
        )
        children_lists: List[List[int]] = [[] for _ in range(sent.end - sent.start)]
        for child, head in enumerate(heads):
            if head is not None:
                children_lists[head].append(child)
        all_indices_ordered_by_column: List[int] = []
        # start with the root column
        indices_in_current_column = [i for i, h in enumerate(heads) if h is None]
        while len(indices_in_current_column) > 0:
            assert (
                len(
                    [
                        i
                        for i in indices_in_current_column
                        if i in all_indices_ordered_by_column
                    ]
                )
                == 0
            )
            all_indices_ordered_by_column = (
                indices_in_current_column + all_indices_ordered_by_column
            )
            indices_in_next_column = []
            # The calculation order of the horizontal lengths of the children
            # on either given side of a head must ensure that children
            # closer to the head are processed first.
            for index_in_current_column in indices_in_current_column:
                following_children_indices = [
                    i
                    for i in children_lists[index_in_current_column]
                    if i > index_in_current_column
                ]
                indices_in_next_column.extend(following_children_indices)
                preceding_children_indices = [
                    i
                    for i in children_lists[index_in_current_column]
                    if i < index_in_current_column
                ]
                preceding_children_indices.reverse()
                indices_in_next_column.extend(preceding_children_indices)
            indices_in_current_column = indices_in_next_column
        horizontal_line_lengths = [
            -1 if heads[i] is None else 1
            # length == 1: governed by direct neighbour and has no children itself
            if len(children_lists[i]) == 0 and abs(cast(int, heads[i]) - i) == 1 else 0
            for i in range(sent.end - sent.start)
        ]
        while 0 in horizontal_line_lengths:
            for working_token_index in (
                i
                for i in all_indices_ordered_by_column
                if horizontal_line_lengths[i] == 0
            ):
                # render relation between this token and its head
                first_index_in_relation = min(
                    working_token_index,
                    cast(int, heads[working_token_index]),
                )
                second_index_in_relation = max(
                    working_token_index,
                    cast(int, heads[working_token_index]),
                )
                # If this token has children, they will already have been rendered.
                # The line needs to be one character longer than the longest of the
                # children's lines.
                if len(children_lists[working_token_index]) > 0:
                    horizontal_line_lengths[working_token_index] = (
                        max(
                            [
                                horizontal_line_lengths[i]
                                for i in children_lists[working_token_index]
                            ]
                        )
                        + 1
                    )
                else:
                    horizontal_line_lengths[working_token_index] = 1
                for inbetween_index in (
                    i
                    for i in range(
                        first_index_in_relation + 1, second_index_in_relation
                    )
                    if horizontal_line_lengths[i] != 0
                ):
                    horizontal_line_lengths[working_token_index] = max(
                        horizontal_line_lengths[working_token_index],
                        horizontal_line_lengths[inbetween_index]
                        if inbetween_index
                        in children_lists[cast(int, heads[working_token_index])]
                        and inbetween_index not in children_lists[working_token_index]
                        else horizontal_line_lengths[inbetween_index] + 1,
                    )
        max_horizontal_line_length = max(horizontal_line_lengths)
        char_matrix = [
            [SPACE] * max_horizontal_line_length * 2
            for _ in range(sent.start, sent.end)
        ]
        for working_token_index in range(sent.end - sent.start):
            head_token_index = heads[working_token_index]
            if head_token_index is None:
                continue
            first_index_in_relation = min(working_token_index, head_token_index)
            second_index_in_relation = max(working_token_index, head_token_index)
            char_horizontal_line_length = (
                2 * horizontal_line_lengths[working_token_index]
            )

            # Draw the corners of the relation
            char_matrix[first_index_in_relation][char_horizontal_line_length - 1] |= (
                HALF_HORIZONTAL_LINE + LOWER_HALF_VERTICAL_LINE
            )
            char_matrix[second_index_in_relation][char_horizontal_line_length - 1] |= (
                HALF_HORIZONTAL_LINE + UPPER_HALF_VERTICAL_LINE
            )

            # Draw the horizontal line for the governing token
            for working_horizontal_position in range(char_horizontal_line_length - 1):
                if (
                    char_matrix[head_token_index][working_horizontal_position]
                    != FULL_VERTICAL_LINE
                ):
                    char_matrix[head_token_index][
                        working_horizontal_position
                    ] |= FULL_HORIZONTAL_LINE

            # Draw the vertical line for the relation
            for working_vertical_position in range(
                first_index_in_relation + 1, second_index_in_relation
            ):
                if (
                    char_matrix[working_vertical_position][
                        char_horizontal_line_length - 1
                    ]
                    != FULL_HORIZONTAL_LINE
                ):
                    char_matrix[working_vertical_position][
                        char_horizontal_line_length - 1
                    ] |= FULL_VERTICAL_LINE
        for working_token_index in (
            i for i in range(sent.end - sent.start) if heads[i] is not None
        ):
            for working_horizontal_position in range(
                2 * horizontal_line_lengths[working_token_index] - 2, -1, -1
            ):
                if (
                    (
                        char_matrix[working_token_index][working_horizontal_position]
                        == FULL_VERTICAL_LINE
                    )
                    and working_horizontal_position > 1
                    and char_matrix[working_token_index][
                        working_horizontal_position - 2
                    ]
                    == SPACE
                ):
                    # Cross over the existing vertical line, which is owing to a non-projective tree
                    continue
                if (
                    char_matrix[working_token_index][working_horizontal_position]
                    != SPACE
                ):
                    # Draw the arrowhead to the right of what is already there
                    char_matrix[working_token_index][
                        working_horizontal_position + 1
                    ] = ARROWHEAD
                    break
                if working_horizontal_position == 0:
                    # Draw the arrowhead at the boundary of the diagram
                    char_matrix[working_token_index][
                        working_horizontal_position
                    ] = ARROWHEAD
                else:
                    # Fill in the horizontal line for the governed token
                    char_matrix[working_token_index][
                        working_horizontal_position
                    ] |= FULL_HORIZONTAL_LINE
        if root_right:
            return [
                "".join(
                    ROOT_RIGHT_CHARS[
                        char_matrix[vertical_position][horizontal_position]
                    ]
                    for horizontal_position in range((max_horizontal_line_length * 2))
                )
                for vertical_position in range(sent.end - sent.start)
            ]
        else:
            return [
                "".join(
                    ROOT_LEFT_CHARS[char_matrix[vertical_position][horizontal_position]]
                    for horizontal_position in range((max_horizontal_line_length * 2))
                )[::-1]
                for vertical_position in range(sent.end - sent.start)
            ]

    def render_table(
        self, doc: Doc, columns: List[AttributeFormat], spacing: int
    ) -> str:
        """Renders a document as a table.
        TODO: specify a specific portion of the document to display.

        columns: the attribute formats of the columns to display.
                    tree_right and tree_left are magic values for the
                    attributes that render dependency trees where the
                    roots are on the left or right respectively.
        spacing: the number of spaces between each column in the table.
        """
        return_string = ""
        for sent in doc.sents:
            if "tree_right" in (c.attribute for c in columns):
                tree_right = self.render_dependency_tree(sent, True)
            if "tree_left" in (c.attribute for c in columns):
                tree_left = self.render_dependency_tree(sent, False)
            widths = []
            for column in columns:
                # get the values without any color codes
                if column.attribute == "tree_left":
                    width = len(tree_left[0])  # type: ignore
                elif column.attribute == "tree_right":
                    width = len(tree_right[0])  # type: ignore
                else:
                    if len(sent) > 0:
                        width = max(
                            len(column.render(token, ignore_colors=True))
                            for token in sent
                        )
                    else:
                        width = 0
                    if column.max_width is not None:
                        width = min(width, column.max_width)
                width = max(width, len(column.name))
                widths.append(width)
            data = [
                [
                    tree_right[token_index]  # type: ignore
                    if column.attribute == "tree_right"
                    else tree_left[token_index]  # type: ignore
                    if column.attribute == "tree_left"
                    else column.render(token, right_pad_to_length=widths[column_index])
                    for column_index, column in enumerate(columns)
                ]
                for token_index, token in enumerate(sent)
            ]
            header: Optional[List[str]]
            if len([1 for c in columns if len(c.name) > 0]) > 0:
                header = [c.name for c in columns]
            else:
                header = None
            aligns = [c.aligns for c in columns]
            fg_colors = [c.fg_color for c in columns]
            bg_colors = [c.bg_color for c in columns]
            return_string += (
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
        return return_string

    def render_text(self, doc: Doc, attributes: List[AttributeFormat]) -> str:
        """Renders a text interspersed with attribute labels.
        TODO: specify a specific portion of the document to display.

        """
        return_string = ""
        text_attributes = [a for a in attributes if a.attribute == "text"]
        text_attribute = (
            text_attributes[0] if len(text_attributes) > 0 else AttributeFormat("text")
        )
        for token in doc:
            this_token_strings = [""]
            for attribute in (a for a in attributes if a.attribute != "text"):
                attribute_text = attribute.render(
                    token, render_all_colors_within_values=True
                )
                if attribute_text is not None and len(attribute_text) > 0:
                    this_token_strings.append(" " + attribute_text)
            this_token_strings[0] = (
                token.text
                if len(this_token_strings) == 1
                else text_attribute.render(token, render_all_colors_within_values=True)
            )
            this_token_strings.append(token.whitespace_)
            return_string += "".join(this_token_strings)
        return return_string

    def render_instances(
        self,
        doc: Doc,
        *,
        search_attributes: List[AttributeFormat],
        display_columns: List[AttributeFormat],
        group: bool,
        spacing: int,
        surrounding_tokens_height: int,
        surrounding_tokens_fg_color: Union[str, int],
        surrounding_tokens_bg_color: Union[str, int],
    ) -> str:
        """Shows all tokens in a document with specific attribute(s), e.g. entity labels, or attribute value(s), e.g. 'GPE'.
        TODO: specify a specific portion of the document to display.

        search_attributes:              the attribute(s) or attribute value(s) that cause a row to be displayed for a token.
        display_columns:                the attributes that should be displayed in each row.
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
            for attribute in search_attributes:
                value = attribute.render(token, ignore_colors=True)
                if len(value) == 0:
                    return False
            return True

        matched_tokens = [token for token in doc if filter(token)]
        tokens_to_display_indices = [
            index
            for token in matched_tokens
            for index in range(
                token.i - surrounding_tokens_height,
                token.i + surrounding_tokens_height + 1,
            )
            if index >= 0 and index < len(doc)
        ]
        widths = []
        for column in display_columns:
            if len(tokens_to_display_indices) > 0:
                width = max(
                    len(column.render(doc[i], ignore_colors=True))
                    for i in tokens_to_display_indices
                )
            else:
                width = 0
            if column.max_width is not None:
                width = min(width, column.max_width)
            width = max(width, len(column.name))
            widths.append(width)
        if group:
            matched_tokens.sort(
                key=(
                    lambda token: [
                        attribute.render(token, ignore_colors=True)
                        for attribute in search_attributes
                    ]
                )
            )

        rows = []
        token_index_to_display = -1
        for matched_token_index, matched_token in enumerate(matched_tokens):
            if surrounding_tokens_height > 0:
                surrounding_start_index = max(
                    0, matched_token.i - surrounding_tokens_height
                )
                if token_index_to_display + 1 == matched_token.i:
                    surrounding_start_index = token_index_to_display + 1
                surrounding_end_index = min(
                    len(doc), matched_token.i + surrounding_tokens_height + 1
                )
                if (
                    matched_token_index + 1 < len(matched_tokens)
                    and matched_token.i + 1 == matched_tokens[matched_token_index + 1].i
                ):
                    surrounding_end_index = matched_token.i + 1

            else:
                surrounding_start_index = matched_token.i
                surrounding_end_index = surrounding_start_index + 1
            for token_index_to_display in range(
                surrounding_start_index, surrounding_end_index
            ):
                if token_index_to_display == matched_token.i:
                    rows.append(
                        [
                            column.render(
                                matched_token,
                                right_pad_to_length=widths[column_index],
                            )
                            for column_index, column in enumerate(display_columns)
                        ]
                    )
                else:
                    rows.append(
                        [
                            column.render(
                                doc[token_index_to_display],
                                whole_row_fg_color=surrounding_tokens_fg_color,
                                whole_row_bg_color=surrounding_tokens_bg_color,
                                right_pad_to_length=widths[column_index],
                            )
                            for column_index, column in enumerate(display_columns)
                        ]
                    )
            if (
                matched_token_index + 1 < len(matched_tokens)
                and token_index_to_display + 1
                != matched_tokens[matched_token_index + 1].i
            ):
                rows.append([])
        header: Optional[List[str]]
        if len([1 for c in display_columns if len(c.name) > 0]) > 0:
            header = [c.name for c in display_columns]
        else:
            header = None
        aligns = [c.aligns for c in display_columns]
        fg_colors = [c.fg_color for c in display_columns]
        bg_colors = [c.bg_color for c in display_columns]
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
