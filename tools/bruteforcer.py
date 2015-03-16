#!/usr/bin/env python2.6

import time
import os
import random


import formats




#For future perhaps
#class multiplicationPresentation():
#    def __init__(self, bases, baseOrder = None):
#        self.bases = bases
#        self.numberList = [0] * len(self.bases)
#        if baseOrder == None:
#            """numbers are in LSB order at the list (lowest first)"""
#            self.baseOrder = [i for i in range(len(bases))]
#    
#    def __add__(self, added = 1):
#        """return value != 0 in case of overflow"""
#        for i in range(len(self.numberList)):
#            self.numberList[i] += int(added)
#            if self.numberList[i] >= self.bases[i]**i:
#                added = self.numberList[i] / self.bases[i]
#                self.numberList[i] = self.numberList[i] % self.bases[i]
#                continue
#            break
#        return added
#
#    def __int__(self):
#        n = 1
#        base = 1
#        for i in self.baseOrder:
#            n += self.numberList[i] * base
#            base *= self.bases[i]
#        return n




def binSearch(n,base = 2):
    """exactly the same could be done by just reversing the bits"""
    if base != 2:
        n = myLogForBigIntegers(2**n,base)
    
    m = base**n
    i = m / base

    yield 0

    while i >= 1:
        moduloCnt = 0
        
        index = 0
        while index < m:
            
            index += i
            if moduloCnt % base == 0:
                yield index
            moduloCnt += 1
        i /= base



def primes(primes = None):
    if primes == None or len(primes) == 0:
        primes = [2]        
    number = primes[-1]+1
    while True:#len(alkuluvut) < n:
        prime = True
        sqNumber = number ** 0.5
        for i in primes:
            if number % i == 0:
                prime = False
                break
            if  sqNumber < i:
                break
        if prime:
            primes.append(number)
            yield prime, primes
        number = number + 1

#def getNextPrime(n):
#    i = n + 1
#    while True:
#        prime = True
#        for j in range(int(n**0.5)+1):
#            if i % j == 0:
#                i += 1
#                prime = False
#                break
#        if prime:
#            return i


#def gcd(a, b):
#    if a == 0:
#        return b
#    while b != 0:
#        if a > b:
#            a = a - b
#        else:
#           b = b - a
#    return a

LCGprimes = []
def getLCG(seed=None, n=2**32, maxprimes = 50):

    
    
    """n = the size of keyspace"""
    if n < 5:
        raise ValueError('too small n for this')


    if seed != None:
        random.seed(seed)
    else:
        random.seed()

    """No need to recalculate the primes allways. TODO: do this better."""
    global LCGprimes
    if len(LCGprimes) < maxprimes or LCGprimes[-1]**2 < n:
        for p,pt in primes(LCGprimes):
            if p**2 > n:
                break
            if len(pt) >= maxprimes:
                break
        LCGprimes = pt
    else:
        pt = LCGprimes


    while True:
        """find a suitable number m, such that m > n. the prime factors are for a"""
        m = 1
        mp = [1]
        while m < n:
            p = pt[random.randrange(len(pt))]
            m*=p
            mp.append(p)


        """a - 1 is divisible by all prime factors of m"""

        mp.sort()
        a = 1
        ap = [1]
        #ap = set(mp)
        for i in mp:
            if i != ap[-1] or random.randrange(2) == 1:
                ap.append(i)
                a *= i

        """a - 1 is a multiple of 4 if m is a multiple of 4"""
        if m % 4 == 0:
            a *= 2
        a += 1



        if a < m:
            break

    """ c and m should be relatively primes"""
    c = 1

    """this cp  SHOULD allways be != [].. ! if the used list of primes is BIG enough"""
    cp = list(set(pt) - set(ap) )
    while c < m**0.5 and len(cp) > 1:
        c *= cp[random.randrange(len(cp))]

    return {'n':n,'a':a,'m':m,'c':c}

def LCG(n = 2**32,a = 1103515245, m = 2**32, c = 12345, offset = 0):
    i = offset%m + 1
    start = i
    while True:
        if i < n:
            yield i
        i = ( a*i + c) % m
        if i == start:
            break



#this approach needs a rewrite of the bruteforcer yielders
def myLogForBigIntegers(m, base):
    """Use python's big integers which math.log does not use."""
    power = base
    n = 1
    while power < m:
        n += 1
        power *= base
    return n

def permutations(k, end=1):
    if k in [1,end,0]:
        return 1
    else:
        return k*permutations(k - 1, end)

def combinations(n,b):
    maxdivterm = max(n-b,b)
    mindivterm = min(n-b,b)
    return permutations(n,maxdivterm) / permutations(mindivterm)        


def combination(aSet, combNmbr, n, k, allcombs):
    """enumerates combinations of a given list"""
    
    if k == 0:
        return []
    a = k * allcombs / n
    if combNmbr <= a:
        return [aSet[0]] + combination(aSet[1:], combNmbr, n-1, k-1, a)

    return combination(aSet[1:], combNmbr - a, n - 1, k, allcombs - a)




