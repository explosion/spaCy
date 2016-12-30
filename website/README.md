<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spacy.io website and docs

The [spacy.io](https://spacy.io) website is implemented in [Jade (aka Pug)](https://www.jade-lang.org), and is built or served by [Harp](https://harpjs.com). Jade is an extensible templating language with a readable syntax, that compiles to HTML.
The website source makes extensive use of Jade mixins, so that the design system is abstracted away from the content you're
writing. You can read more about our approach in our blog post, ["Rebuilding a Website with Modular Markup"](https://explosion.ai/blog/modular-markup).


## Viewing the site locally

```bash
sudo npm install --global harp
git clone https://github.com/explosion/spaCy
cd spaCy/website
harp server
```

This will serve the site on [http://localhost:9000](http://localhost:9000).


## Making changes to the site

The docs can always use another example or more detail, and they should always be up to date and not misleading. If you see something, say something – we always appreciate a [pull request](https://github.com/explosion/spaCy/pulls). To quickly find the correct file to edit, simply click on the "Suggest edits" button at the bottom of a page.

### File structure

While all page content lives in the `.jade` files, article meta (page titles, sidebars etc.) is stored as JSON. Each folder contains a `_data.json` with all required meta for its files.

For simplicity, all sites linked in the [tutorials](https://spacy.io/docs/usage/tutorials) and [showcase](https://spacy.io/docs/usage/showcase) are also stored as JSON. So in order to edit those pages, there's no need to dig into the Jade files – simply edit the [`_data.json`](docs/usage/_data.json).

### Markup language and conventions

Jade/Pug is a whitespace-sensitive markup language that compiles to HTML. Indentation is used to nest elements, and for template logic, like `if`/`else` or `for`, mainly used to iterate over objects and arrays in the meta data. It also allows inline JavaScript expressions.

For an overview of Harp and Jade, see [this blog post](https://ines.io/blog/the-ultimate-guide-static-websites-harp-jade). For more info on the Jade/Pug syntax, check out their [documentation](https://pugjs.org).

In the [spacy.io](https://spacy.io) source, we use 4 spaces to indent and hard-wrap at 80 characters.

```pug
p This is a very short paragraph. It stays inline.

p
    |  This is a much longer paragraph. It's hard-wrapped at 80 characters to
    |  make it easier to read on GitHub and in editors that do not have soft
    |  wrapping enabled. To prevent Jade from interpreting each line as a new
    |  element, it's prefixed with a pipe and two spaces. This ensures that no
    |  spaces are dropped – for example, if your editor strips out trailing
    |  whitespace by default. Inline links are added using the inline syntax,
    |  like this: #[+a("https://google.com") Google].
```

Note that for external links, `+a("...")` is used instead of `a(href="...")` – it's a mixin that takes care of adding all required attributes. If possible, always use a mixin instead of regular HTML elements. The only plain HTML elements we use are:

| Element | Description |
| --- | --- |
| `p` | paragraphs |
| `code` | inline `code` |
| `em` | *italicized* text |
| `strong` | **bold** text |

### Mixins

Each file includes a collection of [custom mixins](_includes/_mixins.jade) that make it easier to add content components – no HTML or class names required.

For example:
```pug
//- Bulleted list

+list
    +item This is a list item.
    +item This is another list item.

//- Table with header

+table([ "Header one", "Header two" ])
    +row
        +cell Table cell
        +cell Another one

    +row
        +cell And one more.
        +cell And the last one.

//- Headlines with optional permalinks

+h(2, "link-id") Headline 2 with link to #link-id
```

Code blocks are implemented using `+code` or `+aside-code` (to display them in the right sidebar). A `.` is added after the mixin call to preserve whitespace:

```pug
+code("This is a label").
    import spacy
    en_nlp = spacy.load('en')
    en_doc = en_nlp(u'Hello, world. Here are two sentences.')
```

You can find the documentation for the available mixins in [`_includes/_mixins.jade`](_includes/_mixins.jade).

### Helpers for linking to content

Aside from the `+a()` mixin, there are three other helpers to make linking to content more convenient.

#### Linking to GitHub

Since GitHub links can be long and tricky, you can use the `gh()` function to generate them automatically for spaCy and all repositories owned by [explosion](https://github.com/explosion):

```javascript
// Syntax: gh(repo, [file], [branch])

gh("spaCy", "spacy/matcher.pyx")
// https://github.com/explosion/spaCy/blob/master/spacy/matcher.pyx

```

#### Linking to source

`+src()` generates a link with a little source icon to indicate it's linking to a code source. Ideally, it's used in combination with `gh()`:

```pug
+src(gh("spaCy", "spacy/matcher.pyx")) matcher.pxy
```

#### Linking to API reference

`+api()` generates a link to a page in the API docs, with an added icon. It should only be used across the workflows in the usage section, and only on the first mention of the respective class.

It takes the slug of an API page as the argument. You can also use anchors to link to specific sections – they're usually the method or property names.

```pug
+api("tokenizer") #[code Tokenizer]
+api("doc#similarity") #[code Doc.similarity()]
```

### Most common causes of compile errors

| Problem | Fix |
| --- | --- |
| JSON formatting errors | make sure last elements of objects don't end with commas and/or use a JSON linter |
| unescaped characters like `<` or `>` and sometimes `'` in inline elements | replace with encoded version: `&lt;`, `&gt;` etc. |
| "Cannot read property 'call' of undefined" / "foo is not a function" | make sure mixin names are spelled correctly and mixins file is included with the correct path |
| "no closing bracket found" | make sure inline elements end with a `]`, like `#[code spacy.load('en')]` and for nested inline elements, make sure they're all on the same line and contain spaces between them (**bad:** `#[+api("doc")#[code Doc]]`) |

If Harp fails and throws a Jade error, don't take the reported line number at face value – it's often wrong, as the page is compiled from templates and several files.
