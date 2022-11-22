# spacy.io website and docs

![Netlify Status](https://api.netlify.com/api/v1/badges/d65fe97d-99ab-47f8-a339-1d8987251da0/deploy-status)

The styleguide for the spaCy website is available at
[spacy.io/styleguide](https://spacy.io/styleguide).

## Setup and installation

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

## Building & developing the site with Docker

Sometimes it's hard to get a local environment working due to rapid updates to
node dependencies, so it may be easier to use docker for building the docs.

If you'd like to do this, **be sure you do _not_ include your local
`node_modules` folder**, since there are some dependencies that need to be built
for the image system. Rename it before using.

```bash
docker run -it \
  -v $(pwd):/spacy-io/website \
  -p 8000:8000 \
  ghcr.io/explosion/spacy-io \
  gatsby develop -H 0.0.0.0
```

This will allow you to access the built website at http://0.0.0.0:8000/ in your
browser, and still edit code in your editor while having the site reflect those
changes.

**Note**: If you're working on a Mac with an M1 processor, you might see
segfault errors from `qemu` if you use the default image. To fix this use the
`arm64` tagged image in the `docker run` command
(ghcr.io/explosion/spacy-io:arm64).

### Building the Docker image

If you'd like to build the image locally, you can do so like this:

```bash
docker build -t spacy-io .
```

This will take some time, so if you want to use the prebuilt image you'll save a
bit of time.

## Project structure

```yaml
├── docs                 # the actual markdown content
├── meta                 # JSON-formatted site metadata
|   ├── languages.json   # supported languages and statistical models
|   ├── sidebars.json    # sidebar navigations for different sections
|   ├── site.json        # general site metadata
|   ├── type-annotations.json # Type annotations
|   └── universe.json    # data for the spaCy universe section
├── public               # compiled site
├── setup                # Jinja setup
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
├── .eslintrc.json       # ESLint config file
├── .prettierrc          # Prettier config file
├── gatsby-browser.js    # browser-specific hooks for Gatsby
├── gatsby-config.js     # Gatsby configuration
├── gatsby-node.js       # Node-specific hooks for Gatsby
└── package.json         # package settings and dependencies
```
