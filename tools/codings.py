#!/usr/bin/env python2.6
import sys
from optparse import OptionParser

import array
import csv

import codecs
try:
    import hashlib
except:
    print 'hashlib not imported'
    
import zlib

import dataformat

from myIterators import yieldSliceIndexes

import base64

def returnCodings(data,codecName):
    encoding = None
    decoding = None
    try:
        encoding = codecs.lookup(codecName).encode(data)[0]
    except:
        pass
    try:
        decoding = codecs.lookup(codecName).decode(data)[0]
    except:
        pass     
    return (codecName, encoding, decoding)

def codecEncodingsAndDecodings(data, reader):
    for acodec in reader:
        codecName = acodec['Codec']
        yield returnCodings(data,codecName)


hashlibalgs = {
        'md5':hashlib.md5,
        'sha1':hashlib.sha1,
        'sha224':hashlib.sha224,
        'sha256':hashlib.sha256,
        'sha384':hashlib.sha384,
        'sha512':hashlib.sha512}

def hashlibEncodings(data,codecName=None):
    
    if codecName == None:
        for name, hash in hashlibalgs.items():
            m = hash()
            m.update(data)
            yield (name, m.digest(), None) 
    else:
        m = hashlibalgs[codecName]()
        m.update(data)
        yield (codecName, m.digest(), None) 



zlibalgs = {}


zlibalgs['alder32'] = lambda data: zlib.adler32(data)


for compressRate in range(1,10):
    zlibalgs['zlib-compress-%d'%compressRate] = lambda data: zlib.compress(
        data, 
        compressRate)

zlibalgs['crc32'] = lambda data: zlib.crc32(data)
zlibalgs['zlib-decompress'] = lambda data:zlib.decompress(data)



def zlibEncodings(data, codecName = None):
    if codecName == None:
        for name in zlibalgs:
            try:
                encoded = None
                encoded = zlibalgs[name](data)
            except:
                pass
            
            yield (name,encoded,None)
    else:
        try:
            encoded = None
            encoded = zlibalgs[codecName](data)
        except:
            pass
        yield (codecName,encoded,None)

def yieldDataPairEncodings(data):
    yielders = [hashlibEncodings, zlibEncodings ]
    for yielder in yielders:
        try:
            for n,e,d in yielder(data):
                for dn, de in intsToStr(n, e):
                    yield dn,de,None
        except:
            print 'fail', yielder





def unsignedIntAsChrs(data):
    try:
        returlt = None
        data = int(data)
        k = array.array('B')
        while data >0:
            #print data
            k.insert(0,data%256)
            data = data >> 8
        returlt = k.tostring()
    except:
        pass
    return returlt

def asUnsignedInteger(data):
    try:
        l = map(ord,data)
        l = [256**(len(l)-1-i)*v for i,v in enumerate(l)]
        l = sum(l)
    except:
        l = None
    return l

def asSignedInteger(data):
    if ord(data[0]) & 128 != 0:
        sign = -1
    else:
        sign = 1
    
    data = chr(ord(data[0]) &127) + data[1:]
    return sign*asUnsignedInteger(data)

def signedIntegerAsChrs(data):
    try:
        value = int(data)
        unsignedChrs = unsignedIntAsChrs(abs(value))
        if value < 0:
            if ord(unsignedChrs[0]) > 128:
                return chr(128)+unsignedChrs
            else:
                return chr(ord(unsignedChrs[0]) | 128)+ unsignedChrs[1:]
        else:
            if ord(unsignedChrs[0]) > 128:
                return chr(0) + unsignedChrs
            else:
                return unsignedChrs
    except:
        return None

def ones(data):
    ones = 0
    for i in data:
        n = ord(i)
        for j in range(8):
            if n & 2**j > 0:
                ones += 1
    return ones

def parity(data):
    return ones(data)%2

def floathex(data):
    try:
        return float(data).hex()
    except:
        return None
def hexfloat(data):
    try:
        return float(data)
    except:
        return None


def tobits(x,digits=16):
    r = []    
    for i in range(digits):
        r.insert(0,x % 2)
        x >>= 1
    return r

concat = lambda l: [j for i in l for j in i]
toStr = lambda i: "".join(map(str,i))
toChrs = lambda i: "".join(map(chr,i))

