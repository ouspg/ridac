import time
import os

toInts = lambda l: [int(i) for i in l]
takeOne = lambda l,n: [i[n] for i in l]

heads = lambda l: [l[i:] for i in range(len(l))]
tails = lambda l: [l[:i+1] for i in range(len(l))]

concat = lambda l: [j for i in l for j in i] 
toStr = lambda i: "".join(map(str,i))

"""the IEEE 802.5"""
standardManchester = lambda b:[ [0,1],[1,0]][b] 
startSeq = [0,0,0,1,1,1]

manchester = lambda bits: startSeq + concat( [
    standardManchester(i) for i in bits
    ])

evenBit = lambda bits: sum(bits )%2
oddBit = lambda bits:  ( evenBit(bits) +1 )%2
wiegandParities = lambda bits: concat([
        [evenBit(bits[:12])],
        bits[:12],
        bits[12:],
        [oddBit(bits[12:])]
        ])

manchesterDecode = lambda k : [ v for i,v in enumerate(k[6:]) if i%2 == 0]


def printDataValues (s, printVals = True):
    d = {}
    d['allBits'] = s
    d['frameStart'] = s[:19]
    d['wiegandData'] = s[19:]
    d['firstBlock'] = s[19:32]
    d['secondBlock'] = s[33:45]
    d['evenBit'] = s[19]
    d['oddBit'] = s[44]
    d['facilityCode'] = s[20:28]
    d['firstPartOfCardnumber'] = s[28:32]
    d['secondPartOfCardNumber'] = s[33:44]
    
    d['facilityCodeAsInteger'] = toInteger(toInts(d['facilityCode']))
    d['firstPartNmbrAsInteger'] = toInteger(toInts(d['firstPartOfCardnumber']))
    d['secondPartNmbAsInteger'] = toInteger(toInts(d['secondPartOfCardNumber']))
    d['cardNumberAsInteger'] = toInteger(toInts(s[28:44]))
    d['wiegandDataAsInteger'] = toInteger(toInts(s[20:44]))
    

    print """
 * Read manchester decoded bit sequence: 
   %(allBits)s
 * protocol information, wiegand data:
   %(frameStart)s, %(wiegandData)s
 * first wiegand block, second wiegand block:
   %(firstBlock)s, %(secondBlock)s
 * evenBit, facility code, 1. part of the card number, 2. part of the card number, odd bit:
   %(evenBit)s, %(facilityCode)s, %(firstPartOfCardnumber)s, %(secondPartOfCardNumber)s, %(oddBit)s
 * integer conversions:
   * facility number, 1. part of the card number, 2. part of the card number, 
     %(facilityCodeAsInteger)s,%(firstPartNmbrAsInteger)s,%(secondPartNmbAsInteger)s,
   * combined card number as integer:
     %(cardNumberAsInteger)s
   * whole wiegand data block as an integer:
     %(wiegandDataAsInteger)s
"""%d
    
    
    
    
standardFrameStart = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]

dataFrame = lambda data: standardFrameStart + wiegandParities(data)

def tobits(x,digits=16):
    r = []    
    for i in range(digits):
        r.insert(0,x % 2)
        x >>= 1
    return r

toInteger = lambda k: sum([v*2**(len(k)-1-i) for i,v in enumerate(k)])


def makeKeyFromInteger(i):
    return manchester(dataFrame(tobits(i,digits=24)))

def yieldAllKeysInOrder(start=0, stop=2**24):
    for i in range(start, stop):
        yield makeKeyFromInteger(i)

toBCD = lambda n: [ toStr(tobits(int(d),4)) for d in str(n) ]

def binSearch(n):
    m = 2**n
    i = m / 2

    yield 0
    yield m-1

    while i >= 1:
        moduloCnt = 0
        
        index = 0
        while index < m:
            
            index += i
            if moduloCnt % 2 == 0:
                yield index
            moduloCnt += 1

        i /= 2

def yieldAllKeysInBinarySearchFashion():
    for i in binSearch(24):
        yield makeKeyFromInteger(i)

def writeKeyBlockToFile(generator,
                        fname= "keytest.txt",
                        start = 0,
                        stop = 2**24,
                        repeats = 1
                        ):
    t1 = time.time()
    tmpfilename = os.tempnam(".")
    f = open(tmpfilename, "w")
    cnt = 0
    for bitString in generator:
        for r in range(repeats):
            f.write(toStr(bitString))
        f.flush()
        if cnt > stop - start - 1:
            print cnt,bitString
            break
        cnt += 1
    f.close()
    t2 = time.time()
    
    print 'generation time:', t2 - t1
    #print open(tmpfilename).read()
    while os.path.exists(fname):
        """this 0.041 is the time that it takes to send a one key seqv"""
        pollingTime = 2 #repeats * 0.041 * ( stop - start ) / 2.0
        print pollingTime
        time.sleep(pollingTime)
        
    
    os.rename(tmpfilename, fname)

    
    
    
    
    

        
