<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# Contribute to spaCy

Following the v1.0 release, it's time to welcome more contributors into the spaCy project and code base 🎉 This page will give you a quick overview of how things are organised and most importantly, how to get involved.

## Table of contents
1. [Issues and bug reports](#issues-and-bug-reports)
2. [Contributing to the code base](#contributing-to-the-code-base)
3. [Updating the website](#updating-the-website)
4. [Submitting a tutorial](#submitting-a-tutorial)
5. [Submitting a project to the showcase](#submitting-a-project-to-the-showcase)
6. [Code of conduct](#code-of-conduct)

## Issues and bug reports

First, [do a quick search](https://github.com/issues?q=+is%3Aissue+user%3Aexplosion) to see if the issue has already been reported. If so, it's often better to just leave a comment on an existing issue, rather than creating a new one.

If you're looking for help with your code, consider posting a question on [StackOverflow](http://stackoverflow.com/questions/tagged/spacy) instead. If you tag it `spacy` and `python`, more people will see it and hopefully be able to help.

When opening an issue, use a descriptive title and include your environment (operating system, Python version, spaCy version). Our [issue template](https://github.com/explosion/spaCy/issues/new) helps you remember the most important details to include.

If you've discovered a bug, you can also submit a [regression test](#fixing-bugs) straight away. When you're opening an issue to report the bug, simply refer to your pull request in the issue body.

### Issue labels

We use the following system to tag our issues:

| Issue label | Description |
| --- | --- |
| [`bug`](https://github.com/explosion/spaCy/labels/bug) | Bugs and behaviour differing from documentation |
| [`enhancement`](https://github.com/explosion/spaCy/labels/enhancement) | Feature requests and improvements |
| [`install`](https://github.com/explosion/spaCy/labels/install) | Installation problems |
| [`performance`](https://github.com/explosion/spaCy/labels/performance) | Accuracy, speed and memory use problems |
| [`tests`](https://github.com/explosion/spaCy/labels/tests) | Missing or incorrect [tests](spacy/tests) |
| [`linux`](https://github.com/explosion/spaCy/labels/linux), [`osx`](https://github.com/explosion/spaCy/labels/osx), [`windows`](https://github.com/explosion/spaCy/labels/windows) | Issues related to the specific operating systems |
| [`pip`](https://github.com/explosion/spaCy/labels/pip), [`conda`](https://github.com/explosion/spaCy/labels/conda) | Issues related to the specific package managers |
| [`duplicate`](https://github.com/explosion/spaCy/labels/duplicate) | Duplicates, i.e. issues that have been reported before |
| [`help wanted`](https://github.com/explosion/spaCy/labels/help%20wanted) | Requests for contributions |


## Contributing to the code base

Coming soon.


### Conventions for Python

Coming soon.


### Conventions for Cython

Coming soon.


### Fixing bugs

When fixing a bug, first create an [issue](https://github.com/explosion/spaCy/issues) if one does not already exist. The description text can be very short – we don't want to make this too bureaucratic. Next, create a test file named `test_issue[ISSUE NUMBER].py` in the [`spacy/tests/regression`](spacy/tests/regression) folder.

Test for the bug you're fixing, and make sure the test fails. If the test requires the models to be loaded, mark it with the `pytest.mark.models` decorator.

Next, add and commit your test file referencing the issue number in the commit message. Finally, fix the bug, make sure your test passes and reference the issue in your commit message.


## Updating the website

Our [website and docs](https://spacy.io) are implemented in [Jade/Pug](https://www.jade-lang.org), and built or served by [Harp](https://harpjs.com). Jade/Pug is an extensible templating language with a readable syntax, that compiles to HTML. Here's how to view the site locally:

```bash
sudo npm install --global harp
git clone https://github.com/explosion/spaCy
cd website
harp server
```

The docs can always use another example or more detail, and they should always be up to date and not misleading. To quickly find the correct file to edit, simply click on the "Suggest edits" button at the bottom of a page.

To make it easy to add content components, we use a [collection of custom mixins](_includes/_mixins.jade), like `+table`, `+list` or `+code`. For more info and troubleshooting guides, check out the [website README](website).

### Resources to get you started

* [Guide to static websites with Harp and Jade](https://ines.io/blog/the-ultimate-guide-static-websites-harp-jade) (ines.io)
* [Building a website with modular markup components (mixins)](https://explosion.ai/blog/modular-markup) (explosion.ai)
* [Jade/Pug documentation](https://pugjs.org) (pugjs.org)
* [Harp documentation](https://harpjs.com/) (harpjs.com)


## Submitting a tutorial

Did you write a [tutorial](https://spacy.io/docs/usage/tutorials) to help others use spaCy, or did you come across one that should be added to our directory? You can submit it by making a pull request to [`website/docs/usage/_data.json`](website/docs/usage/_data.json):

```json
{
    "tutorials": {
        "deep_dives": {
            "Deep Learning with custom pipelines and Keras": {
                "url": "https://explosion.ai/blog/spacy-deep-learning-keras",
                "author": "Matthew Honnibal",
                "tags": [ "keras", "sentiment" ]
            }
        }
    }
}
```

### A few tips

* A suitable tutorial should provide additional content and practical examples that are not covered as such in the docs.
* Make sure to choose the right category – `first_steps`, `deep_dives` (tutorials that take a deeper look at specific features) or `code` (programs and scripts on GitHub etc.).
* Don't go overboard with the tags. Take inspirations from the existing ones and only add tags for features (`"sentiment"`, `"pos"`) or integrations (`"jupyter"`, `"keras"`).
* Double-check the JSON markup and/or use a linter. A wrong or missing comma will (unfortunately) break the site rendering.

## Submitting a project to the showcase

Have you built a library, visualizer, demo or product with spaCy, or did you come across one that should be featured in our [showcase](https://spacy.io/docs/usage/showcase)? You can submit it by making a pull request to [`website/docs/usage/_data.json`](website/docs/usage/_data.json):

```json
{
    "showcase": {
        "visualizations": {
            "displaCy": {
                "url": "https://demos.explosion.ai/displacy",
                "author": "Ines Montani",
                "description": "An open-source NLP visualiser for the modern web",
                "image": "displacy.jpg"
            }
        }
    }
}
```

### A few tips

* A suitable third-party library should add substantial functionality, be well-documented and open-source. If it's just a code snippet or script, consider submitting it to the `code` category of the tutorials section instead.
* A suitable demo should be hosted and accessible online. Open-source code is always a plus.
* For visualizations and products, add an image that clearly shows how it looks – screenshots are ideal.
* The image should be resized to 300x188px, optimised using a tool like [ImageOptim](https://imageoptim.com/mac) and added to [`website/assets/img/showcase`](website/assets/img/showcase).
* Double-check the JSON markup and/or use a linter. A wrong or missing comma will (unfortunately) break the site rendering.

## Code of conduct

spaCy adheres to the [Contributor Covenant Code of Conduct](http://contributor-covenant.org/version/1/4/). By participating, you are expected to uphold this code.