def toNibles(data):
    ints = map(ord,data)
    ints = concat(map(lambda d: (d>>4,d&127),ints))
    return ints

def fromNibles(data):
    data = map(int,data.strip('[]()').split(','))
    out = [0]*(len(data)/2)
    for i,v in enumerate(data):
        if i%2 ==0:
            out[i/2] += v <<4
        else:
            out[i/2] += v
    
    return toChrs(out)


def listeverse(data):
    try:
        data = data.strip('[]()').split(',')
        data.reverse()
        return data
    except:
        return None

def listswap2(data):
    try:
        data = data.strip('[]()').split(',')
        data = concat([(data[2*i+1],data[2*i]) for i in range(len(data)/2)])
        return data
    except:
        return None


miscEncodings = ['length','longUInt','longInt','onesInBinary','parity','floatHex','floatBin','asciiBinary','nibles','list_reverse','list_swap2']


def yieldMiscEncodings(data,codingName = None):
    if codingName in [None,'length']:
        yield 'length',len(data), None
    if codingName in [None,'longUInt']:
        yield ('longUInt',unsignedIntAsChrs(data), asUnsignedInteger(data))
    if codingName in [None,'longInt']:
        yield ('longInt',signedIntegerAsChrs(data), asSignedInteger(data))
    if codingName in [None,'onesInBinary']:
        yield ('onesInBinary',ones(data), None)
    if codingName in [None,'parity']:
        yield ('parity',parity(data), None)
    if codingName in [None,'floatHex']:
        yield ('floatHex',floathex(data), hexfloat(data))
    if codingName in [None,'list_reverse']:
        yield ('list_reverse',listeverse(data), None)
    if codingName in [None,'list_reverse']:
        yield ('list_swap2',listswap2(data), None)

    if  codingName in [None,'asciiBinary']:
        try:
            d = int(data,2)
            d = unsignedIntAsChrs(d)
        except:
            d = None
        yield ('asciiBinary',"".join(map(str, concat(map(lambda d: tobits(d,8),map(ord,data))) )),d)
    if  codingName in [None,'nibles']:
        try:
            e = toNibles(data)
        except:
            e = None
        try:
            d = fromNibles(data)
        except:
            d = None
        yield ('nibles',e,d)
    

arrayCodecs = {
    'local_character1':'c',
    'local_signed_integer1':'b',         
    'local_unsigned_integer1':'B',
    'local_Unicod_ character2':'u',
    'local_signed_integer2 ':'h',
    'local_unsigned_integer2':'H',
    'local_signed_integer2':'i', 
    'local_unsigned_integer2': 'I',
    'local_signed_integer4': 'l',
    'local_unsigned_integer4': 'L',
    'local_floating_point4': 'f',
    'local_floating_point8':  'd'
}


def yieldArray(data, codecName= None):
    for i in arrayCodecs:
        if codecName != None and codecName != i:
            continue
        try:
            k = array.array(arrayCodecs[i])
            k.fromstring(data)
            k = list(k)
        except:
            k = None
        try:
            l = array.array(arrayCodecs[i])
            f = int
            if i.find('float') != -1:
                f = float
            ints = map(f, data.strip('[(])').split(','))
            for n in ints:
                l.insert(0,n)
            l = l.tostring()
        except:
            l = None
        yield (i,k,l)
    

def intsToStr(name,i):
    if type(i) != type(1):
        yield name, i
    else:    
        #TODO: MORE int endodings
        yield name+ ' as str',str(i)
    
        yield name+ ' as chrs',unsignedIntAsChrs(i)



integers = {}
for i in range(2,37):
   integers['base%dint'%i] = i 


def yieldIntegerBase(data,coding = None):
    numbers = "0123456789"+"".join([chr(i) for i in range(ord('a'),ord('z')+1)])
    for i in integers:
        #print i
        if coding != None and coding != i:
            continue
        base = integers[i]
        try:
            n = int(data,integers[i])
        except:
            n = None
        try:
            d2 = int(data)

            base = integers[i]

            n2 = ""
            d = abs(d2)
            while d > 0:
                n2 = numbers[d%base] + n2
                d /= base
            if d2 < 0:
                n2 = '-'+n2
        except:
            n2 = None
            
        yield (i,n,n2)


