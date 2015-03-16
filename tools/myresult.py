from math import log


from fractions import Fraction


class MyResult:
    def __init__(self,fieldMaxSize, fieldMinSize, maxlen):
        """
        How to create an empty result item for field sizes from 1 ... 4 for at most 6 symbol long items  
        >>> k = MyResult(4,1,6)
        >>> k
        (fieldMaxSize 4, fieldMinSize 1, maxlen 6)
        R 1 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 1 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        R 2 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 2 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        R 3 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 3 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        R 4 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 4 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        <BLANKLINE>
        """
        
        self.fieldMaxSize, self.fieldMinSize, self.maxlen = fieldMaxSize, fieldMinSize, maxlen
        self.result = self.makeDict(0)
        self.uses = self.makeDict(0)
        self.divided = False

    def __repr__(self):
        return str(self)

    def __str__(self):
        out = "(fieldMaxSize %d, fieldMinSize %d, maxlen %d)\n"%(self.fieldMaxSize, self.fieldMinSize, self.maxlen)
        for l in self.result:
            out += "R %d %s\n"%(l,self.result[l])
            if not self.divided:
                out += "U %d %s\n"%(l,self.uses[l])
        return out

    def rowsAsFloat(self):
        return [[float(self.result[l][i]) for i in range(self.maxlen)] for l in self.result]

    def makeDict(self, default):
        return dict(
            [(l, [Fraction(default)]*self.maxlen) 
             for l in range(self.fieldMinSize, self.fieldMaxSize+1)])

    def calculateExcess(self):
        newresult = {}
        for i in self.result:
            if i-1 not in self.result:
               newresult[i] = self.result[i]
            else:
                newresult[i] = [self.result[i][j] - self.result[i-1][j] for j in range(self.maxlen)]
        self.result = newresult

    def addField(self, added, (start, end), field = None):
        """
        >>> k = MyResult(4,1,6)
        >>> k.addField(Fraction(1,3),(0,2))       
        >>> k.addField(Fraction(1,3),(1,3))
        >>> k
        (fieldMaxSize 4, fieldMinSize 1, maxlen 6)
        R 1 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 1 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        R 2 [Fraction(1, 3), Fraction(2, 3), Fraction(1, 3), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 2 [Fraction(1, 1), Fraction(2, 1), Fraction(1, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        R 3 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 3 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        R 4 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 4 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        <BLANKLINE>
        >>> k = MyResult(5,1,5)
        >>> for i in range(5):
        ...  for j in range(i+1,6):
        ...   k.addField(1,(i,j))
        ... 
        >>> k
        (fieldMaxSize 5, fieldMinSize 1, maxlen 5)
        R 1 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
        U 1 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
        R 2 [Fraction(1, 1), Fraction(2, 1), Fraction(2, 1), Fraction(2, 1), Fraction(1, 1)]
        U 2 [Fraction(1, 1), Fraction(2, 1), Fraction(2, 1), Fraction(2, 1), Fraction(1, 1)]
        R 3 [Fraction(1, 1), Fraction(2, 1), Fraction(3, 1), Fraction(2, 1), Fraction(1, 1)]
        U 3 [Fraction(1, 1), Fraction(2, 1), Fraction(3, 1), Fraction(2, 1), Fraction(1, 1)]
        R 4 [Fraction(1, 1), Fraction(2, 1), Fraction(2, 1), Fraction(2, 1), Fraction(1, 1)]
        U 4 [Fraction(1, 1), Fraction(2, 1), Fraction(2, 1), Fraction(2, 1), Fraction(1, 1)]
        R 5 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
        U 5 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
        <BLANKLINE>
        >>> k = MyResult(5,1,5)
        >>> for i in range(5):
        ...  for j in range(i+1,6):
        ...   k.addField(Fraction(1,2),(i,j))
        ... 
        >>> k
        (fieldMaxSize 5, fieldMinSize 1, maxlen 5)
        R 1 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)]
        U 1 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
        R 2 [Fraction(1, 2), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 2)]
        U 2 [Fraction(1, 1), Fraction(2, 1), Fraction(2, 1), Fraction(2, 1), Fraction(1, 1)]
        R 3 [Fraction(1, 2), Fraction(1, 1), Fraction(3, 2), Fraction(1, 1), Fraction(1, 2)]
        U 3 [Fraction(1, 1), Fraction(2, 1), Fraction(3, 1), Fraction(2, 1), Fraction(1, 1)]
        R 4 [Fraction(1, 2), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 2)]
        U 4 [Fraction(1, 1), Fraction(2, 1), Fraction(2, 1), Fraction(2, 1), Fraction(1, 1)]
        R 5 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)]
        U 5 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
        <BLANKLINE>
        """
        if self.divided:
            raise AssertionError("divideUses called first!")
        if field == None:
            field = end - start
        result, uses =  self.result[field], self.uses[field]
        for i in range(start, end):
            result[i] += added
            uses[i] += 1

    
    def divideUses(self):
        """
        Calculates a mean value for each element according it's uses in different fileds
        >>> k = MyResult(5,1,5)
        >>> for i in range(5):
        ...  for j in range(i+1,6):
        ...   k.addField(Fraction(1,2),(i,j))
        ... 
        >>> k.divideUses()
        >>> k
        (fieldMaxSize 5, fieldMinSize 1, maxlen 5)
        R 1 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)]
        R 2 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)]
        R 3 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)]
        R 4 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)]
        R 5 [Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)]
        <BLANKLINE>
        """
        self.result =  dict([ 
                (l,[self.result[l][i] / self.uses[l][i] if self.result[l][i] != 0 else Fraction(0) for i in range(self.maxlen)]) 
                for l in self.result
                ])
        self.divided = True
        self.uses = None


    def delta(self):
        """
        calculates the difference of each item to it's previous one  
        >>> k = MyResult(5,1,4)
        >>> for i in range(3):
        ...  k.addField(1,(i,4))
        ... 
        >>> k.delta()
        >>> k
        (fieldMaxSize 5, fieldMinSize 1, maxlen 4)
        R 1 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 1 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        R 2 [Fraction(0, 1), Fraction(0, 1), Fraction(1, 1), Fraction(0, 1)]
        U 2 [Fraction(0, 1), Fraction(0, 1), Fraction(1, 1), Fraction(1, 1)]
        R 3 [Fraction(0, 1), Fraction(1, 1), Fraction(0, 1), Fraction(0, 1)]
        U 3 [Fraction(0, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
        R 4 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 4 [Fraction(1, 1), Fraction(1, 1), Fraction(1, 1), Fraction(1, 1)]
        R 5 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        U 5 [Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(0, 1)]
        <BLANKLINE>
        """
        self.result = dict([ 
                (l,[Fraction(0)] + [self.result[l][i]-self.result[l][i-1] for i in range(1,self.maxlen)]) 
                for l in self.result
                ])
    
    def normalize(self):
        """
        >>> k = MyResult(5,1,6)
        >>> for s in range(1,6):
        ...  for i in range(6):
        ...    k.result[s][i] += (s * i) % 7 
        >>> _ = k.normalize()
        >>> k.normalize()
        ({1: Fraction(0, 1), 2: Fraction(0, 1), 3: Fraction(0, 1), 4: Fraction(0, 1), 5: Fraction(0, 1)}, {1: Fraction(1, 1), 2: Fraction(1, 1), 3: Fraction(1, 1), 4: Fraction(1, 1), 5: Fraction(1, 1)})
        """
        means = dict([
                (l,sum(self.result[l]) / self.maxlen) for l in self.result])
                                                      
        sampleStandardDeviations = dict([
                (l, Fraction.from_float( (sum([(i-means[l])**2 for i in self.result[l]]) / (self.maxlen -1) ) ** 0.5) )
                for l in self.result])
        
        """ if there is no variation at all then division by 1 is not a big deal"""
        for fieldsize in sampleStandardDeviations:
            if sampleStandardDeviations[fieldsize] == 0:
                sampleStandardDeviations[fieldsize] = 1

        self.result = dict([
                (l,[(i-means[l])/sampleStandardDeviations[l] for i in self.result[l]])
                for l in self.result])        
        return means, sampleStandardDeviations
    

    def forEach(self,fcn,another):
        for i in self.result:
            if i not in another.result:
                continue
            for j in range(self.maxlen):
                self.result[i][j] =  fcn(self.result[i][j],another.result[i][j])



class MaxResult(MyResult):
    def __init__(self,fieldMaxSize, fieldMinSize, maxlen):
        self.fieldMaxSize, self.fieldMinSize, self.maxlen = fieldMaxSize, fieldMinSize, maxlen
        self.result = self.makeDict(0)
        self.divided = False

    def divideUses(self):
        self.divided = True


    def addField(self, added, (start, end), field = None):
        if self.divided:
            raise AssertionError("divideUses called first!")
        if field == None:
            field = end - start
        result =  self.result[field]
        for i in range(start, end):
            result[i] = max(added, result[i])
        
class MinResult(MaxResult):
    def addField(self, added, (start, end), field = None):
        if self.divided:
            raise AssertionError("divideUses called first!")
        if field == None:
            field = end - start
        result =  self.result[field]
        for i in range(start, end):
            result[i] = min(added, result[i])
    

if __name__ == "__main__":
    import doctest
    doctest.testmod()



