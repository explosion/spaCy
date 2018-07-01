# coding: utf8
from __future__ import unicode_literals

from .render import DependencyRenderer, EntityRenderer
from ..tokens import Doc, Span
from ..compat import b_to_str
from ..errors import Errors, Warnings, user_warning
from ..util import prints, is_in_jupyter


_html = {}
IS_JUPYTER = is_in_jupyter()


def render(docs, style='dep', page=False, minify=False, jupyter=IS_JUPYTER,
           options={}, manual=False):
    """Render displaCy visualisation.

    docs (list or Doc): Document(s) to visualise.
    style (unicode): Visualisation style, 'dep' or 'ent'.
    page (bool): Render markup as full HTML page.
    minify (bool): Minify HTML markup.
    jupyter (bool): Experimental, use Jupyter's `display()` to output markup.
    options (dict): Visualiser-specific options, e.g. colors.
    manual (bool): Don't parse `Doc` and instead expect a dict/list of dicts.
    RETURNS (unicode): Rendered HTML markup.
    """
    factories = {'dep': (DependencyRenderer, parse_deps),
                 'ent': (EntityRenderer, parse_ents)}
    if style not in factories:
        raise ValueError(Errors.E087.format(style=style))
    if isinstance(docs, (Doc, Span, dict)):
        docs = [docs]
    docs = [obj if not isinstance(obj, Span) else obj.as_doc() for obj in docs]
    if not all(isinstance(obj, (Doc, Span, dict)) for obj in docs):
        raise ValueError(Errors.E096)
    renderer, converter = factories[style]
    renderer = renderer(options=options)
    parsed = [converter(doc, options) for doc in docs] if not manual else docs
    _html['parsed'] = renderer.render(parsed, page=page, minify=minify).strip()
    html = _html['parsed']
    if jupyter:  # return HTML rendered by IPython display()
        from IPython.core.display import display, HTML
        return display(HTML(html))
    return html


def serve(docs, style='dep', page=True, minify=False, options={}, manual=False,
          port=5000):
    """Serve displaCy visualisation.

    docs (list or Doc): Document(s) to visualise.
    style (unicode): Visualisation style, 'dep' or 'ent'.
    page (bool): Render markup as full HTML page.
    minify (bool): Minify HTML markup.
    options (dict): Visualiser-specific options, e.g. colors.
    manual (bool): Don't parse `Doc` and instead expect a dict/list of dicts.
    port (int): Port to serve visualisation.
    """
    from wsgiref import simple_server
    render(docs, style=style, page=page, minify=minify, options=options,
           manual=manual)
    httpd = simple_server.make_server('0.0.0.0', port, app)
    prints("Using the '{}' visualizer".format(style),
           title="Serving on port {}...".format(port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        prints("Shutting down server on port {}.".format(port))
    finally:
        httpd.server_close()


def app(environ, start_response):
    # headers and status need to be bytes in Python 2, see #1227
    headers = [(b_to_str(b'Content-type'),
                b_to_str(b'text/html; charset=utf-8'))]
    start_response(b_to_str(b'200 OK'), headers)
    res = _html['parsed'].encode(encoding='utf-8')
    return [res]


def parse_deps(orig_doc, options={}):
    """Generate dependency parse in {'words': [], 'arcs': []} format.

    doc (Doc): Document do parse.
    RETURNS (dict): Generated dependency parse keyed by words and arcs.
    """
    doc = Doc(orig_doc.vocab).from_bytes(orig_doc.to_bytes())
    if not doc.is_parsed:
        user_warning(Warnings.W005)
    if options.get('collapse_phrases', False):
        for np in list(doc.noun_chunks):
            np.merge(tag=np.root.tag_, lemma=np.root.lemma_,
                    ent_type=np.root.ent_type_)
    if options.get('collapse_punct', True):
        spans = []
        for word in doc[:-1]:
            if word.is_punct or not word.nbor(1).is_punct:
                continue
            start = word.i
            end = word.i + 1
            while end < len(doc) and doc[end].is_punct:
                end += 1
            span = doc[start:end]
            spans.append((span.start_char, span.end_char, word.tag_,
                          word.lemma_, word.ent_type_))
        for start, end, tag, lemma, ent_type in spans:
            doc.merge(start, end, tag=tag, lemma=lemma, ent_type=ent_type)
    if options.get('fine_grained'):
        words = [{'text': w.text, 'tag': w.tag_} for w in doc]
    else:
        words = [{'text': w.text, 'tag': w.pos_} for w in doc]
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
    if not ents:
        user_warning(Warnings.W006)
    title = (doc.user_data.get('title', None)
             if hasattr(doc, 'user_data') else None)
    return {'text': doc.text, 'ents': ents, 'title': title}
