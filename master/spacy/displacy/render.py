from typing import Any, Dict, List, Optional, Tuple, Union
import uuid
import itertools

from ..errors import Errors
from ..util import escape_html, minify_html, registry
from .templates import TPL_DEP_ARCS, TPL_DEP_SVG, TPL_DEP_WORDS
from .templates import TPL_DEP_WORDS_LEMMA, TPL_ENT, TPL_ENT_RTL, TPL_ENTS
from .templates import TPL_FIGURE, TPL_KB_LINK, TPL_PAGE, TPL_SPAN
from .templates import TPL_SPAN_RTL, TPL_SPAN_SLICE, TPL_SPAN_SLICE_RTL
from .templates import TPL_SPAN_START, TPL_SPAN_START_RTL, TPL_SPANS
from .templates import TPL_TITLE

DEFAULT_LANG = "en"
DEFAULT_DIR = "ltr"
DEFAULT_ENTITY_COLOR = "#ddd"
DEFAULT_LABEL_COLORS = {
    "ORG": "#7aecec",
    "PRODUCT": "#bfeeb7",
    "GPE": "#feca74",
    "LOC": "#ff9561",
    "PERSON": "#aa9cfc",
    "NORP": "#c887fb",
    "FAC": "#9cc9cc",
    "EVENT": "#ffeb80",
    "LAW": "#ff8197",
    "LANGUAGE": "#ff8197",
    "WORK_OF_ART": "#f0d0ff",
    "DATE": "#bfe1d9",
    "TIME": "#bfe1d9",
    "MONEY": "#e4e7d2",
    "QUANTITY": "#e4e7d2",
    "ORDINAL": "#e4e7d2",
    "CARDINAL": "#e4e7d2",
    "PERCENT": "#e4e7d2",
}


