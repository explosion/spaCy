import plac

from spacy.en import English
from spacy.parts_of_speech import NOUN
from spacy.parts_of_speech import ADP as PREP


def _span_to_tuple(span):
    start = span[0].idx
    end = span[-1].idx + len(span[-1])
    tag = span.root.tag_
    text = span.text
    label = span.label_
    return (start, end, tag, text, label)

def merge_spans(spans, doc):
    # This is a bit awkward atm. What we're doing here is merging the entities,
    # so that each only takes up a single token. But an entity is a Span, and
    # each Span is a view into the doc. When we merge a span, we invalidate
    # the other spans. This will get fixed --- but for now the solution
    # is to gather the information first, before merging.
    tuples = [_span_to_tuple(span) for span in spans]
    for span_tuple in tuples:
        doc.merge(*span_tuple)


def extract_currency_relations(doc):
    merge_spans(doc.ents, doc)
    merge_spans(doc.noun_chunks, doc)

    relations = []
    for money in filter(lambda w: w.ent_type_ == 'MONEY', doc):
        if money.dep_ in ('attr', 'dobj'):
            subject = [w for w in money.head.lefts if w.dep_ == 'nsubj']
            if subject:
                subject = subject[0]
                relations.append((subject, money))
        elif money.dep_ == 'pobj' and money.head.dep_ == 'prep':
            relations.append((money.head.head, money))
 
    return relations


def main():
    nlp = English()
    texts = [
        u'Net income was $9.4 million compared to the prior year of $2.7 million.',
        u'Revenue exceeded twelve billion dollars, with a loss of $1b.',
    ]
               
    for text in texts:
        doc = nlp(text)
        relations = extract_currency_relations(doc)
        for r1, r2 in relations:
            print(r1.text, r2.ent_type_, r2.text)


if __name__ == '__main__':
    plac.call(main)
