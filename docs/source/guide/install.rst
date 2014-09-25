Installation
============

pip install spacy
-----------------

The easiest way to install is from PyPi via pip::

    pip install spacy

git clone http://github.com/honnibal/spaCy.git
----------------------------------------------

Installation From source via `GitHub <https://github.com/honnibal/spaCy>`_, using virtualenv::

    $ git clone http://github.com/honnibal/spaCy.git
    $ cd spaCy
    $ virtualenv .env
    $ source .env/bin/activate
    $ pip install -r requirements.txt
    $ fab make
    $ fab test
