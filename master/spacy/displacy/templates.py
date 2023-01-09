# Setting explicit height and max-width: none on the SVG is required for
# Jupyter to render it properly in a cell

TPL_DEP_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" xml:lang="{lang}" id="{id}" class="displacy" width="{width}" height="{height}" direction="{dir}" style="max-width: none; height: {height}px; color: {color}; background: {bg}; font-family: {font}; direction: {dir}">{content}</svg>
"""


TPL_DEP_WORDS = """
<text class="displacy-token" fill="currentColor" text-anchor="middle" y="{y}">
    <tspan class="displacy-word" fill="currentColor" x="{x}">{text}</tspan>
    <tspan class="displacy-tag" dy="2em" fill="currentColor" x="{x}">{tag}</tspan>
</text>
"""


TPL_DEP_WORDS_LEMMA = """
<text class="displacy-token" fill="currentColor" text-anchor="middle" y="{y}">
    <tspan class="displacy-word" fill="currentColor" x="{x}">{text}</tspan>
    <tspan class="displacy-lemma" dy="2em" fill="currentColor" x="{x}">{lemma}</tspan>
    <tspan class="displacy-tag" dy="2em" fill="currentColor" x="{x}">{tag}</tspan>
</text>
"""


TPL_DEP_ARCS = """
<g class="displacy-arrow">
    <path class="displacy-arc" id="arrow-{id}-{i}" stroke-width="{stroke}px" d="{arc}" fill="none" stroke="currentColor"/>
    <text dy="1.25em" style="font-size: 0.8em; letter-spacing: 1px">
        <textPath xlink:href="#arrow-{id}-{i}" class="displacy-label" startOffset="50%" side="{label_side}" fill="currentColor" text-anchor="middle">{label}</textPath>
    </text>
    <path class="displacy-arrowhead" d="{head}" fill="currentColor"/>
</g>
"""


TPL_FIGURE = """
<figure style="margin-bottom: 6rem">{content}</figure>
"""

TPL_TITLE = """
<h2 style="margin: 0">{title}</h2>
"""


TPL_ENTS = """
<div class="entities" style="line-height: 2.5; direction: {dir}">{content}</div>
"""


TPL_ENT = """
<mark class="entity" style="background: {bg}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">
    {text}
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-left: 0.5rem">{label}{kb_link}</span>
</mark>
"""

TPL_ENT_RTL = """
<mark class="entity" style="background: {bg}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em">
    {text}
    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; vertical-align: middle; margin-right: 0.5rem">{label}{kb_link}</span>
</mark>
"""

TPL_SPANS = """
<div class="spans" style="line-height: 2.5; direction: {dir}">{content}</div>
"""

TPL_SPAN = """
<span style="font-weight: bold; display: inline-block; position: relative; height: {total_height}px;">
    {text}
    {span_slices}
    {span_starts}
</span>
"""

TPL_SPAN_SLICE = """
<span style="background: {bg}; top: {top_offset}px; height: 4px; left: -1px; width: calc(100% + 2px); position: absolute;">
</span>
"""


TPL_SPAN_START = """
<span style="background: {bg}; top: {top_offset}px; height: 4px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;">
    <span style="background: {bg}; z-index: 10; color: #000; top: -0.5em; padding: 2px 3px; position: absolute; font-size: 0.6em; font-weight: bold; line-height: 1; border-radius: 3px">
        {label}{kb_link}
    </span>
</span>

"""

TPL_SPAN_RTL = """
<span style="font-weight: bold; display: inline-block; position: relative;">
    {text}
    {span_slices}
    {span_starts}
</span>
"""

TPL_SPAN_SLICE_RTL = """
<span style="background: {bg}; top: {top_offset}px; height: 4px; left: -1px; width: calc(100% + 2px); position: absolute;">
</span>
"""

TPL_SPAN_START_RTL = """
<span style="background: {bg}; top: {top_offset}px; height: 4px; border-top-left-radius: 3px; border-bottom-left-radius: 3px; left: -1px; width: calc(100% + 2px); position: absolute;">
    <span style="background: {bg}; z-index: 10; color: #000; top: -0.5em; padding: 2px 3px; position: absolute; font-size: 0.6em; font-weight: bold; line-height: 1; border-radius: 3px">
        {label}{kb_link}
    </span>
</span>
"""


# Important: this needs to start with a space!
TPL_KB_LINK = """
 <a style="text-decoration: none; color: inherit; font-weight: normal" href="{kb_url}">{kb_id}</a>
"""


TPL_PAGE = """
<!DOCTYPE html>
<html lang="{lang}">
    <head>
        <title>displaCy</title>
    </head>

    <body style="font-size: 16px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; padding: 4rem 2rem; direction: {dir}">{content}</body>
</html>
"""
