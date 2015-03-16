from math import log

from fractions import Fraction

from myresult import *

Fl = lambda x: Fraction.from_float(x)

def yieldParts(maxlen, field_max_size = None, minlen = None):
    """
    yields all (start index, end index + 1) pairs 
    >>> for i in yieldParts(4,4,1):
    ...  print i
    ... 
    (0, 1)
    (0, 2)
    (0, 3)
    (0, 4)
    (1, 2)
    (1, 3)
    (1, 4)
    (2, 3)
    (2, 4)
    (3, 4)
    """
    if field_max_size == None:
        field_max_size = maxlen
    if minlen == None:
        minlen = 1

    for i in range(maxlen + 1 - minlen):
        for j in range(i+minlen, min(maxlen, i + field_max_size) + 1  ):
            yield (i,j)

class MyWindowSummer:
    def __init__(self):
        self.yieldParts = yieldParts

        
        self.differentLengths = None
        self.fieldMaxSize = None
        self.fieldMinSize = None
        self.maxSymbols = 256
        self.strings = None

        self.maxStrlen = None
        self.result = None
        self.uses = None

        self.resultClass = None
        
    def validateClassValues(self):
        if type(self.strings) != type([]) or len(self.strings) == 0 or type(self.strings[0]) != type(" "):
            raise ValueError('self.strings')
        if type(self.maxSymbols) not in [type(1), type(1L)] or self.maxSymbols <= 0:
            raise ValueError('self.maxSymbols')
        if self.differentLengths not in [True, False]:
            raise ValueError('self.differentLengths')
        if self.fieldMaxSize != None and (
            type(self.fieldMaxSize) not in [type(1), type(1L)] or self.fieldMaxSize <= 0):
            raise ValueError('self.fieldMaxSize')
        if self.fieldMinSize != None and (
            type(self.fieldMinSize) not in [type(1), type(1L)] or self.fieldMinSize <= 0):
            raise ValueError('self.fieldMinSize')
        if not issubclass(self.resultClass, MyResult):
            raise ValueError('self.resultClass')
        return True

    def calculateLocals(self):
        self.maxlen = max([len(i) for i in self.strings])
        
        if self.fieldMaxSize == None:
            self.fieldMaxSize = self.maxlen
        
        if self.fieldMinSize == None:
            self.fieldMinSize = 1
    
    def calculate(self):
        self.validateClassValues()
        self.calculateLocals()

        result = self.resultClass(self.fieldMaxSize, self.fieldMinSize, self.maxlen)

        for part in self.yieldParts(self.maxlen, self.fieldMaxSize, self.fieldMinSize):
            added = self.calculatePart(part)
            self.addToResult(added,part,result)
        result.divideUses()
        return result

    
    def claculateDistribution(self,(start,end)):
        n = {}
        N = 0
        for x in [
            s[start:end] 
            for s in self.strings 
            if not self.differentLengths or len(s[start:end]) == end - start
            ]:
            #optimize
            n.setdefault(x,0)
            n[x] += 1
            N += 1
        return n, N


    def addToResult(self,added,part,result):
        result.addField(added, part)
    

    def calculatePart(self, part):
        """ this should return an integer, long or fraction"""
        raise NotImplementedError

    

class FieldSubWords(MyWindowSummer):
    """one (and I) could write a book about how to optimize this one ..."""
    def getSubwords(self,(start,end)):
        lengthOfPart = end - start
        subwords = set([])
        for (partStart,partEnd) in self.yieldParts(lengthOfPart, 
                                                   lengthOfPart, 
                                                   self.fieldMinSize):
            words = set([s[start+partStart:start+partEnd] for s in self.strings ])
            #print start+partStart,start+partEnd,words

            subwords = subwords.union(words)
        if self.differentLengths:
            subwords.discard('')

        return subwords

    def calculatePart(self,(start,end)):        
        #print (start,end), len(subwords)
        return Fraction(len(self.getSubwords((start,end))))

