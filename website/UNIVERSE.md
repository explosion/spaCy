<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# spaCy Universe

The [spaCy Universe](https://spacy.io/universe) collects the many great resources developed with or for spaCy. It
includes standalone packages, plugins, extensions, educational materials,
operational utilities and bindings for other languages.

If you have a project that you want the spaCy community to make use of, you can
suggest it by submitting a pull request to this repository. The Universe
database is open-source and collected in a simple JSON file.

Looking for inspiration for your own spaCy plugin or extension? Check out the
[`project ideas`](https://github.com/explosion/spaCy/discussions?discussions_q=category%3A%22New+Features+%26+Project+Ideas%22) 
discussion forum.

## Checklist

### Projects

✅ Libraries and packages should be **open-source** (with a user-friendly license) and at least somewhat **documented** (e.g. a simple `README` with usage instructions).

✅ We're happy to include work in progress and prereleases, but we'd like to keep the emphasis on projects that should be useful to the community **right away**.

✅ Demos and visualizers should be available via a **public URL**.

### Educational Materials

✅ Books should be **available for purchase or download** (not just pre-order). Ebooks and self-published books are fine, too, if they include enough substantial content.

✅ The `"url"` of book entries should either point to the publisher's website or a reseller of your choice (ideally one that ships worldwide or as close as possible).

✅ If an online course is only available behind a paywall, it should at least have a **free excerpt** or chapter available, so users know what to expect.

## JSON format

To add a project, fork this repository, edit the [`universe.json`](meta/universe.json)
and add an object of the following format to the list of `"resources"`. Before
you submit your pull request, make sure to use a linter to verify that your
markup is correct.

```json
{
    "id": "unique-project-id",
    "title": "Project title",
    "slogan": "A short summary",
    "description": "A longer description – *Markdown allowed!*",
    "github": "user/repo",
    "pip": "package-name",
    "code_example": [
        "import spacy",
        "import package_name",
        "",
        "nlp = spacy.load('en')",
        "nlp.add_pipe(package_name)"
    ],
    "code_language": "python",
    "url": "https://example.com",
    "thumb": "https://example.com/thumb.jpg",
    "image": "https://example.com/image.jpg",
    "author": "Your Name",
    "author_links": {
        "twitter": "username",
        "github": "username",
        "website": "https://example.com"
    },
    "category": ["pipeline", "standalone"],
    "tags": ["some-tag", "etc"]
}
```

|  Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique ID of the project. |
| `title` | string | Project title. If not set, the `id` will be used as the display title. |
| `slogan` | string | A short description of the project. Displayed in the overview and under the title. |
| `description` | string | A longer description of the project. Markdown is allowed, but should be limited to basic formatting like bold, italics, code or links. |
| `github` | string | Associated GitHub repo in the format `user/repo`. Will be displayed as a link and used for release, license and star badges. |
| `pip` | string | Package name on pip. If available, the installation command will be displayed. |
| `cran` | string | For R packages: package name on CRAN. If available, the installation command will be displayed. |
| `code_example` | array | Short example that shows how to use the project. Formatted as an array with one string per line. |
| `code_language` | string | Defaults to `'python'`. Optional code language used for syntax highlighting with [Prism](http://prismjs.com/). |
| `url` | string | Optional project link to display as button. |
| `thumb` | string | Optional URL to project thumbnail to display in overview and project header. Recommended size is 100x100px. |
| `image` | string | Optional URL to project image to display with description. |
| `author` | string | Name(s) of project author(s). |
| `author_links` | object | Usernames and links to display as icons to author info. Currently supports `twitter` and `github` usernames, as well as `website` link. |
| `category` | list | One or more categories to assign to project. Must be one of the available options. |
| `tags` | list | Still experimental and not used for filtering: one or more tags to assign to project. |

To separate them from the projects, educational materials also specify
`"type": "education`. Books can also set a `"cover"` field containing a URL
to a cover image. If available, it's used in the overview and displayed on
the individual book page.