class SpanRenderer:
    """Render Spans as SVGs."""

    style = "span"

    def __init__(self, options: Dict[str, Any] = {}) -> None:
        """Initialise span renderer

        options (dict): Visualiser-specific options (colors, spans)
        """
        # Set up the colors and overall look
        colors = dict(DEFAULT_LABEL_COLORS)
        user_colors = registry.displacy_colors.get_all()
        for user_color in user_colors.values():
            if callable(user_color):
                # Since this comes from the function registry, we want to make
                # sure we support functions that *return* a dict of colors
                user_color = user_color()
            if not isinstance(user_color, dict):
                raise ValueError(Errors.E925.format(obj=type(user_color)))
            colors.update(user_color)
        colors.update(options.get("colors", {}))
        self.default_color = DEFAULT_ENTITY_COLOR
        self.colors = {label.upper(): color for label, color in colors.items()}

        # Set up how the text and labels will be rendered
        self.direction = DEFAULT_DIR
        self.lang = DEFAULT_LANG
        # These values are in px
        self.top_offset = options.get("top_offset", 40)
        # This is how far under the top offset the span labels appear
        self.span_label_offset = options.get("span_label_offset", 20)
        self.offset_step = options.get("top_offset_step", 17)

        # Set up which templates will be used
        template = options.get("template")
        if template:
            self.span_template = template["span"]
            self.span_slice_template = template["slice"]
            self.span_start_template = template["start"]
        else:
            if self.direction == "rtl":
                self.span_template = TPL_SPAN_RTL
                self.span_slice_template = TPL_SPAN_SLICE_RTL
                self.span_start_template = TPL_SPAN_START_RTL
            else:
                self.span_template = TPL_SPAN
                self.span_slice_template = TPL_SPAN_SLICE
                self.span_start_template = TPL_SPAN_START

    def render(
        self, parsed: List[Dict[str, Any]], page: bool = False, minify: bool = False
    ) -> str:
        """Render complete markup.

        parsed (list): Dependency parses to render.
        page (bool): Render parses wrapped as full HTML page.
        minify (bool): Minify HTML markup.
        RETURNS (str): Rendered SVG or HTML markup.
        """
        rendered = []
        for i, p in enumerate(parsed):
            if i == 0:
                settings = p.get("settings", {})
                self.direction = settings.get("direction", DEFAULT_DIR)
                self.lang = settings.get("lang", DEFAULT_LANG)
            rendered.append(self.render_spans(p["tokens"], p["spans"], p.get("title")))

        if page:
            docs = "".join([TPL_FIGURE.format(content=doc) for doc in rendered])
            markup = TPL_PAGE.format(content=docs, lang=self.lang, dir=self.direction)
        else:
            markup = "".join(rendered)
        if minify:
            return minify_html(markup)
        return markup

    def render_spans(
        self,
        tokens: List[str],
        spans: List[Dict[str, Any]],
        title: Optional[str],
    ) -> str:
        """Render span types in text.

        Spans are rendered per-token, this means that for each token, we check if it's part
        of a span slice (a member of a span type) or a span start (the starting token of a
        given span type).

        tokens (list): Individual tokens in the text
        spans (list): Individual entity spans and their start, end, label, kb_id and kb_url.
        title (str / None): Document title set in Doc.user_data['title'].
        """
        per_token_info = []
        # we must sort so that we can correctly describe when spans need to "stack"
        # which is determined by their start token, then span length (longer spans on top),
        # then break any remaining ties with the span label
        spans = sorted(
            spans,
            key=lambda s: (
                s["start_token"],
                -(s["end_token"] - s["start_token"]),
                s["label"],
            ),
        )
        for s in spans:
            # this is the vertical 'slot' that the span will be rendered in
            # vertical_position = span_label_offset + (offset_step * (slot - 1))
            s["render_slot"] = 0
        for idx, token in enumerate(tokens):
            # Identify if a token belongs to a Span (and which) and if it's a
            # start token of said Span. We'll use this for the final HTML render
            token_markup: Dict[str, Any] = {}
            token_markup["text"] = token
            concurrent_spans = 0
            entities = []
            for span in spans:
                ent = {}
                if span["start_token"] <= idx < span["end_token"]:
                    concurrent_spans += 1
                    span_start = idx == span["start_token"]
                    ent["label"] = span["label"]
                    ent["is_start"] = span_start
                    if span_start:
                        # When the span starts, we need to know how many other
                        # spans are on the 'span stack' and will be rendered.
                        # This value becomes the vertical render slot for this entire span
                        span["render_slot"] = concurrent_spans
                    ent["render_slot"] = span["render_slot"]
                    kb_id = span.get("kb_id", "")
                    kb_url = span.get("kb_url", "#")
                    ent["kb_link"] = (
                        TPL_KB_LINK.format(kb_id=kb_id, kb_url=kb_url) if kb_id else ""
                    )
                    entities.append(ent)
                else:
                    # We don't specifically need to do this since we loop
                    # over tokens and spans sorted by their start_token,
                    # so we'll never use a span again after the last token it appears in,
                    # but if we were to use these spans again we'd want to make sure
                    # this value was reset correctly.
                    span["render_slot"] = 0
            token_markup["entities"] = entities
            per_token_info.append(token_markup)
        markup = self._render_markup(per_token_info)
        markup = TPL_SPANS.format(content=markup, dir=self.direction)
        if title:
            markup = TPL_TITLE.format(title=title) + markup
        return markup

    def _render_markup(self, per_token_info: List[Dict[str, Any]]) -> str:
        """Render the markup from per-token information"""
        markup = ""
        for token in per_token_info:
            entities = sorted(token["entities"], key=lambda d: d["render_slot"])
            # Whitespace tokens disrupt the vertical space (no line height) so that the
            # span indicators get misaligned. We don't render them as individual
            # tokens anyway, so we'll just not display a span indicator either.
            is_whitespace = token["text"].strip() == ""
            if entities and not is_whitespace:
                slices = self._get_span_slices(token["entities"])
                starts = self._get_span_starts(token["entities"])
                total_height = (
                    self.top_offset
                    + self.span_label_offset
                    + (self.offset_step * (len(entities) - 1))
                )
                markup += self.span_template.format(
                    text=token["text"],
                    span_slices=slices,
                    span_starts=starts,
                    total_height=total_height,
                )
            else:
                markup += escape_html(token["text"] + " ")
        return markup

    def _get_span_slices(self, entities: List[Dict]) -> str:
        """Get the rendered markup of all Span slices"""
        span_slices = []
        for entity in entities:
            # rather than iterate over multiples of offset_step, we use entity['render_slot']
            # to determine the vertical position, since that tells where
            # the span starts vertically so we can extend it horizontally,
            # past other spans that might have already ended
            color = self.colors.get(entity["label"].upper(), self.default_color)
            top_offset = self.top_offset + (
                self.offset_step * (entity["render_slot"] - 1)
            )
            span_slice = self.span_slice_template.format(
                bg=color,
                top_offset=top_offset,
            )
            span_slices.append(span_slice)
        return "".join(span_slices)

    def _get_span_starts(self, entities: List[Dict]) -> str:
        """Get the rendered markup of all Span start tokens"""
        span_starts = []
        for entity in entities:
            color = self.colors.get(entity["label"].upper(), self.default_color)
            top_offset = self.top_offset + (
                self.offset_step * (entity["render_slot"] - 1)
            )
            span_start = (
                self.span_start_template.format(
                    bg=color,
                    top_offset=top_offset,
                    label=entity["label"],
                    kb_link=entity["kb_link"],
                )
                if entity["is_start"]
                else ""
            )
            span_starts.append(span_start)
        return "".join(span_starts)


