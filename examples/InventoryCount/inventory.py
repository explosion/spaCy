class Inventory:
    """
        Inventory class - a struct{} like feature to house inventory counts
        across modules.
    """
    originalQuery = None
    item = ""
    unit = ""
    amount = ""

    def __init__(self, statement):
        """
        Constructor - only takes in the original query/statement
        :return: new Inventory object
        """

        self.originalQuery = statement
        pass

    def __str__(self):
        return str(self.amount) + ' ' + str(self.unit) + ' ' + str(self.item)

    def printInfo(self):
        print '-------------Inventory Count------------'
        print "Original Query:  " + str(self.originalQuery)
        print 'Amount:  ' + str(self.amount)
        print 'Unit:    ' + str(self.unit)
        print 'Item:    ' + str(self.item)
        print '----------------------------------------'

    def isValid(self):
        if not self.item or not self.unit or not self.amount or not self.originalQuery:
            return False
        else:
            return True
