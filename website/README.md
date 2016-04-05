# Source files for the spacy.io website and docs

The [spacy.io](https://spacy.io) website is implemented in [Jade (aka Pug)](https://www.jade-lang.org), and is built or served by [Harp](https://harpjs.com).

## Building the site

To build the site and start making changes:

    sudo npm install --global harp
    git clone https://github.com/spacy-io/website
    cd website
    harp server

This will serve the site on [http://localhost:9000](http://localhost:9000). You can then edit the jade source and refresh the page to see your changes.

## Reading the source

Jade is an extensible templating language with a readable syntax, that compiles to HTML.
The website source makes extensive use of Jade mixins, so that the design system is abstracted away from the content you're
writing. You can read more about our approach in our blog post, ["Rebuilding a Website with Modular Markup Components"](https://spacy.io/blog/modular-markup).

If you want to write or edit the pages, the site's [styleguide](http://spacy.io/styleguide) serves as a useful reference of the available mixins.