class DependencyRenderer:
    """Render dependency parses as SVGs."""

    style = "dep"

    def __init__(self, options: Dict[str, Any] = {}) -> None:
        """Initialise dependency renderer.

        options (dict): Visualiser-specific options (compact, word_spacing,
            arrow_spacing, arrow_width, arrow_stroke, distance, offset_x,
            color, bg, font)
        """
        self.compact = options.get("compact", False)
        self.word_spacing = options.get("word_spacing", 45)
        self.arrow_spacing = options.get("arrow_spacing", 12 if self.compact else 20)
        self.arrow_width = options.get("arrow_width", 6 if self.compact else 10)
        self.arrow_stroke = options.get("arrow_stroke", 2)
        self.distance = options.get("distance", 150 if self.compact else 175)
        self.offset_x = options.get("offset_x", 50)
        self.color = options.get("color", "#000000")
        self.bg = options.get("bg", "#ffffff")
        self.font = options.get("font", "Arial")
        self.direction = DEFAULT_DIR
        self.lang = DEFAULT_LANG

    def render(
        self, parsed: List[Dict[str, Any]], page: bool = False, minify: bool = False
    ) -> str:
        """Render complete markup.

        parsed (list): Dependency parses to render.
        page (bool): Render parses wrapped as full HTML page.
        minify (bool): Minify HTML markup.
        RETURNS (str): Rendered SVG or HTML markup.
        """
        # Create a random ID prefix to make sure parses don't receive the
        # same ID, even if they're identical
        id_prefix = uuid.uuid4().hex
        rendered = []
        for i, p in enumerate(parsed):
            if i == 0:
                settings = p.get("settings", {})
                self.direction = settings.get("direction", DEFAULT_DIR)
                self.lang = settings.get("lang", DEFAULT_LANG)
            render_id = f"{id_prefix}-{i}"
            svg = self.render_svg(render_id, p["words"], p["arcs"])
            rendered.append(svg)
        if page:
            content = "".join([TPL_FIGURE.format(content=svg) for svg in rendered])
            markup = TPL_PAGE.format(
                content=content, lang=self.lang, dir=self.direction
            )
        else:
            markup = "".join(rendered)
        if minify:
            return minify_html(markup)
        return markup

    def render_svg(
        self,
        render_id: Union[int, str],
        words: List[Dict[str, Any]],
        arcs: List[Dict[str, Any]],
    ) -> str:
        """Render SVG.

        render_id (Union[int, str]): Unique ID, typically index of document.
        words (list): Individual words and their tags.
        arcs (list): Individual arcs and their start, end, direction and label.
        RETURNS (str): Rendered SVG markup.
        """
        self.levels = self.get_levels(arcs)
        self.highest_level = max(self.levels.values(), default=0)
        self.offset_y = self.distance / 2 * self.highest_level + self.arrow_stroke
        self.width = self.offset_x + len(words) * self.distance
        self.height = self.offset_y + 3 * self.word_spacing
        self.id = render_id
        words_svg = [
            self.render_word(w["text"], w["tag"], w.get("lemma", None), i)
            for i, w in enumerate(words)
        ]
        arcs_svg = [
            self.render_arrow(a["label"], a["start"], a["end"], a["dir"], i)
            for i, a in enumerate(arcs)
        ]
        content = "".join(words_svg) + "".join(arcs_svg)
        return TPL_DEP_SVG.format(
            id=self.id,
            width=self.width,
            height=self.height,
            color=self.color,
            bg=self.bg,
            font=self.font,
            content=content,
            dir=self.direction,
            lang=self.lang,
        )

    def render_word(self, text: str, tag: str, lemma: str, i: int) -> str:
        """Render individual word.

        text (str): Word text.
        tag (str): Part-of-speech tag.
        i (int): Unique ID, typically word index.
        RETURNS (str): Rendered SVG markup.
        """
        y = self.offset_y + self.word_spacing
        x = self.offset_x + i * self.distance
        if self.direction == "rtl":
            x = self.width - x
        html_text = escape_html(text)
        if lemma is not None:
            return TPL_DEP_WORDS_LEMMA.format(
                text=html_text, tag=tag, lemma=lemma, x=x, y=y
            )
        return TPL_DEP_WORDS.format(text=html_text, tag=tag, x=x, y=y)

    def render_arrow(
        self, label: str, start: int, end: int, direction: str, i: int
    ) -> str:
        """Render individual arrow.

        label (str): Dependency label.
        start (int): Index of start word.
        end (int): Index of end word.
        direction (str): Arrow direction, 'left' or 'right'.
        i (int): Unique ID, typically arrow index.
        RETURNS (str): Rendered SVG markup.
        """
        if start < 0 or end < 0:
            error_args = dict(start=start, end=end, label=label, dir=direction)
            raise ValueError(Errors.E157.format(**error_args))
        level = self.levels[(start, end, label)]
        x_start = self.offset_x + start * self.distance + self.arrow_spacing
        if self.direction == "rtl":
            x_start = self.width - x_start
        y = self.offset_y
        x_end = (
            self.offset_x
            + (end - start) * self.distance
            + start * self.distance
            - self.arrow_spacing * (self.highest_level - level) / 4
        )
        if self.direction == "rtl":
            x_end = self.width - x_end
        y_curve = self.offset_y - level * self.distance / 2
        if self.compact:
            y_curve = self.offset_y - level * self.distance / 6
        if y_curve == 0 and max(self.levels.values(), default=0) > 5:
            y_curve = -self.distance
        arrowhead = self.get_arrowhead(direction, x_start, y, x_end)
        arc = self.get_arc(x_start, y, y_curve, x_end)
        label_side = "right" if self.direction == "rtl" else "left"
        return TPL_DEP_ARCS.format(
            id=self.id,
            i=i,
            stroke=self.arrow_stroke,
            head=arrowhead,
            label=label,
            label_side=label_side,
            arc=arc,
        )

    def get_arc(self, x_start: int, y: int, y_curve: int, x_end: int) -> str:
        """Render individual arc.

        x_start (int): X-coordinate of arrow start point.
        y (int): Y-coordinate of arrow start and end point.
        y_curve (int): Y-corrdinate of Cubic Bézier y_curve point.
        x_end (int): X-coordinate of arrow end point.
        RETURNS (str): Definition of the arc path ('d' attribute).
        """
        template = "M{x},{y} C{x},{c} {e},{c} {e},{y}"
        if self.compact:
            template = "M{x},{y} {x},{c} {e},{c} {e},{y}"
        return template.format(x=x_start, y=y, c=y_curve, e=x_end)

    def get_arrowhead(self, direction: str, x: int, y: int, end: int) -> str:
        """Render individual arrow head.

        direction (str): Arrow direction, 'left' or 'right'.
        x (int): X-coordinate of arrow start point.
        y (int): Y-coordinate of arrow start and end point.
        end (int): X-coordinate of arrow end point.
        RETURNS (str): Definition of the arrow head path ('d' attribute).
        """
        if direction == "left":
            p1, p2, p3 = (x, x - self.arrow_width + 2, x + self.arrow_width - 2)
        else:
            p1, p2, p3 = (end, end + self.arrow_width - 2, end - self.arrow_width + 2)
        return f"M{p1},{y + 2} L{p2},{y - self.arrow_width} {p3},{y - self.arrow_width}"

    def get_levels(self, arcs: List[Dict[str, Any]]) -> Dict[Tuple[int, int, str], int]:
        """Calculate available arc height "levels".
        Used to calculate arrow heights dynamically and without wasting space.

        args (list): Individual arcs and their start, end, direction and label.
        RETURNS (dict): Arc levels keyed by (start, end, label).
        """
        arcs = [dict(t) for t in {tuple(sorted(arc.items())) for arc in arcs}]
        length = max([arc["end"] for arc in arcs], default=0)
        max_level = [0] * length
        levels = {}
        for arc in sorted(arcs, key=lambda arc: arc["end"] - arc["start"]):
            level = max(max_level[arc["start"] : arc["end"]]) + 1
            for i in range(arc["start"], arc["end"]):
                max_level[i] = level
            levels[(arc["start"], arc["end"], arc["label"])] = level
        return levels