def yieldInOrder(offset=0,bits = 32, base = 2):
    for i in range(2**(bits)+1):
        yield (offset + i) % (2**bits+1)

def yieldInOrderXOR(offset=0,bits = 32, base =2):
    for i in range( 2**(bits)+1):
        yield (offset ^ i) % (2**bits)

def yieldGrid(offset=0, bits = 32, base=2):
    for i in  binSearch(bits, base=base):              
        yield (offset + i) % (2**bits)


def generatedLCG(offset = 0, bits = None, n = None, base =None):
    if bits != None:
        n = 2**bits
    if n > 10: #TODO: fix this
        params = getLCG(seed = None, n = n)
        if bits != None:
            print 'used LCG params', params
        for i in  LCG(offset= offset, **params):              
            yield i
    else:
        k = list(range(n))
        random.shuffle(k)
        for i in k:
            yield i
    

def raisingHammingDistance(offset, bits = 32, base = None):
    def binaryLoop(loops, bits):
        if loops == 0:
            yield 0
        else:
            for p in range(loops-1,bits):
                for p2 in binaryLoop(loops-1, p):
                    yield 2**p + p2
                
    for i in range(bits+1):
        for p in binaryLoop(i, bits):
            yield (offset^p)%(2**bits)



def mixedRaisingHammingDist(offset = 0, bits = 32, base = None):
    n = 2**bits
    indexList = list(range(bits))
    for nOnes in range(bits+1):
        print 'mutated:',nOnes
        combs =  combinations(bits,nOnes)
        for comb in generatedLCG(n = combs):            

            ones = combination(indexList, comb+1, bits, nOnes,combs)
            

            yield (offset^sum(map(lambda p:1<<p,ones)))%n
            
        

bruteforceTypes = {
    'straight':yieldInOrder ,
    'binary-grid': yieldGrid,
    'straight-xor':yieldInOrderXOR,
    'generated-LCG':generatedLCG,
    'raising-hamming-distance':raisingHammingDistance,
    'mixed-raising-hamming-dist':mixedRaisingHammingDist
    }



def addBruteforceOptions(parser):
    parser.add_option(
        "-n",
        "--first-sent-number",
        default="0",
        help="the sent ID. The default is 0")

    parser.add_option(
        "-b",
        "--number-of-bruteforced-bits",
        default="0",
        help="the number bruteforced bits. Default 0 (=just send the first number)")

    parser.add_option(
        "-B",
        "--grid-base",
        default="2",
        help="The base of grid, if the grid BF is used.default =2")

    parser.add_option(
        "-t",
        "--bruteforce-type",
        default="straight",
        help="choose the bruteforce style (default straight): %s"%bruteforceTypes.keys())


def parseOptions(options):
    options.first_sent_number = int(options.first_sent_number)
    options.number_of_bruteforced_bits = int(options.number_of_bruteforced_bits)
    options.grid_base = int(options.grid_base)
    if options.bruteforce_type not in bruteforceTypes:
        raise ValueError('invalid bruteforce type')


def main():
    from optparse import OptionParser
    import sys
    parser = OptionParser()
    formats.addEncodingOptions(parser)
    addBruteforceOptions(parser)
    

    parser.add_option(
        "-r",
        "--repeat-of-one-key",
        default="5",
        help="The number of repets per key. default is 5.")

    parser.add_option(
        "-f",
        "--destination-file",
        default="",
        help="The destination file.")

    parser.add_option(
        "-v",
        "--verbose-interval",
        default="64",
        help="print every 'verbose-interval':th tested key to stdout. default 64")
    parser.add_option(
        "-V",
        "--output-to-stdout",
        default=False,
        action= 'store_true',
        help="print data to sys.stdout")
    
    
    (options, args) = parser.parse_args()
    
    try:
        formats.parseOptions(options)
        parseOptions(options)
        
        options.repeat_of_one_key = int(options.repeat_of_one_key)
        if options.output_to_stdout:
            options.destination_file = sys.stdout
        else:
            options.destination_file = open(options.destination_file, 'wb')
        options.verbose_interval = int(options.verbose_interval)
        
    except Exception, e:
        print 'invalid parameters', e, type(e)
        sys.exit(1)


    """Make a pipe for the format"""    
    processFormats, formatFncs =  formats.getFormatPipe()
    formats.setRfidFormatPipe(options,  formatFncs)
    
    bruteforce = bruteforceTypes[options.bruteforce_type](
        offset = options.first_sent_number,
        bits = options.number_of_bruteforced_bits,
        base = options.grid_base
        )

    print 'options:', options
    cnt = 0
    
    
    for number in bruteforce:
        key =  processFormats(number)
        if cnt % options.verbose_interval == 0:
            print 'number', number
            print 'formated data', key

        for repeat in range(options.repeat_of_one_key):
            options.destination_file.write(key)
        cnt += 1
    
    
if __name__ == "__main__":
    main()
