from inventory import Inventory


def runTest(nlp):
    testset = []
    testset += [nlp(u'6 lobster cakes')]
    testset += [nlp(u'6 avacados')]
    testset += [nlp(u'fifty five carrots')]
    testset += [nlp(u'i have 55 carrots')]
    testset += [nlp(u'i got me some 9 cabbages')]
    testset += [nlp(u'i got 65 kgs of carrots')]

    result = []
    for doc in testset:
        c = decodeInventoryEntry_level1(doc)
        if not c.isValid():
            c = decodeInventoryEntry_level2(doc)
        result.append(c)

    for i in result:
        i.printInfo()


def decodeInventoryEntry_level1(document):
    """
    Decodes a basic entry such as: '6 lobster cake' or '6' cakes
    @param document : NLP Doc object
    :return: Status if decoded correctly (true, false), and Inventory object
    """
    count = Inventory(str(document))
    for token in document:
        if token.pos_ == (u'NOUN' or u'NNS' or u'NN'):
            item = str(token)

            for child in token.children:
                if child.dep_ == u'compound' or child.dep_ == u'ad':
                    item = str(child) + str(item)
                elif child.dep_ == u'nummod':
                    count.amount = str(child).strip()
                    for numerical_child in child.children:
                        # this isn't arithmetic rather than treating it such as a string
                        count.amount = str(numerical_child) + str(count.amount).strip()
                else:
                    print "WARNING: unknown child: " + str(child) + ':'+str(child.dep_)

            count.item = item
            count.unit = item

    return count


def decodeInventoryEntry_level2(document):
    """
    Entry level 2, a more complicated parsing scheme that covers examples such as
    'i have 80 boxes of freshly baked pies'

    @document @param document : NLP Doc object
    :return: Status if decoded correctly (true, false), and Inventory object-
    """

    count = Inventory(str(document))

    for token in document:
        #  Look for a preposition object that is a noun (this is the item we are counting).
        #  If found, look at its' dependency (if a preposition that is not indicative of
        #  inventory location, the dependency of the preposition must be a noun

        if token.dep_ == (u'pobj' or u'meta') and token.pos_ == (u'NOUN' or u'NNS' or u'NN'):
            item = ''

            #  Go through all the token's children, these are possible adjectives and other add-ons
            #  this deals with cases such as 'hollow rounded waffle pancakes"
            for i in token.children:
                item += ' ' + str(i)

            item += ' ' + str(token)
            count.item = item

            # Get the head of the item:
            if token.head.dep_ != u'prep':
                #  Break out of the loop, this is a confusing entry
                break
            else:
                amountUnit = token.head.head
                count.unit = str(amountUnit)

                for inner in amountUnit.children:
                    if inner.pos_ == u'NUM':
                        count.amount += str(inner)
    return count


