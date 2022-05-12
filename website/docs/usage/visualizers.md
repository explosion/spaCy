---
title: Visualizers
teaser: Visualize dependencies and entities in your browser or in a notebook
new: 2
menu:
  - ['Dependencies', 'dep']
  - ['Named Entities', 'ent']
  - ['Spans', 'span']
  - ['Jupyter Notebooks', 'jupyter']
  - ['Rendering HTML', 'html']
  - ['Web app usage', 'webapp']
---

Visualizing a dependency parse or named entities in a text is not only a fun NLP
demo – it can also be incredibly helpful in speeding up development and
debugging your code and training process. That's why our popular visualizers,
[displaCy](https://explosion.ai/demos/displacy) and
[displaCy <sup>ENT</sup>](https://explosion.ai/demos/displacy-ent) are also an
official part of the core library. If you're running a
[Jupyter](https://jupyter.org) notebook, displaCy will detect this and return
the markup in a format [ready to be rendered and exported](#jupyter).

The quickest way to visualize `Doc` is to use
[`displacy.serve`](/api/top-level#displacy.serve). This will spin up a simple
web server and let you view the result straight from your browser. displaCy can
either take a single `Doc` or a list of `Doc` objects as its first argument.
This lets you construct them however you like – using any pipeline or
modifications you like. If you're using [Streamlit](https://streamlit.io), check
out the [`spacy-streamlit`](https://github.com/explosion/spacy-streamlit)
package that helps you integrate spaCy visualizations into your apps!

## Visualizing the dependency parse {#dep}

The dependency visualizer, `dep`, shows part-of-speech tags and syntactic
dependencies.

```python
### Dependency example
import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("This is a sentence.")
displacy.serve(doc, style="dep")
```

![displaCy visualizer](../images/displacy.svg)

The argument `options` lets you specify a dictionary of settings to customize
the layout, for example:

<Infobox title="Important note" variant="warning">

There's currently a known issue with the `compact` mode for sentences with short
arrows and long dependency labels, that causes labels longer than the arrow to
wrap. So if you come across this problem, especially when using custom labels,
you'll have to increase the `distance` setting in the `options` to allow longer
arcs.

</Infobox>

| Argument  | Description                                                                               |
| --------- | ----------------------------------------------------------------------------------------- |
| `compact` | "Compact mode" with square arrows that takes up less space. Defaults to `False`. ~~bool~~ |
| `color`   | Text color (HEX, RGB or color names). Defaults to `"#000000"`. ~~str~~                    |
| `bg`      | Background color (HEX, RGB or color names). Defaults to `"#ffffff"`. ~~str~~              |
| `font`    | Font name or font family for all text. Defaults to `"Arial"`. ~~str~~                     |

For a list of all available options, see the
[`displacy` API documentation](/api/top-level#displacy_options).

> #### Options example
>
> ```python
> options = {"compact": True, "bg": "#09a3d5",
>            "color": "white", "font": "Source Sans Pro"}
> displacy.serve(doc, style="dep", options=options)
> ```

![displaCy visualizer (compact mode)](../images/displacy-compact.svg)

### Visualizing long texts {#dep-long-text new="2.0.12"}

Long texts can become difficult to read when displayed in one row, so it's often
better to visualize them sentence-by-sentence instead. As of v2.0.12, `displacy`
supports rendering both [`Doc`](/api/doc) and [`Span`](/api/span) objects, as
well as lists of `Doc`s or `Span`s. Instead of passing the full `Doc` to
`displacy.serve`, you can also pass in a list `doc.sents`. This will create one
visualization for each sentence.

```python
import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")
text = """In ancient Rome, some neighbors live in three adjacent houses. In the center is the house of Senex, who lives there with wife Domina, son Hero, and several slaves, including head slave Hysterium and the musical's main character Pseudolus. A slave belonging to Hero, Pseudolus wishes to buy, win, or steal his freedom. One of the neighboring houses is owned by Marcus Lycus, who is a buyer and seller of beautiful women; the other belongs to the ancient Erronius, who is abroad searching for his long-lost children (stolen in infancy by pirates). One day, Senex and Domina go on a trip and leave Pseudolus in charge of Hero. Hero confides in Pseudolus that he is in love with the lovely Philia, one of the courtesans in the House of Lycus (albeit still a virgin)."""
doc = nlp(text)
sentence_spans = list(doc.sents)
displacy.serve(sentence_spans, style="dep")
```

## Visualizing the entity recognizer {#ent}

The entity visualizer, `ent`, highlights named entities and their labels in a
text.

```python
### Named Entity example
import spacy
from spacy import displacy

text = "When Sebastian Thrun started working on self-driving cars at Google in 2007, few people outside of the company took him seriously."

nlp = spacy.load("en_core_web_sm")
doc = nlp(text)
displacy.serve(doc, style="ent")
```

import DisplacyEntHtml from 'images/displacy-ent2.html'

<Iframe title="displaCy visualizer for entities" html={DisplacyEntHtml} height={180} />

The entity visualizer lets you customize the following `options`:

| Argument | Description                                                                                                   |
| -------- | ------------------------------------------------------------------------------------------------------------- |
| `ents`   | Entity types to highlight (`None` for all types). Defaults to `None`. ~~Optional[List[str]]~~                 | `None` |
| `colors` | Color overrides. Entity types should be mapped to color names or values. Defaults to `{}`. ~~Dict[str, str]~~ |

If you specify a list of `ents`, only those entity types will be rendered – for
example, you can choose to display `PERSON` entities. Internally, the visualizer
knows nothing about available entity types and will render whichever spans and
labels it receives. This makes it especially easy to work with custom entity
types. By default, displaCy comes with colors for all entity types used by
[trained spaCy pipelines](/models). If you're using custom entity types, you can
use the `colors` setting to add your own colors for them.

> #### Options example
>
> ```python
> colors = {"ORG": "linear-gradient(90deg, #aa9cfc, #fc9ce7)"}
> options = {"ents": ["ORG"], "colors": colors}
> displacy.serve(doc, style="ent", options=options)
> ```

import DisplacyEntCustomHtml from 'images/displacy-ent-custom.html'

<Iframe title="displaCy visualizer for entities (custom styling)" html={DisplacyEntCustomHtml} height={225} />

The above example uses a little trick: Since the background color values are
added as the `background` style attribute, you can use any
[valid background value](https://tympanus.net/codrops/css_reference/background/)
or shorthand – including gradients and even images!

### Adding titles to documents {#ent-titles}

Rendering several large documents on one page can easily become confusing. To
add a headline to each visualization, you can add a `title` to its `user_data`.
User data is never touched or modified by spaCy.

```python
doc = nlp("This is a sentence about Google.")
doc.user_data["title"] = "This is a title"
displacy.serve(doc, style="ent")
```

This feature is especially handy if you're using displaCy to compare performance
at different stages of a process, e.g. during training. Here you could use the
title for a brief description of the text example and the number of iterations.

## Visualizing spans {#span}

The span visualizer, `span`, highlights overlapping spans in a text.

```python
### Span example
import spacy
from spacy import displacy
from spacy.tokens import Span

text = "Welcome to the Bank of China."

nlp = spacy.blank("en")
doc = nlp(text)

doc.spans["sc"] = [
    Span(doc, 3, 6, "ORG"), 
    Span(doc, 5, 6, "GPE"),
]

displacy.serve(doc, style="span")
```

import DisplacySpanHtml from 'images/displacy-span.html'

<Iframe title="displaCy visualizer for overlapping spans" html={DisplacySpanHtml} height={180} />


The span visualizer lets you customize the following `options`:

| Argument | Description                                                                                                                                             |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|
| `spans_key`       | Which spans key to render spans from. Default is `"sc"`. ~~str~~                                                                                                   |
| `templates`       | Dictionary containing the keys `"span"`, `"slice"`, and `"start"`. These dictate how the overall span, a span slice, and the starting token will be rendered. ~~Optional[Dict[str, str]~~ |
| `kb_url_template` | Optional template to construct the KB url for the entity to link to. Expects a python f-string format with single field to fill in ~~Optional[str]~~                    |
| `colors`          | Color overrides. Entity types should be mapped to color names or values. ~~Dict[str, str]~~ |

Because spans can be stored across different keys in `doc.spans`, you need to specify
which one displaCy should use with `spans_key` (`sc` is the default). 

> #### Options example
>
> ```python
> doc.spans["custom"] = [Span(doc, 3, 6, "BANK")]
> options = {"spans_key": "custom"}
> displacy.serve(doc, style="span", options=options)

import DisplacySpanCustomHtml from 'images/displacy-span-custom.html'

<Iframe title="displaCy visualizer for spans (custom spans_key)" html={DisplacySpanCustomHtml} height={225} />



## Using displaCy in Jupyter notebooks {#jupyter}

displaCy is able to detect whether you're working in a
[Jupyter](https://jupyter.org) notebook, and will return markup that can be
rendered in a cell straight away. When you export your notebook, the
visualizations will be included as HTML.

```python
### Jupyter example
# Don't forget to install a trained pipeline, e.g.: python -m spacy download en

# In[1]:
import spacy
from spacy import displacy

# In[2]:
doc = nlp("Rats are various medium-sized, long-tailed rodents.")
displacy.render(doc, style="dep")

# In[3]:
doc2 = nlp(LONG_NEWS_ARTICLE)
displacy.render(doc2, style="ent")
```

<Infobox variant="warning" title="Important note">

To explicitly enable or disable "Jupyter mode", you can use the `jupyter`
keyword argument – e.g. to return raw HTML in a notebook, or to force Jupyter
rendering if auto-detection fails.

</Infobox>

![displaCy visualizer in a Jupyter notebook](../images/displacy_jupyter.jpg)

Internally, displaCy imports `display` and `HTML` from `IPython.core.display`
and returns a Jupyter HTML object. If you were doing it manually, it'd look like
this:

```python
from IPython.core.display import display, HTML

html = displacy.render(doc, style="dep")
display(HTML(html))
```

## Rendering HTML {#html}

If you don't need the web server and just want to generate the markup – for
example, to export it to a file or serve it in a custom way – you can use
[`displacy.render`](/api/top-level#displacy.render). It works the same way, but
returns a string containing the markup.

```python
### Example
import spacy
from spacy import displacy

nlp = spacy.load("en_core_web_sm")
doc1 = nlp("This is a sentence.")
doc2 = nlp("This is another sentence.")
html = displacy.render([doc1, doc2], style="dep", page=True)
```

`page=True` renders the markup wrapped as a full HTML page. For minified and
more compact HTML markup, you can set `minify=True`. If you're rendering a
dependency parse, you can also export it as an `.svg` file.

> #### What's SVG?
>
> Unlike other image formats, the SVG (Scalable Vector Graphics) uses XML markup
> that's easy to manipulate
> [using CSS](https://www.smashingmagazine.com/2014/11/styling-and-animating-svgs-with-css/)
> or
> [JavaScript](https://css-tricks.com/smil-is-dead-long-live-smil-a-guide-to-alternatives-to-smil-features/).
> Essentially, SVG lets you design with code, which makes it a perfect fit for
> visualizing dependency trees. SVGs can be embedded online in an `<img>` tag,
> or inlined in an HTML document. They're also pretty easy to
> [convert](https://convertio.co/image-converter/).

```python
svg = displacy.render(doc, style="dep")
output_path = Path("/images/sentence.svg")
output_path.open("w", encoding="utf-8").write(svg)
```

<Infobox title="Important note" variant="warning">

Since each visualization is generated as a separate SVG, exporting `.svg` files
only works if you're rendering **one single doc** at a time. (This makes sense –
after all, each visualization should be a standalone graphic.) So instead of
rendering all `Doc`s at once, loop over them and export them separately.

</Infobox>

### Example: Export SVG graphics of dependency parses {#examples-export-svg}

```python
### Example
import spacy
from spacy import displacy
from pathlib import Path

nlp = spacy.load("en_core_web_sm")
sentences = ["This is an example.", "This is another one."]
for sent in sentences:
    doc = nlp(sent)
    svg = displacy.render(doc, style="dep", jupyter=False)
    file_name = '-'.join([w.text for w in doc if not w.is_punct]) + ".svg"
    output_path = Path("/images/" + file_name)
    output_path.open("w", encoding="utf-8").write(svg)
```

The above code will generate the dependency visualizations as two files,
`This-is-an-example.svg` and `This-is-another-one.svg`.

### Rendering data manually {#manual-usage}

You can also use displaCy to manually render data. This can be useful if you
want to visualize output from other libraries, like [NLTK](http://www.nltk.org)
or
[SyntaxNet](https://github.com/tensorflow/models/tree/master/research/syntaxnet).
If you set `manual=True` on either `render()` or `serve()`, you can pass in data
in displaCy's format as a dictionary (instead of `Doc` objects).

> #### Example
>
> ```python
> ex = [{"text": "But Google is starting from behind.",
>        "ents": [{"start": 4, "end": 10, "label": "ORG"}],
>        "title": None}]
> html = displacy.render(ex, style="ent", manual=True)
> ```

```python
### DEP input
{
    "words": [
        {"text": "This", "tag": "DT"},
        {"text": "is", "tag": "VBZ"},
        {"text": "a", "tag": "DT"},
        {"text": "sentence", "tag": "NN"}
    ],
    "arcs": [
        {"start": 0, "end": 1, "label": "nsubj", "dir": "left"},
        {"start": 2, "end": 3, "label": "det", "dir": "left"},
        {"start": 1, "end": 3, "label": "attr", "dir": "right"}
    ]
}
```

```python
### ENT input
{
    "text": "But Google is starting from behind.",
    "ents": [{"start": 4, "end": 10, "label": "ORG"}],
    "title": None
}
```

```python
### ENT input with knowledge base links
{
    "text": "But Google is starting from behind.",
    "ents": [{"start": 4, "end": 10, "label": "ORG", "kb_id": "Q95", "kb_url": "https://www.wikidata.org/entity/Q95"}],
    "title": None
}
```

## Using displaCy in a web application {#webapp}

If you want to use the visualizers as part of a web application, for example to
create something like our [online demo](https://explosion.ai/demos/displacy),
it's not recommended to only wrap and serve the displaCy renderer. Instead, you
should only rely on the server to perform spaCy's processing capabilities, and
use a client-side implementation like
[`displaCy.js`](https://github.com/explosion/displacy) to render the
JSON-formatted output.

> #### Why not return the HTML by the server?
>
> It's certainly possible to just have your server return the markup. But
> outputting raw, unsanitized HTML is risky and makes your app vulnerable to
> [cross-site scripting](https://en.wikipedia.org/wiki/Cross-site_scripting)
> (XSS). All your user needs to do is find a way to make spaCy return text like
> `<script src="malicious-code.js"></script>`, which is pretty easy in NER mode.
> Instead of relying on the server to render and sanitize HTML, you can do this
> on the client in JavaScript. displaCy.js creates the markup as DOM nodes and
> will never insert raw HTML.

<Grid cols={2}>

Alternatively, if you're using [Streamlit](https://streamlit.io), check out the
[`spacy-streamlit`](https://github.com/explosion/spacy-streamlit) package that
helps you integrate spaCy visualizations into your apps. It includes a full
embedded visualizer, as well as individual components.

![](../images/spacy-streamlit.png)

</Grid>
