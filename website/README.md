<Comment>

# spacy.io website and docs

![Netlify Status](https://api.netlify.com/api/v1/badges/d65fe97d-99ab-47f8-a339-1d8987251da0/deploy-status)

_This page contains the documentation and styleguide for the spaCy website. Its
rendered version is available at https://spacy.io/styleguide._

---

</Comment>

The [spacy.io](https://spacy.io) website is implemented using
[Gatsby](https://www.gatsbyjs.org) with
[Remark](https://github.com/remarkjs/remark) and [MDX](https://mdxjs.com/). This
allows authoring content in **straightforward Markdown** without the usual
limitations. Standard elements can be overwritten with powerful
[React](http://reactjs.org/) components and wherever Markdown syntax isn't
enough, JSX components can be used.

> #### Contributing to the site
>
> The docs can always use another example or more detail, and they should always
> be up to date and not misleading. We always appreciate a
> [pull request](https://github.com/explosion/spaCy/pulls). To quickly find the
> correct file to edit, simply click on the "Suggest edits" button at the bottom
> of a page.
>
> For more details on editing the site locally, see the installation
> instructions and markdown reference below.

## Logo {#logo source="website/src/images/logo.svg"}

import { Logos } from 'widgets/styleguide'

If you would like to use the spaCy logo on your site, please get in touch and
ask us first. However, if you want to show support and tell others that your
project is using spaCy, you can grab one of our
[spaCy badges](/usage/spacy-101#faq-project-with-spacy).

<Logos />

## Colors {#colors}

import { Colors, Patterns } from 'widgets/styleguide'

<Colors />

### Patterns

<Patterns />

## Typography {#typography}

import { H1, H2, H3, H4, H5, Label, InlineList, Comment } from
'components/typography'

> #### Markdown
>
> ```markdown_
> ## Headline 2
> ## Headline 2 {#some_id}
> ## Headline 2 {#some_id tag="method"}
> ```
>
> #### JSX
>
> ```jsx
> <H2>Headline 2</H2>
> <H2 id="some_id">Headline 2</H2>
> <H2 id="some_id" tag="method">Headline 2</H2>
> ```

Headlines are set in
[HK Grotesk](http://cargocollective.com/hanken/HK-Grotesk-Open-Source-Font) by
Hanken Design. All other body text and code uses the best-matching default
system font to provide a "native" reading experience. All code uses the
[JetBrains Mono](https://www.jetbrains.com/lp/mono/) typeface by JetBrains.

<Infobox title="Important note" variant="warning">

Level 2 headings are automatically wrapped in `<section>` elements at compile
time, using a custom
[Markdown transformer](https://github.com/explosion/spaCy/tree/master/website/plugins/remark-wrap-section.js).
This makes it easier to highlight the section that's currently in the viewpoint
in the sidebar menu.

</Infobox>

<div>
<H1>Headline 1</H1>
<H2>Headline 2</H2>
<H3>Headline 3</H3>
<H4>Headline 4</H4>
<H5>Headline 5</H5>
<Label>Label</Label>
</div>

---

The following optional attributes can be set on the headline to modify it. For
example, to add a tag for the documented type or mark features that have been
introduced in a specific version or require statistical models to be loaded.
Tags are also available as standalone `<Tag />` components.

| Argument | Example                    | Result                                    |
| -------- | -------------------------- | ----------------------------------------- |
| `tag`    | `{tag="method"}`           | <Tag>method</Tag>                         |
| `new`    | `{new="3"}`                | <Tag variant="new">3</Tag>                |
| `model`  | `{model="tagger, parser"}` | <Tag variant="model">tagger, parser</Tag> |
| `hidden` | `{hidden="true"}`          |                                           |

## Elements {#elements}

### Links {#links}

> #### Markdown
>
> ```markdown
> [I am a link](https://spacy.io)
> ```
>
> #### JSX
>
> ```jsx
> <Link to="https://spacy.io">I am a link</Link>
> ```

Special link styles are used depending on the link URL.

- [I am a regular external link](https://explosion.ai)
- [I am a link to the documentation](/api/doc)
- [I am a link to an architecture](/api/architectures#HashEmbedCNN)
- [I am a link to a model](/models/en#en_core_web_sm)
- [I am a link to GitHub](https://github.com/explosion/spaCy)

### Abbreviations {#abbr}

import { Abbr } from 'components/typography'

> #### JSX
>
> ```jsx
> <Abbr title="Explanation">Abbreviation</Abbr>
> ```

Some text with <Abbr title="Explanation here">an abbreviation</Abbr>. On small
screens, I collapse and the explanation text is displayed next to the
abbreviation.

### Tags {#tags}

import Tag from 'components/tag'

> ```jsx
> <Tag>method</Tag>
> <Tag variant="new">2.1</Tag>
> <Tag variant="model">tagger, parser</Tag>
> ```

Tags can be used together with headlines, or next to properties across the
documentation, and combined with tooltips to provide additional information. An
optional `variant` argument can be used for special tags. `variant="new"` makes
the tag take a version number to mark new features. Using the component,
visibility of this tag can later be toggled once the feature isn't considered
new anymore. Setting `variant="model"` takes a description of model capabilities
and can be used to mark features that require a respective model to be
installed.

<InlineList>

<Tag>method</Tag> <Tag variant="new">2</Tag> <Tag variant="model">tagger,
parser</Tag>

</InlineList>

### Buttons {#buttons}

import Button from 'components/button'

> ```jsx
> <Button to="#" variant="primary">Primary small</Button>
> <Button to="#" variant="secondary">Secondary small</Button>
> ```

Link buttons come in two variants, `primary` and `secondary` and two sizes, with
an optional `large` size modifier. Since they're mostly used as enhanced links,
the buttons are implemented as styled links instead of native button elements.

<InlineList><Button to="#" variant="primary">Primary small</Button>
<Button to="#" variant="secondary">Secondary small</Button></InlineList>

<br />

<InlineList><Button to="#" variant="primary" large>Primary large</Button>
<Button to="#" variant="secondary" large>Secondary large</Button></InlineList>

## Components

### Table {#table}

> #### Markdown
>
> ```markdown_
> | Header 1 | Header 2 |
> | -------- | -------- |
> | Column 1 | Column 2 |
> ```
>
> #### JSX
>
> ```markup
> <Table>
>     <Tr><Th>Header 1</Th><Th>Header 2</Th></Tr></thead>
>     <Tr><Td>Column 1</Td><Td>Column 2</Td></Tr>
> </Table>
> ```

Tables are used to present data and API documentation. Certain keywords can be
used to mark a footer row with a distinct style, for example to visualize the
return values of a documented function.

| Header 1    | Header 2 | Header 3 | Header 4 |
| ----------- | -------- | :------: | -------: |
| Column 1    | Column 2 | Column 3 | Column 4 |
| Column 1    | Column 2 | Column 3 | Column 4 |
| Column 1    | Column 2 | Column 3 | Column 4 |
| Column 1    | Column 2 | Column 3 | Column 4 |
| **RETURNS** | Column 2 | Column 3 | Column 4 |

Tables also support optional "divider" rows that are typically used to denote
keyword-only arguments in API documentation. To turn a row into a dividing
headline, it should only include content in its first cell, and its value should
be italicized:

> #### Markdown
>
> ```markdown_
> | Header 1 | Header 2 | Header 3 |
> | -------- | -------- | -------- |
> | Column 1 | Column 2 | Column 3 |
> | _Hello_  |          |          |
> | Column 1 | Column 2 | Column 3 |
> ```

| Header 1 | Header 2 | Header 3 |
| -------- | -------- | -------- |
| Column 1 | Column 2 | Column 3 |
| _Hello_  |          |          |
| Column 1 | Column 2 | Column 3 |

### Type Annotations {#type-annotations}

> #### Markdown
>
> ```markdown_
> ~~Model[List[Doc], Floats2d]~~
> ```
>
> #### JSX
>
> ```markup
> <TypeAnnotation>Model[List[Doc], Floats2d]</Typeannotation>
> ```

Type annotations are special inline code blocks are used to describe Python
types in the [type hints](https://docs.python.org/3/library/typing.html) format.
The special component will split the type, apply syntax highlighting and link
all types that specify links in `meta/type-annotations.json`. Types can link to
internal or external documentation pages. To make it easy to represent the type
annotations in Markdown, the rendering "hijacks" the `~~` tags that would
typically be converted to a `<del>` element – but in this case, text surrounded
by `~~` becomes a type annotation.

- ~~Dict[str, List[Union[Doc, Span]]]~~
- ~~Model[List[Doc], List[numpy.ndarray]]~~

Type annotations support a special visual style in tables and will render as a
separate row, under the cell text. This allows the API docs to display complex
types without taking up too much space in the cell. The type annotation should
always be the **last element** in the row.

> #### Markdown
>
> ```markdown_
> | Header 1 | Header 2                |
> | -------- | ----------------------- |
> | Column 1 | Column 2 ~~List[Doc]~~ |
> ```

| Name                    | Description                                                                                                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `vocab`                 | The shared vocabulary. ~~Vocab~~                                                                                                                                            |
| `model`                 | The Thinc [`Model`](https://thinc.ai/docs/api-model) wrapping the transformer. ~~Model[List[Doc], FullTransformerBatch]~~                                                   |
| `set_extra_annotations` | Function that takes a batch of `Doc` objects and transformer outputs and can set additional annotations on the `Doc`. ~~Callable[[List[Doc], FullTransformerBatch], None]~~ |

### List {#list}

> #### Markdown
>
> ```markdown_
> 1. One
> 2. Two
> ```
>
> #### JSX
>
> ```markup
> <Ol>
>     <Li>One</Li>
>     <Li>Two</Li>
> </Ol>
> ```

Lists are available as bulleted and numbered. Markdown lists are transformed
automatically.

- I am a bulleted list
- I have nice bullets
- Lorem ipsum dolor
- consectetur adipiscing elit

1. I am an ordered list
2. I have nice numbers
3. Lorem ipsum dolor
4. consectetur adipiscing elit

### Aside {#aside}

> #### Markdown
>
> ```markdown_
> > #### Aside title
> > This is aside text.
> ```
>
> #### JSX
>
> ```jsx
> <Aside title="Aside title">This is aside text.</Aside>
> ```

Asides can be used to display additional notes and content in the right-hand
column. Asides can contain text, code and other elements if needed. Visually,
asides are moved to the side on the X-axis, and displayed at the same level they
were inserted. On small screens, they collapse and are rendered in their
original position, in between the text.

To make them easier to use in Markdown, paragraphs formatted as blockquotes will
turn into asides by default. Level 4 headlines (with a leading `####`) will
become aside titles.

### Code Block {#code-block}

> #### Markdown
>
> ````markdown_
> ```python
> ### This is a title
> import spacy
> ```
> ````
>
> #### JSX
>
> ```jsx
> <CodeBlock title="This is a title" lang="python">
>   import spacy
> </CodeBlock>
> ```

Code blocks use the [Prism](http://prismjs.com/) syntax highlighter with a
custom theme. The language can be set individually on each block, and defaults
to raw text with no highlighting. An optional label can be added as the first
line with the prefix `####` (Python-like) and `///` (JavaScript-like). the
indented block as plain text and preserve whitespace.

```python
### Using spaCy
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("This is a sentence.")
for token in doc:
    print(token.text, token.pos_)
```

Code blocks and also specify an optional range of line numbers to highlight by
adding `{highlight="..."}` to the headline. Acceptable ranges are spans like
`5-7`, but also `5-7,10` or `5-7,10,13-14`.

> #### Markdown
>
> ````markdown_
> ```python
> ### This is a title {highlight="1-2"}
> import spacy
> nlp = spacy.load("en_core_web_sm")
> ```
> ````

```python
### Using the matcher {highlight="5-7"}
import spacy
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
pattern = [{"LOWER": "hello"}, {"IS_PUNCT": True}, {"LOWER": "world"}]
matcher.add("HelloWorld", None, pattern)
doc = nlp("Hello, world! Hello world!")
matches = matcher(doc)
```

Adding `{executable="true"}` to the title turns the code into an executable
block, powered by [Binder](https://mybinder.org) and
[Juniper](https://github.com/ines/juniper). If JavaScript is disabled, the
interactive widget defaults to a regular code block.

> #### Markdown
>
> ````markdown_
> ```python
> ### {executable="true"}
> import spacy
> nlp = spacy.load("en_core_web_sm")
> ```
> ````

```python
### {executable="true"}
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("This is a sentence.")
for token in doc:
    print(token.text, token.pos_)
```

If a code block only contains a URL to a GitHub file, the raw file contents are
embedded automatically and syntax highlighting is applied. The link to the
original file is shown at the top of the widget.

> #### Markdown
>
> ````markdown_
> ```python
> https://github.com/...
> ```
> ````
>
> #### JSX
>
> ```jsx
> <GitHubCode url="https://github.com/..." lang="python" />
> ```

```python
https://github.com/explosion/spaCy/tree/master/spacy/language.py
```

### Infobox {#infobox}

import Infobox from 'components/infobox'

> #### JSX
>
> ```jsx
> <Infobox title="Information">Regular infobox</Infobox>
> <Infobox title="Important note" variant="warning">This is a warning.</Infobox>
> <Infobox title="Be careful!" variant="danger">This is dangerous.</Infobox>
> ```

Infoboxes can be used to add notes, updates, warnings or additional information
to a page or section. Semantically, they're implemented and interpreted as an
`aside` element. Infoboxes can take an optional `title` argument, as well as an
optional `variant` (either `"warning"` or `"danger"`).

<Infobox title="This is an infobox">

If needed, an infobox can contain regular text, `inline code`, lists and other
blocks.

</Infobox>

<Infobox title="This is a warning" variant="warning">

If needed, an infobox can contain regular text, `inline code`, lists and other
blocks.

</Infobox>

<Infobox title="This is dangerous" variant="danger">

If needed, an infobox can contain regular text, `inline code`, lists and other
blocks.

</Infobox>

### Accordion {#accordion}

import Accordion from 'components/accordion'

> #### JSX
>
> ```jsx
> <Accordion title="This is an accordion">
>   Accordion content goes here.
> </Accordion>
> ```

Accordions are collapsible sections that are mostly used for lengthy tables,
like the tag and label annotation schemes for different languages. They all need
to be presented – but chances are the user doesn't actually care about _all_ of
them, especially not at the same time. So it's fairly reasonable to hide them
begin a click. This particular implementation was inspired by the amazing
[Inclusive Components blog](https://inclusive-components.design/collapsible-sections/).

<Accordion title="This is an accordion">

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque enim ante,
pretium a orci eget, varius dignissim augue. Nam eu dictum mauris, id tincidunt
nisi. Integer commodo pellentesque tincidunt. Nam at turpis finibus tortor
gravida sodales tincidunt sit amet est. Nullam euismod arcu in tortor auctor,
sit amet dignissim justo congue.

</Accordion>

## Setup and installation {#setup}

Before running the setup, make sure your versions of
[Node](https://nodejs.org/en/) and [npm](https://www.npmjs.com/) are up to date.
Node v10.15 or later is required.

```bash
# Clone the repository
git clone https://github.com/explosion/spaCy
cd spaCy/website

# Install Gatsby's command-line tool
npm install --global gatsby-cli

# Install the dependencies
npm install

# Start the development server
npm run dev
```

If you are planning on making edits to the site, you should also set up the
[Prettier](https://prettier.io/) code formatter. It takes care of formatting
Markdown and other files automatically.
[See here](https://prettier.io/docs/en/editors.html) for the available
extensions for your code editor. The
[`.prettierrc`](https://github.com/explosion/spaCy/tree/master/website/.prettierrc)
file in the root defines the settings used in this codebase.

## Building & developing the site with Docker {#docker}
Sometimes it's hard to get a local environment working due to rapid updates to node dependencies,
so it may be easier to use docker for building the docs.

If you'd like to do this,
**be sure you do *not* include your local `node_modules` folder**,
since there are some dependencies that need to be built for the image system. 
Rename it before using.

```bash
docker run -it \
  -v $(pwd):/spacy-io/website \
  -p 8000:8000 \
  ghcr.io/explosion/spacy-io \
  gatsby develop -H 0.0.0.0
```

This will allow you to access the built website at http://0.0.0.0:8000/ 
in your browser, and still edit code in your editor while having the site 
reflect those changes.

**Note**: If you're working on a Mac with an M1 processor, 
you might see segfault errors from `qemu` if you use the default image. 
To fix this use the `arm64` tagged image in the `docker run` command 
(ghcr.io/explosion/spacy-io:arm64).

### Building the Docker image {#docker-build}

If you'd like to build the image locally, you can do so like this:

```bash
docker build -t spacy-io .
```

This will take some time, so if you want to use the prebuilt image you'll save a bit of time.

## Markdown reference {#markdown}

All page content and page meta lives in the `.md` files in the `/docs`
directory. The frontmatter block at the top of each file defines the page title
and other settings like the sidebar menu.

````markdown
---
title: Page title
---

## Headline starting a section {#some_id}

This is a regular paragraph with a [link](https://spacy.io) and **bold text**.

> #### This is an aside title
>
> This is aside text.

### Subheadline

| Header 1 | Header 2 |
| -------- | -------- |
| Column 1 | Column 2 |

```python
### Code block title {highlight="2-3"}
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("Hello world")
```

<Infobox title="Important note" variant="warning">

This is content in the infobox.

</Infobox>
````

In addition to the native markdown elements, you can use the components
[`<Infobox />`][infobox], [`<Accordion />`][accordion], [`<Abbr />`][abbr] and
[`<Tag />`][tag] via their JSX syntax.

[infobox]: https://spacy.io/styleguide#infobox
[accordion]: https://spacy.io/styleguide#accordion
[abbr]: https://spacy.io/styleguide#abbr
[tag]: https://spacy.io/styleguide#tag

## Project structure {#structure}

```yaml
### Directory structure
├── docs                 # the actual markdown content
├── meta                 # JSON-formatted site metadata
|   ├── languages.json   # supported languages and statistical models
|   ├── sidebars.json    # sidebar navigations for different sections
|   ├── site.json        # general site metadata
|   └── universe.json    # data for the spaCy universe section
├── public               # compiled site
├── src                  # source
|   ├── components       # React components
|   ├── fonts            # webfonts
|   ├── images           # images used in the layout
|   ├── plugins          # custom plugins to transform Markdown
|   ├── styles           # CSS modules and global styles
|   ├── templates        # page layouts
|   |   ├── docs.js      # layout template for documentation pages
|   |   ├── index.js     # global layout template
|   |   ├── models.js    # layout template for model pages
|   |   └── universe.js  # layout templates for universe
|   └── widgets          # non-reusable components with content, e.g. changelog
├── gatsby-browser.js    # browser-specific hooks for Gatsby
├── gatsby-config.js     # Gatsby configuration
├── gatsby-node.js       # Node-specific hooks for Gatsby
└── package.json         # package settings and dependencies
```

## Editorial {#editorial}

- "spaCy" should always be spelled with a lowercase "s" and a capital "C",
  unless it specifically refers to the Python package or Python import `spacy`
  (in which case it should be formatted as code).
  - ✅ spaCy is a library for advanced NLP in Python.
  - ❌ Spacy is a library for advanced NLP in Python.
  - ✅ First, you need to install the `spacy` package from pip.
- Mentions of code, like function names, classes, variable names etc. in inline
  text should be formatted as `code`.
  - ✅ "Calling the `nlp` object on a text returns a `Doc`."
- Objects that have pages in the [API docs](/api) should be linked – for
  example, [`Doc`](/api/doc) or [`Language.to_disk`](/api/language#to_disk). The
  mentions should still be formatted as code within the link. Links pointing to
  the API docs will automatically receive a little icon. However, if a paragraph
  includes many references to the API, the links can easily get messy. In that
  case, we typically only link the first mention of an object and not any
  subsequent ones.
  - ✅ The [`Span`](/api/span) and [`Token`](/api/token) objects are views of a
    [`Doc`](/api/doc). [`Span.as_doc`](/api/span#as_doc) creates a `Doc` object
    from a `Span`.
  - ❌ The [`Span`](/api/span) and [`Token`](/api/token) objects are views of a
    [`Doc`](/api/doc). [`Span.as_doc`](/api/span#as_doc) creates a
    [`Doc`](/api/doc) object from a [`Span`](/api/span).

* Other things we format as code are: references to trained pipeline packages
  like `en_core_web_sm` or file names like `code.py` or `meta.json`.

  - ✅ After training, the `config.cfg` is saved to disk.

* [Type annotations](#type-annotations) are a special type of code formatting,
  expressed by wrapping the text in `~~` instead of backticks. The result looks
  like this: ~~List[Doc]~~. All references to known types will be linked
  automatically.

  - ✅ The model has the input type ~~List[Doc]~~ and it outputs a
    ~~List[Array2d]~~.

* We try to keep links meaningful but short.
  - ✅ For details, see the usage guide on
    [training with custom code](/usage/training#custom-code).
  - ❌ For details, see
    [the usage guide on training with custom code](/usage/training#custom-code).
  - ❌ For details, see the usage guide on training with custom code
    [here](/usage/training#custom-code).
