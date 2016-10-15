<a href="https://explosion.ai"><img src="https://explosion.ai/assets/img/logo.svg" width="125" height="125" align="right" /></a>

# Source files for the spacy.io website and docs

The [spacy.io](https://spacy.io) website is implemented in [Jade (aka Pug)](https://www.jade-lang.org), and is built or served by [Harp](https://harpjs.com). Jade is an extensible templating language with a readable syntax, that compiles to HTML.
The website source makes extensive use of Jade mixins, so that the design system is abstracted away from the content you're
writing. You can read more about our approach in our blog post, ["Rebuilding a Website with Modular Markup Components"](https://explosion.ai/blog/modular-markup).


## Building the site

```bash
sudo npm install --global harp
git clone https://github.com/explosion/spacy
cd website
harp server
```

This will serve the site on [http://localhost:9000](http://localhost:9000).
