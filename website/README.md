Source for spacy.io
==============================

This directory contains the source for official spaCy website at http://spacy.io/.

Fixes, updates and suggestions are welcome.


Releases
--------
Changes made to this directory go live on spacy.io.  <When / how often?>


The Stack
--------
The site is built with the [Jade](http://jade-lang.com/) template language.

See [the Makefile](Makefile) for more


Developing
--------
To make and test changes
```
  npm install jade --global
  cd website
  make
  python -m SimpleHTTPServer 8000
```
Then visit [localhost:8000/src/...](http://localhost:8000/src/)