class CommonFieldSubWords(MyWindowSummer):
    """one (and I) could write a book about how to optimize this one ..."""
    """copypastecode"""
    def __init__(self):
        MyWindowSummer.__init__(self)
        self.fixedSubFieldSize = None


    def validateClassValues(self):
        MyWindowSummer.validateClassValues(self)
        """why to bother with an error message?"""
        if self.fieldMinSize == 1:
            self.fieldMinSize = 2
        try:
            if self.fixedSubFieldSize != None:
                self.fixedSubFieldSize = int(self.fixedSubFieldSize)
                self.fieldMinSize = self.fixedSubFieldSize
        except:
            raise ValueError('self.fixedSubFieldSize')
        if self.fixedSubFieldSize < self.fieldMinSize or self.fixedSubFieldSize > self.fieldMaxSize:
            raise ValueError('self.fixedSubFieldSize')
    
    def calculateLocals(self):
        MyWindowSummer.calculateLocals(self)
        self.minsubsize = self.fieldMinSize
        if self.fixedSubFieldSize != None:
            self.maxsubsize = self.fixedSubFieldSize
            self.minsubsize = self.fixedSubFieldSize

    def getSubwords(self,(start,end)):
        lengthOfPart = end - start
        subwords = {}
        
        for (partStart,partEnd) in self.yieldParts(lengthOfPart, 
                                                   lengthOfPart, 
                                                   self.minsubsize):
            words = set([s[start+partStart:start+partEnd] for s in self.strings ])
            #print start+partStart,start+partEnd,words
            subdist, _ = self.claculateDistribution((start+partStart,start+partEnd))
            for k,v in subdist.items():
                subwords.setdefault(k,0)
                subwords[k] += v

        if self.differentLengths:
            try:
                del subwords['']
            except KeyError:
                pass
        return subwords
    

    def calculatePart(self,(start,end)):
        L = end - start
        border = start + L/2
        dist1 = self.getSubwords((start,border))
        dist2 = self.getSubwords((border+L%2,end))
        common = set(dist1.keys()).intersection(dist2.keys())
        mulSum = sum(dist1[k]*dist2[k] for k in common)
        return Fraction(mulSum)


class IdenticalFieldIndexes(MyWindowSummer):
    def validateClassValues(self):
        MyWindowSummer.validateClassValues(self)
        """why to bother with an error message?"""
        if self.fieldMinSize == 1:
            self.fieldMinSize = 2
            
    def calculatePart(self,(start,end)):
        L = end - start
        border = start + L/2 + L%2
        try:
            value = sum([ sum([1 for i in range(L/2) if s[start + i] == s[border + i]]) for s in self.strings if len(s) >= end]) *Fraction(2,L)
        except Exception, e:
            print start, end, border, L
            raise e
        return value


class FieldPermutations(MyWindowSummer):
    """
    "111aaa"
    "111aba"
    So there is 2 strings which do not differ at index 0 ... 2
    >>> calc = FieldPermutations()
    >>> calc.differentLengths = False
    >>> calc.strings = ["111aaa","111aba"]
    >>> calc.calculate()
    (fieldMaxSize 6, fieldMinSize 1, maxlen 6)
    R 1 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 1), Fraction(1, 2)]
    R 2 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(3, 4), Fraction(1, 1), Fraction(1, 1)]
    R 3 [Fraction(1, 2), Fraction(1, 2), Fraction(2, 3), Fraction(5, 6), Fraction(1, 1), Fraction(1, 1)]
    R 4 [Fraction(1, 2), Fraction(3, 4), Fraction(5, 6), Fraction(5, 6), Fraction(1, 1), Fraction(1, 1)]
    R 5 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
    R 6 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
    <BLANKLINE>
    """
    def calculatePart(self,(start,end)):
        """
        This function returns the amount of different strings in one field from index 
        start to index end-1 divided by maximum possible amount of different string in that field
        Examples:
        Strings
        "111aaa"
        "111aba"
        So there is 2 strings which do not differ at index 0 ... 2
        >>> calc = FieldPermutations()
        >>> calc.differentLengths = False
        >>> calc.strings = ["111aaa","111aba"]
        >>> calc.calculatePart((0,6))
        Fraction(1, 1)
        >>> calc.calculatePart((5,6))
        Fraction(1, 2)
        >>> calc.calculatePart((0,3))
        Fraction(1, 2)
        """
        
        allParts = [tuple(s[start:end]) for s in self.strings]
        parts = len(set(allParts))
        emptyones = allParts.count(tuple([]))
        
        countOfdifferentSamples = len(allParts)
        if self.differentLengths:
            countOfdifferentSamples -= emptyones
        
        maxparts = min(countOfdifferentSamples, self.maxSymbols ** (end - start) )
        added = Fraction(parts, maxparts)

        return added


