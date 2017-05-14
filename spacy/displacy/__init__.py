# coding: utf8
from __future__ import unicode_literals

from .render import DependencyRenderer, EntityRenderer
from ..tokens import Doc
from ..util import prints


_html = {}


def render(docs, style='dep', page=False, minify=False, jupyter=False, options={}):
    """Render displaCy visualisation.

    docs (list or Doc): Document(s) to visualise.
    style (unicode): Visualisation style, 'dep' or 'ent'.
    page (bool): Render markup as full HTML page.
    minify (bool): Minify HTML markup.
    jupyter (bool): Experimental, use Jupyter's display() to output markup.
    options (dict): Visualiser-specific options, e.g. colors.
    RETURNS (unicode): Rendered HTML markup.
    """
    if isinstance(docs, Doc):
        docs = [docs]
    if style is 'dep':
        renderer = DependencyRenderer(options=options)
        parsed = [parse_deps(doc, options) for doc in docs]
    elif style is 'ent':
        renderer = EntityRenderer(options=options)
        parsed = [parse_ents(doc, options) for doc in docs]
    _html['parsed'] = renderer.render(parsed, page=page, minify=minify).strip()
    html = _html['parsed']
    if jupyter: # return HTML rendered by IPython display()
        from IPython.core.display import display, HTML
        return display(HTML(html))
    return html


def serve(docs, style='dep', page=True, minify=False, options={}, port=5000):
    """Serve displaCy visualisation.

    docs (list or Doc): Document(s) to visualise.
    style (unicode): Visualisation style, 'dep' or 'ent'.
    page (bool): Render markup as full HTML page.
    minify (bool): Minify HTML markup.
    options (dict): Visualiser-specific options, e.g. colors.
    port (int): Port to serve visualisation.
    """
    from wsgiref import simple_server
    render(docs, style=style, page=page, minify=minify, options=options)
    httpd = simple_server.make_server('0.0.0.0', port, app)
    prints("Using the '%s' visualizer" % style, title="Serving on port %d..." % port)
    httpd.serve_forever()


def app(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
    res = _html['parsed'].encode(encoding='utf-8')
    return [res]


def parse_deps(doc, options={}):
    """Generate dependency parse in {'words': [], 'arcs': []} format.

    doc (Doc): Document do parse.
    RETURNS (dict): Generated dependency parse keyed by words and arcs.
    """
    if options.get('collapse_punct', True):
        spans = []
        for word in doc[:-1]:
            if word.is_punct or not word.nbor(1).is_punct:
                continue
            start = word.i
            end = word.i + 1
            while end < len(doc) and doc[end].is_punct:
                end += 1
            span = doc[start : end]
            spans.append((span.start_char, span.end_char, word.tag_,
                            word.lemma_, word.ent_type_))
        for span_props in spans:
            doc.merge(*span_props)
    words = [{'text': w.text, 'tag': w.tag_} for w in doc]
    arcs = []
    for word in doc:
        if word.i < word.head.i:
            arcs.append({'start': word.i, 'end': word.head.i,
                         'label': word.dep_, 'dir': 'left'})
        elif word.i > word.head.i:
            arcs.append({'start': word.head.i, 'end': word.i,
                         'label': word.dep_, 'dir': 'right'})
    return {'words': words, 'arcs': arcs}


def parse_ents(doc, options={}):
    """Generate named entities in [{start: i, end: i, label: 'label'}] format.

    doc (Doc): Document do parse.
    RETURNS (dict): Generated entities keyed by text (original text) and ents.
    """
    ents = [{'start': ent.start_char, 'end': ent.end_char, 'label': ent.label_}
             for ent in doc.ents]
    title = doc.user_data.get('title', None)
    return {'text': doc.text, 'ents': ents, 'title': title}
