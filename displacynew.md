### displacy.parse_deps {#displacy.parse_deps tag="method" new="2"}

Generate dependency parse in `{'words': [], 'arcs': []}` format.
For use with the `manual=True` argument in `displacy.render`.

> #### Example
>
> ```python
> import spacy
> from spacy import displacy
> nlp = spacy.load("en_core_web_sm")
> doc = nlp("This is a sentence.")
> deps_parse = displacy.parse_deps(doc)
> html = displacy.render(deps_parse, style="dep", manual=True)
> ```

| Name        | Description                                                         |
| ----------- | ------------------------------------------------------------------- |
| `doc`       | Doc to parse dependencies. ~~Doc~~                                  |
| `options`   | Dependency parse specific visualisation options. ~~Dict[str, Any]~~ |
| **RETURNS** | Generated dependency parse keyed by words and arcs. ~~dict~~        |

### displacy.parse_ents {#displacy.parse_ents tag="method" new="2"}

Generate named entities in `[{start: i, end: i, label: 'label'}]` format.
For use with the `manual=True` argument in `displacy.render`.

> #### Example
>
> ```python
> import spacy
> from spacy import displacy
> nlp = spacy.load("en_core_web_sm")
> doc = nlp("But Google is starting from behind.")
> ents_parse = displacy.parse_ents(doc)
> html = displacy.render(ents_parse, style="ent", manual=True)
> ```

| Name        | Description                                                         |
| ----------- | ------------------------------------------------------------------- |
| `doc`       | Doc to parse entities. ~~Doc~~                                      |
| `options`   | NER-specific visualisation options. ~~Dict[str, Any]~~              |
| **RETURNS** | Generated entities keyed by text (original text) and ents. ~~dict~~ |

### displacy.parse_spans {#displacy.parse_ents tag="method" new="2"}

Generate spans in `[{start_token: i, end_token: i, label: 'label'}]` format.
For use with the `manual=True` argument in `displacy.render`.

> #### Example
>
> ```python
> import spacy
> from spacy import displacy
> nlp = spacy.load("en_core_web_sm")
> doc = nlp("But Google is starting from behind.")
> ents_parse = displacy.parse_ents(doc)
> html = displacy.render(ents_parse, style="ent", manual=True)
> ```

| Name        | Description                                                         |
| ----------- | ------------------------------------------------------------------- |
| `doc`       | Doc to parse entities. ~~Doc~~                                      |
| `options`   | Span-specific visualisation options. ~~Dict[str, Any]~~             |
| **RETURNS** | Generated entities keyed by text (original text) and ents. ~~dict~~ |

