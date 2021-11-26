from spacy.tokens import Doc, Token


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
            -1
            if token.dep_.lower() == "root" or token.head.i == token.i
            else token.head.i
            for token in doc
        ]
        children_lists = [[] for _ in range(len(doc))]
        for child, head in enumerate(h for h in heads):
            if head != -1:
                children_lists[head].append(child)
        all_indices_ordered_by_column = []
        indices_in_current_column = [i for i, h in enumerate(heads) if h == -1]
        while len(indices_in_current_column) > 0:
            all_indices_ordered_by_column.extend(indices_in_current_column)
            indices_in_current_column = [
                i
                for index_in_current_column in indices_in_current_column
                for i in children_lists[index_in_current_column]
                if i not in all_indices_ordered_by_column
            ]
        all_indices_ordered_by_column = reversed(all_indices_ordered_by_column)
        # -1: no arrow; None: not yet set
        horizontal_arrow_positions = [
            -1
            if heads[i] == -1
            else 0
            if len(children_lists[i]) == 0 and abs(heads[i] - i) == 1
            else None
            for i in range(len(doc))
        ]
        while None in horizontal_arrow_positions:
            for working_token_index in (
                i
                for i in all_indices_ordered_by_column
                if horizontal_arrow_positions[i] is None
            ):
                first_index_in_relation = min(
                    working_token_index,
                    heads[working_token_index],
                )
                second_index_in_relation = max(
                    working_token_index,
                    heads[working_token_index],
                )
                inbetween_indexes = range(
                    first_index_in_relation + 1, second_index_in_relation
                )
                inbetween_horizontal_arrow_positions = horizontal_arrow_positions[
                    first_index_in_relation + 1 : second_index_in_relation
                ]
                if (
                    -1 in inbetween_horizontal_arrow_positions
                    and None in inbetween_horizontal_arrow_positions
                ):
                    continue
                if None in (
                    horizontal_arrow_positions[i]
                    for i in children_lists[working_token_index]
                ):
                    continue
                if len(children_lists[working_token_index]) > 0:
                    working_horizontal_arrow_position = (
                        max(
                            [
                                horizontal_arrow_positions[i]
                                for i in children_lists[working_token_index]
                            ]
                        )
                        + 1
                    )
                else:
                    working_horizontal_arrow_position = -1
                for inbetween_index in (
                    i
                    for i in inbetween_indexes
                    if i not in children_lists[working_token_index]
                    and horizontal_arrow_positions[i] is not None
                ):
                    working_horizontal_arrow_position = max(
                        working_horizontal_arrow_position,
                        horizontal_arrow_positions[inbetween_index]
                        if inbetween_index in children_lists[heads[working_token_index]]
                        else horizontal_arrow_positions[inbetween_index] + 1,
                    )
                    for child_horizontal_arrow_position in (
                        horizontal_arrow_positions[i]
                        for i in children_lists[working_token_index]
                        if (i < first_index_in_relation or i > second_index_in_relation)
                        and horizontal_arrow_positions[i] is not None
                    ):
                        working_horizontal_arrow_position = max(
                            working_horizontal_arrow_position,
                            child_horizontal_arrow_position + 1,
                        )
                if working_horizontal_arrow_position > -1:
                    horizontal_arrow_positions[
                        working_token_index
                    ] = working_horizontal_arrow_position
        print(horizontal_arrow_positions)


import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("I saw a horse yesterday that was injured.")
Visualizer().render_dependency_trees(doc)