class EntityRenderer:
    """Render named entities as HTML."""

    style = "ent"

    def __init__(self, options: Dict[str, Any] = {}) -> None:
        """Initialise entity renderer.

        options (dict): Visualiser-specific options (colors, ents)
        """
        colors = dict(DEFAULT_LABEL_COLORS)
        user_colors = registry.displacy_colors.get_all()
        for user_color in user_colors.values():
            if callable(user_color):
                # Since this comes from the function registry, we want to make
                # sure we support functions that *return* a dict of colors
                user_color = user_color()
            if not isinstance(user_color, dict):
                raise ValueError(Errors.E925.format(obj=type(user_color)))
            colors.update(user_color)
        colors.update(options.get("colors", {}))
        self.default_color = DEFAULT_ENTITY_COLOR
        self.colors = {label.upper(): color for label, color in colors.items()}
        self.ents = options.get("ents", None)
        if self.ents is not None:
            self.ents = [ent.upper() for ent in self.ents]
        self.direction = DEFAULT_DIR
        self.lang = DEFAULT_LANG
        template = options.get("template")
        if template:
            self.ent_template = template
        else:
            if self.direction == "rtl":
                self.ent_template = TPL_ENT_RTL
            else:
                self.ent_template = TPL_ENT

    def render(
        self, parsed: List[Dict[str, Any]], page: bool = False, minify: bool = False
    ) -> str:
        """Render complete markup.

        parsed (list): Dependency parses to render.
        page (bool): Render parses wrapped as full HTML page.
        minify (bool): Minify HTML markup.
        RETURNS (str): Rendered SVG or HTML markup.
        """
        rendered = []
        for i, p in enumerate(parsed):
            if i == 0:
                settings = p.get("settings", {})
                self.direction = settings.get("direction", DEFAULT_DIR)
                self.lang = settings.get("lang", DEFAULT_LANG)
            rendered.append(self.render_ents(p["text"], p["ents"], p.get("title")))
        if page:
            docs = "".join([TPL_FIGURE.format(content=doc) for doc in rendered])
            markup = TPL_PAGE.format(content=docs, lang=self.lang, dir=self.direction)
        else:
            markup = "".join(rendered)
        if minify:
            return minify_html(markup)
        return markup

    def render_ents(
        self, text: str, spans: List[Dict[str, Any]], title: Optional[str]
    ) -> str:
        """Render entities in text.

        text (str): Original text.
        spans (list): Individual entity spans and their start, end, label, kb_id and kb_url.
        title (str / None): Document title set in Doc.user_data['title'].
        """
        markup = ""
        offset = 0
        for span in spans:
            label = span["label"]
            start = span["start"]
            end = span["end"]
            kb_id = span.get("kb_id", "")
            kb_url = span.get("kb_url", "#")
            kb_link = TPL_KB_LINK.format(kb_id=kb_id, kb_url=kb_url) if kb_id else ""
            additional_params = span.get("params", {})
            entity = escape_html(text[start:end])
            fragments = text[offset:start].split("\n")
            for i, fragment in enumerate(fragments):
                markup += escape_html(fragment)
                if len(fragments) > 1 and i != len(fragments) - 1:
                    markup += "</br>"
            if self.ents is None or label.upper() in self.ents:
                color = self.colors.get(label.upper(), self.default_color)
                ent_settings = {
                    "label": label,
                    "text": entity,
                    "bg": color,
                    "kb_link": kb_link,
                }
                ent_settings.update(additional_params)
                markup += self.ent_template.format(**ent_settings)
            else:
                markup += entity
            offset = end
        fragments = text[offset:].split("\n")
        for i, fragment in enumerate(fragments):
            markup += escape_html(fragment)
            if len(fragments) > 1 and i != len(fragments) - 1:
                markup += "</br>"
        markup = TPL_ENTS.format(content=markup, dir=self.direction)
        if title:
            markup = TPL_TITLE.format(title=title) + markup
        return markup
