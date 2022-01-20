from typing import Dict, Any, List, Optional, Union
import uuid

from .templates import TPL_DEP_SVG, TPL_DEP_WORDS, TPL_DEP_WORDS_LEMMA, TPL_DEP_ARCS
from .templates import TPL_ENT, TPL_ENT_RTL, TPL_FIGURE, TPL_TITLE, TPL_PAGE
from .templates import TPL_ENTS, TPL_KB_LINK
from ..util import minify_html, escape_html, registry
from ..errors import Errors


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
        self.highest_level = len(self.levels)
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
        level = self.levels.index(end - start) + 1
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
        if y_curve == 0 and len(self.levels) > 5:
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

    def get_levels(self, arcs: List[Dict[str, Any]]) -> List[int]:
        """Calculate available arc height "levels".
        Used to calculate arrow heights dynamically and without wasting space.

        args (list): Individual arcs and their start, end, direction and label.
        RETURNS (list): Arc levels sorted from lowest to highest.
        """
        levels = set(map(lambda arc: arc["end"] - arc["start"], arcs))
        return sorted(list(levels))


class EntityRenderer:
    """Render named entities as HTML."""

    style = "ent"

    def __init__(self, options: Dict[str, Any] = {}) -> None:
        """Initialise dependency renderer.

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
        RETURNS (str): Rendered HTML markup.
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
