#!/usr/bin/env python2.6
from optparse import OptionParser
from formats import tobits
from indicators import yieldParts
import sys


def chrsToBitString(s):
    out = []
    for c in s:
        bits = tobits(ord(c), digits=8)
        bits = map(str,bits)
        out += bits
    return "".join(out)


def getParser():
    parser = OptionParser()
    parser.add_option(
        "-b",
        "--as-bits",
        dest = "asbits",
        help = "examine data in bit level. sets symbol count to 2.",
        default = False,
        action = "store_true"
        )
    parser.add_option(
        "-N",
        "--number-of-read-samples",
        default=None,
        help = "after input decoding, how many samples is read. Default is all.")
    parser.add_option(
        "-M",
        "--maximum-size-of-a-field",
        default = None,
        type = "int",
        help = "set the maximum size of a field. If not set, the maximum is the length of a inspected string"
        )
    parser.add_option(
        "-m",
        "--minimum-size-of-a-field",
        default = None,
        type = "int",
        help = "set the minimum size of a field.default is the smallest"
        )
    
    parser.add_option(
        "-O",
        "--offset-of-read-samples",
        default=0,
        help = "after input decoding, from which offset the samples are read. Default is 0.")    

    parser.add_option(
        "-P",
        "--number-of-printed-substrings",
        type = "int",
        default=100,
        help = "default is %default")    

    parser.add_option(
        "-f", 
        "--file", 
        dest="filename",
        help="analyzed file", 
        metavar="FILE", 
        default = ""
        )

    parser.add_option(
        "-s", 
        "--string", 
        help="analyzed string", 
        default = None
        )
    
    return parser


def getStr():
    parser = getParser()    
    (opt, _) = parser.parse_args()
    
    if opt.string != None:
        filestr = opt.string
    else:
        try:
            filestr = open(opt.filename, "rb").read()
        except Exception, e:
            print>>sys.stderr, "opt.filename:"
            print>>sys.stderr, type(e), str(e)
            sys.exit(1)
    print 'read %s bytes'%len(filestr)

    if opt.asbits:
        filestr = chrsToBitString(filestr)

    if opt.number_of_read_samples == None:
        filestr = filestr[opt.offset_of_read_samples:]
        print 'read samples %d'%(len(filestr) )
    else:
        filestr = filestr[
            opt.offset_of_read_samples:opt.offset_of_read_samples+opt.number_of_read_samples]
        print 'read samples %d'%(len(filestr) )



    return opt, filestr


if __name__ =="__main__":
    opt, filestr = getStr()
    #TODO: use efficien suffixtree or smth
    print 'counting...'
    print 'length, count, string'
    subDict = {}
    for i,j in yieldParts(
        len(filestr),
        opt.maximum_size_of_a_field,
        opt.minimum_size_of_a_field, 
        ):
        
        sub = filestr[i:j]
        subDict.setdefault(sub,0)
        subDict[sub] += 1
    
    items = [(v,len(i),i) for i,v in subDict.items()]
    items.sort()
    for c,l,i in items[-opt.number_of_printed_substrings:]:
        print l,c,i
