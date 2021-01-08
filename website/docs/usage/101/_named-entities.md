A named entity is a "real-world object" that's assigned a name – for example, a
person, a country, a product or a book title. spaCy can **recognize various
types of named entities in a document, by asking the model for a
prediction**. Because models are statistical and strongly depend on the
examples they were trained on, this doesn't always work _perfectly_ and might
need some tuning later, depending on your use case.

Named entities are available as the `ents` property of a `Doc`:

```python
### {executable="true"}
import spacy

nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying U.K. startup for $1 billion")

for ent in doc.ents:
    print(ent.text, ent.start_char, ent.end_char, ent.label_)
```

> - **Text:** The original entity text.
> - **Start:** Index of start of entity in the `Doc`.
> - **End:** Index of end of entity in the `Doc`.
> - **Label:** Entity label, i.e. type.

| Text        | Start | End | Label   | Description                                          |
| ----------- | :---: | :-: | ------- | ---------------------------------------------------- |
| Apple       |   0   |  5  | `ORG`   | Companies, agencies, institutions.                   |
| U.K.        |  27   | 31  | `GPE`   | Geopolitical entity, i.e. countries, cities, states. |
| \$1 billion |  44   | 54  | `MONEY` | Monetary values, including unit.                     |

Using spaCy's built-in [displaCy visualizer](/usage/visualizers), here's what
our example sentence and its named entities look like:

import DisplaCyEntHtml from 'images/displacy-ent1.html'; import { Iframe } from
'components/embed'

<Iframe title="displaCy visualization of entities" html={DisplaCyEntHtml} height={100} />