def entropy(n, N):
    """
        entropy = -sum p(x) * log (p(x)) 
            = -sum n(x) / N * log(n(x) / N) 
            = -sum n(x) / N *   (log(n(x)) - log(N))
            = -1/N *  sum n(x)* (log(n(x)) - log(N))
            = -1/N * (sum n(x)* log(n(x))  - (sum n(x) * log(N)) )
            = -1/N * (sum n(x)* log(n(x))  - N * log(N)) 
            = log(N) - 1/N * sum n(x) * log(n(x)) 

     so we need at least list of n(x)
     """
    return Fl(log(N,2)) - Fraction(1,N) * sum([nx * Fl(log(nx,2)) for nx in n.itervalues()])


class FieldEntropyRate(MyWindowSummer):
    def calculatePart(self,(start,end)):
        
        
        n, N = self.claculateDistribution((start,end)) 

        added = Fraction(0)
        if N != 0:
            added = entropy(n, N)
        
        """
        entropy rate = entropy / length
        so
        """
        rate = added / (end - start)

        return rate



#def yieldEvenParts(maxlen, field_max_size = None, minlen = 2):
#    for (start,end) in yieldParts(maxlen, field_max_size, minlen):
#        if (end - start)%2 != 0:
#            continue
#        yield (start,end)

class FieldJSD(FieldEntropyRate):
    def __init__(self):
        FieldEntropyRate.__init__(self)
        #form: {index:({x:nx},N)}
        self.distributiondict = {}
        
    def validateClassValues(self):
        FieldEntropyRate.validateClassValues(self)
        if self.fieldMinSize != None and (
            type(self.fieldMinSize) not in [type(1), type(1L)] 
            or self.fieldMinSize <= 1):
            
            raise ValueError('self.fieldMinSize')

    def calculateLocals(self):
        FieldEntropyRate.calculateLocals(self)
        if self.fieldMinSize == 1:
            self.fieldMinSize = 2
        
    def calculatePart(self,(start,end)):
        distributions = []
        
        for i in range(start,end):
            ni, Ni = self.distributiondict.setdefault(i, self.claculateDistribution((i, i+1)))
            if Ni != 0:
                distributions.append((ni,Ni))
                
        added = Fraction(0)
        if not distributions:
            return added
        
        rightpart = Fraction(1,len(distributions)) * sum(
            [entropy(ni, Ni) for ni, Ni in distributions]
            )
        
        
        randomvalues = set([])
        for ni, Ni in distributions:
            randomvalues.update(ni.keys())
        
        p = [ Fraction(1,len(distributions))*sum(
                [Fraction(ni.get(x,0),Ni) for ni, Ni in distributions])
               for x in randomvalues]
        
        leftpart = -sum([ px * Fl(log(px, 2)) for px in p])
        
        divergence = leftpart - rightpart
        added = divergence / (end - start)
        
        return added


class IndexJSD(FieldJSD):
    #def __init__(self):
    #    FieldEntropyRate.__init__(self)
    #    self.yieldParts = yieldEvenParts

    
    def addToResult(self,added,(start,end),result):
        l = end - start
        field = l 
        if l%2 == 1:
            result.addField(added, (start + l/2, start + l/2 + 1), field = field)
        else:
            result.addField(added, (start + l/2 -1, start + l/2 + 1 ), field = field)

    def calculatePart(self,(start,end)):
        L = end - start
        
        border = start + L/2
        
        n1, N1 = self.claculateDistribution((start, border)) 
        n2, N2 = self.claculateDistribution((border + L%2, end)) 

        added = Fraction(0)
        
        if N1 == 0 or N2 == 0:
            return added        
        
        entropy1 = entropy(n1, N1)
        entropy2 = entropy(n2, N2)
        
        """
        p_1 = n_1/N1, p2 = n2/N2, 
        p = (p1+p2)/2 = (n1/N1 + n2/N2)/2 = (n1*N2+n2*N1)/(2*N1*N2)  
        """
        N3 = N1 * N2 * 2

        keys = list(set(n1.keys() + n2.keys()))
        nx3 = [ n1.get(k,0)*N2 + n2.get(k,0)*N1 for k in keys]
        
        entropy3 = Fl(log(N3, 2)) - Fraction(1,N3) * Fl(sum([nx * log(nx, 2) for nx in nx3]))

        divergence = entropy3 - Fraction(1,2)*(entropy1 + entropy2)
        added = divergence / (end - border)
        
        return added



if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
