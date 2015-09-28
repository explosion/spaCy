all: src/code site

src/code: tests/test_*.py
	mkdir -p src/code/
	./create_code_samples tests/ src/code/

site: site/index.html site/blog/ site/docs/ site/license/ site/blog/introducing-spacy/ site/blog/parsing-english-in-python/ site/blog/part-of-speech-POS-tagger-in-python/ site/tutorials/twitter-filter/ site/tutorials/syntax-search/ site/tutorials/mark-adverbs/ site/blog/writing-c-in-cython/ site/blog/how-spacy-works/

site/index.html: src/jade/header.jade src/jade/*.jade
	jade -P src/jade/home/index.jade --out site/

site/docs/: src/jade/docs/*.jade src/jade/header.jade
	jade -P src/jade/docs/index.jade --out $@

site/license/: src/jade/license/*.jade src/jade/header.jade 
	jade -P src/jade/license/index.jade --out $@

site/blog/: src/jade/blog/*.jade site/blog/*/ site/tutorials/*/ src/jade/header.jade
	jade -P src/jade/blog/index.jade --out $@

site/tutorials/: src/jade/tutorials/*.jade site/tutorials/*/ src/jade/header.jade
	jade -P src/jade/tutorials/index.jade --out $@

site/blog/parsing-english-in-python/: src/jade/blog/parsing-english-in-python/*.jade src/jade/header.jade
	jade -P $< --out $@


site/blog/writing-c-in-cython/: src/jade/blog/writing-c-in-cython/*.jade src/jade/header.jade
	jade -P $< --out $@


site/blog/part-of-speech-POS-tagger-in-python/: src/jade/blog/part-of-speech-POS-tagger-in-python/*.jade src/jade/header.jade
	jade -P $< --out $@

site/blog/introducing-spacy/: src/jade/blog/introducing-spacy/*.jade src/jade/header.jade
	jade -P $< --out $@

site/blog/displacy/: src/jade/blog/displacy/*.jade src/jade/header.jade
	jade -P $< --out $@

site/blog/eli5-computers-learn-reading: src/jade/blog/eli5-computers-learn-reading/*.jade src/jade/header.jade
	jade -P $< --out $@

site/tutorials/mark-adverbs/: src/jade/tutorials/mark-adverbs/*.jade src/jade/header.jade
	jade -P $< --out $@

site/blog/how-spacy-works/: src/jade/blog/how-spacy-works/*.jade src/jade/header.jade
	jade -P $< --out $@

site/tutorials/syntax-search/: src/jade/tutorials/syntax-search/*.jade src/jade/header.jade
	jade -P $< --out $@

site/tutorials/twitter-filter/: src/jade/tutorials/twitter-filter/*.jade src/jade/header.jade
	jade -P $< --out $@

