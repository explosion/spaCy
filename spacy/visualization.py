from spacy.tokens import Doc, Token
from spacy.util import working_dir

HORIZONTAL_LINE_PART_AWAY_FROM_ROOT = 1
HORIZONTAL_LINE_PART_TOWARDS_ROOT = 2
UPPER_VERTICAL_LINE_PART = 4
LOWER_VERTICAL_LINE_PART = 8
ARROWHEAD = 16

SPACE = 0
HORIZONTAL_LINE = 3
VERTICAL_LINE = 12

ROOT_RIGHT_CHARS = {
    0: " ",
    3: "═",
    5: "╝",
    7: "╩",
    9: "╗",
    11: "╦",
    12: "║",
    13: "╣",
    15: "╬",
    16: "<",
}

ROOT_LEFT_CHARS = {
    0: " ",
    3: "═",
    5: "╚",
    7: "╩",
    9: "╔",
    11: "╦",
    12: "║",
    13: "╠",
    15: "╬",
    16: ">",
}


class Visualizer:
    @staticmethod
    def render_dependency_trees(doc: Doc) -> list[str]:
        """
        Returns an ASCII rendering of the document with a dependency tree for each sentence. The
        dependency tree output for a given token has the same index within the output list of
        strings as that token within the input document.

        Adapted from https://github.com/KoichiYasuoka/deplacy
        """
        heads = [
            None
            if token.dep_.lower() == "root" or token.head.i == token.i
            else token.head.i
            for token in doc
        ]
        children_lists = [[] for _ in range(len(doc))]
        for child, head in enumerate(heads):
            if head is not None:
                children_lists[head].append(child)
        all_indices_ordered_by_column = []
        indices_in_current_column = [i for i, h in enumerate(heads) if h is None]
        while len(indices_in_current_column) > 0:
            all_indices_ordered_by_column = (
                indices_in_current_column + all_indices_ordered_by_column
            )
            indices_in_current_column = [
                i
                for index_in_current_column in indices_in_current_column
                for i in children_lists[index_in_current_column]
                if i not in all_indices_ordered_by_column
            ]
        # -1: root token with no arrow; 0: length not yet set
        horizontal_line_lengths = [
            -1
            if heads[i] is None
            else 1
            if len(children_lists[i]) == 0 and abs(heads[i] - i) == 1
            else 0
            for i in range(len(doc))
        ]
        while 0 in horizontal_line_lengths:
            for working_token_index in (
                i
                for i in all_indices_ordered_by_column
                if horizontal_line_lengths[i] == 0
            ):
                first_index_in_relation = min(
                    working_token_index,
                    heads[working_token_index],
                )
                second_index_in_relation = max(
                    working_token_index,
                    heads[working_token_index],
                )
                if len(children_lists[working_token_index]) > 0:
                    working_horizontal_line_length = (
                        max(
                            [
                                horizontal_line_lengths[i]
                                for i in children_lists[working_token_index]
                            ]
                        )
                        + 1
                    )
                else:
                    working_horizontal_line_length = 1
                for inbetween_index in (
                    i
                    for i in range(
                        first_index_in_relation + 1, second_index_in_relation
                    )
                    if i not in children_lists[working_token_index]
                    and horizontal_line_lengths[i] != 0
                ):
                    working_horizontal_line_length = max(
                        working_horizontal_line_length,
                        horizontal_line_lengths[inbetween_index]
                        if inbetween_index in children_lists[heads[working_token_index]]
                        else horizontal_line_lengths[inbetween_index] + 1,
                    )
                    for child_horizontal_line_length in (
                        horizontal_line_lengths[i]
                        for i in children_lists[working_token_index]
                        if (i < first_index_in_relation or i > second_index_in_relation)
                        and horizontal_line_lengths[i] != 0
                    ):
                        working_horizontal_line_length = max(
                            working_horizontal_line_length,
                            child_horizontal_line_length + 1,
                        )
                horizontal_line_lengths[
                    working_token_index
                ] = working_horizontal_line_length
        print(horizontal_line_lengths)

        max_horizontal_line_length = max(horizontal_line_lengths)
        char_matrix = [
            [SPACE] * max_horizontal_line_length * 2 for _ in range(len(doc))
        ]
        for working_token_index in range(len(doc)):
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
                HORIZONTAL_LINE_PART_AWAY_FROM_ROOT + LOWER_VERTICAL_LINE_PART
            )
            char_matrix[second_index_in_relation][char_horizontal_line_length - 1] |= (
                HORIZONTAL_LINE_PART_AWAY_FROM_ROOT + UPPER_VERTICAL_LINE_PART
            )

            # Draw the horizontal line for the governing token
            for working_horizontal_position in range(char_horizontal_line_length - 1):
                if (
                    char_matrix[head_token_index][working_horizontal_position]
                    != VERTICAL_LINE
                ):
                    char_matrix[head_token_index][
                        working_horizontal_position
                    ] |= HORIZONTAL_LINE

            # Draw the vertical line for the relation
            for working_vertical_position in range(
                first_index_in_relation + 1, second_index_in_relation
            ):
                if (
                    char_matrix[working_vertical_position][
                        char_horizontal_line_length - 1
                    ]
                    != HORIZONTAL_LINE
                ):
                    char_matrix[working_vertical_position][
                        char_horizontal_line_length - 1
                    ] |= VERTICAL_LINE
        for working_token_index in (i for i in range(len(doc)) if heads[i] is not None):
            for working_horizontal_position in range(
                2 * horizontal_line_lengths[working_token_index] - 2, -1, -1
            ):
                if (
                    char_matrix[working_token_index][working_horizontal_position]
                    == VERTICAL_LINE) and working_horizontal_position > 1 and char_matrix[working_token_index][working_horizontal_position - 2] == SPACE: 
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
                        working_horizontal_position] = ARROWHEAD
                else:
                    # Fill in the horizontal line for the governed token
                    char_matrix[working_token_index][
                        working_horizontal_position
                    ] |= HORIZONTAL_LINE
        return [
            "".join(
                ROOT_RIGHT_CHARS[char_matrix[vertical_position][horizontal_position]]
                for horizontal_position in range((max_horizontal_line_length * 2))
            )
            for vertical_position in range(len(doc))
        ]


import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("I saw a horse yesterday that was injured")

lines = Visualizer().render_dependency_trees(doc)
for line in lines:
    print(line)