base64Enc = {
    'base16':(lambda s: base64.b16encode(s),lambda s: base64.b16decode(s)),
    'base32':(lambda s: base64.b32encode(s),lambda s: base64.b32decode(s)),
    'base64':(lambda s: base64.b64encode(s),lambda s: base64.b64decode(s)),
    'standard_base64':(lambda s: base64.standard_b64encode(s),lambda s: base64.standard_b64decode(s)),
    'urlsafe_base64':(lambda s: base64.urlsafe_b64encode(s),lambda s: base64.urlsafe_b64decode(s))
}

def yieldBase64(data,encodingName = None, lookup = base64Enc):
    for i in lookup:
        if encodingName in [None,i]:
            try:
                e = lookup[i][0](data)
            except:
                e = None
            try:
                d = lookup[i][1](data)
            except:
                d = None
            yield (i,e,d)
            if i == encodingName:
                break

#TODO here
"""
toChrs = lambda i: "".join(map(chr,i))

def reverse4Bit(data):
    ints = map(ord,data)
    ints = map(lambda d: (d>>4,d&127),ints)
    out = []
    for i,j in ints:
        i = tobits(i,4)
        j = tobits(j,4)
        i.reverse()
        j.reverse()
        out.append( int(toStr(i),2) | int(toStr(j),2))
    return toChrs(out)
        
endians = {
'reverse_4bit': lambda d: reverse4Bit(d),
'reverse_8bit':
'reverse_2nible':
'reverse_2byte':
'reverse_4byte':
}
"""
   


def yieldAllEncodingsAndDecodings(data,f= codecEncodingsAndDecodings):
    yield ('None',s,s)
    yield ('longUInt',unsignedIntAsChrs(s), asUnsignedInteger(s))
    reader = csv.DictReader(open('codecs.csv','rb'))
    for i in f(data,reader):
        yield i
    reader = csv.DictReader(open('codecs_extra.csv','rb'))
    for i in f(data,reader):
        yield i
    
    for i in yieldDataPairEncodings(data):
        yield i

    for i in  yieldArray(data):
        yield i
    for i in yieldIntegerBase(data):
        yield i

    for i in  yieldMiscEncodings(data):
        yield i
    for i in yieldBase64(data):
        yield i



def getcoding(s,coding):
    if coding == 'None':
        return ('None',s,s)
    if coding in base64Enc:
        return  yieldBase64(s,coding).next()
    if coding in miscEncodings:
        return yieldMiscEncodings(s,coding).next()
    elif coding in arrayCodecs:
        return yieldArray(s,coding).next()
    elif coding in hashlibalgs:
        return hashlibEncodings(s, coding).next()
    elif coding in zlibalgs:
        return zlibEncodings(s, coding).next()
    else:
        return returnCodings(s,coding)
         
    #print coding

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option(
        "-s",
        "--input-string",
        default=None,
        help = "the encoded an decoded string")
    parser.add_option(
        "-f",
        "--input-file",
        default=None,
        help = "the encoded an decoded string")
    
    parser.add_option(
        "-c",
        "--coding-name",
        default=None,
        help = "the used encoding name. if None, tries all")

    parser.add_option(
        "-i",
        "--input-coding",
        default=None,
        help = "how the input is encoded. default is None")

    parser.add_option(
        "-D",
        "--input-decode",
        default=False,
        action='store_true',
        help = "The input string decoded instead of encoding (default) before futher processing")
    parser.add_option(
        "-O",
        "--output-field",
        default=None,
        help = "The printed output field(0=name,1=encode,2=decode). default is all.")
    
    (options, _) = parser.parse_args()
    
    s = "1337"
    if options.input_string != None:
        s = options.input_string
    elif options.input_file != None:
        #print options.input_file
        s = open(options.input_file).read()
    
    if options.input_coding != None:
        s = getcoding(s,options.input_coding)
        if options.input_decode:
            s = s[2]
        else:
            s = s[1]
    s = str(s)
    #print 'data via string_escape:',s
    if options.coding_name == None:
        for i in yieldAllEncodingsAndDecodings(s):
            if options.output_field == None:
                print i
            else:
                print i[int(options.output_field)]

    else:
        if options.output_field == None:
            print getcoding(s,options.coding_name)
        else:
            print getcoding(s,options.coding_name)[int(options.output_field)]
