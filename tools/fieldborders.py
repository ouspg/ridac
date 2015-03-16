#!/usr/bin/env python2.6
import re
import array

import sys

from optparse import OptionParser

from indicators import *
from myresult import *

from codings import getcoding

import matplotlib.pyplot as plt

import matplotlib.cm as cm
import pylab


def getParser():
    parser = OptionParser()
    parser.add_option(
        "-R", 
        "--format-regexp", 
        dest="formatRe",
        help="""regular expression used (with DOTALL flag) to find and separate data entries from the given data file. default '([^\\n]*)'""", 
        default =  "([^\n]*)"
        )
            
    parser.add_option(
        "-c",
        "--input-coding",
        default='ascii',
        help = "how the input is encoded. default is plain raw data as unsigned char array. might crash. use with caution.")

    parser.add_option(
        "-D",
        "--input-decode",
        default=False,
        action='store_true',
        help = "The input string decoded instead of encoding (default) before futher processing. might crash. use with caution.")

    parser.add_option(
        "-N",
        "--number-of-read-samples",
        default=None,
        help = "after input decoding, how many samples is read. Default is all.")

    parser.add_option(
        "-O",
        "--offset-of-read-samples",
        default=0,
        help = "after input decoding, from which offset the samples are read. Default is 0.")    

    parser.add_option(
        "-b",
        "--as-bits",
        dest = "asbits",
        help = "examine data in bit level. sets symbol count to 2.",
        default = False,
        action = "store_true"
        )
    
    parser.add_option(
        "-f", 
        "--file", 
        dest="filename",
        help="write report of FILE", 
        metavar="FILE", 
        default = ""
        )

    parser.add_option(
        "-i", 
        "--indicator", 
        dest="indicator",
        help="""choose one of the calculated indicators:
p  = variations / max amount of variations
e  = entropy rate of the sliding window's strings
s  = Jensen-Shannon divergence per symbol for distributions of all fields indexes.
S  = Jensen-Shannon divergence per symbol for two fields surrounding the index.
w  = Amount of subwords in the sliding window.
ws = Frequencies of common substrings in adjacent windows multiplicated
ifi = Number of identical Indexes in adjacent windows
""",
        default = "p"
        )
    parser.add_option(
        "-M",
        "--maximum-size-of-a-field",
        dest = "fieldMaxSize",
        default = None,
        type = "int",
        help = "set the maximum size of a field. If not set, the maximum is the length of a inspected string"
        )
    parser.add_option(
        "-m",
        "--minimum-size-of-a-field",
        dest = "fieldMinSize",
        default = None,
        type = "int",
        help = "set the minimum size of a field.default is the smallest"
        )
    
    parser.add_option(
        "-S", 
        "--forced-subfield-length", 
        help="(for indicator choice ws) Force the length of fields in windows to this.", 
        default = None
        )
    
    
    parser.add_option(
        "-s",
        "--symbol-count",
        dest = "maxSymbols",
        default = 256,
        type = "int",
        help = "set the amount of symbols used. default is 256"
        )
    
    parser.add_option(
        "-l",
        "--length-matter",
        dest = "differentLengths",
        default = False,
        action = "store_true",
        help = "If enabled, only long enough strings are calculated."
        )

    parser.add_option(
        "-F",
        "--smoothing-filter",
        dest = "smoothingFilter",
        default = "mean",
        help = "How the index's value is computed from the same sized overlapping sliding windows. Default is %default, choises are max, min and mean"
        )

    parser.add_option(
        "-n",
        "--normalize",
        dest = "normalize",
        default = False,
        action = "store_true",
        help = "normalize result"
        )

    parser.add_option(
        "-d",
        "--delta",
        dest = "delta",
        default = False,
        action = "store_true",
        help = "save only the difference between the previous item in same line and self"
        )
    parser.add_option(
        "-E",
        "--excess",
        default = False,
        action = "store_true",
        help = "save only the difference between the previous row item and self"
        )
    parser.add_option(
        "-L",
        "--contour-lines",
        dest = "contourLines",
        default = False,
        action = "store_true",
        help = "Draws contour lines to the image"
        )
    parser.add_option(
        "-G",
        "--grayscale",
        default = False,
        action = "store_true",
        help = "Draws contour in grayscale"
        )

    

    #parser.add_option(
    #    "-r", 
    #    "--result", 
    #    dest="result",
    #    help="write report to FILE", 
    #    metavar="FILE", 
    #    default = "do not plot the contour image. save result to a file"
    #    )

    return parser

def getOptStringsDst():
    """
    I made the command line interface phase in such a mechanical fashion 
    that it should be easy to replace it with something more automatized one. 
    """

    parser = getParser()    
    (opt, _) = parser.parse_args()
    
    #TODO: make a dictionary of these or smth
    if opt.indicator not in ['p','e','s','S', 'es','w', 'ws', 'ifi']:
        print>>sys.stderr, "not valid option as property"
        sys.exit(1)

    if opt.smoothingFilter not in ['min','max','mean']:
        print>>sys.stderr, "not valid option as smoothingFilter"
        sys.exit(1)



    try:
        filestr = open(opt.filename, "rb").read()
        print 'read %s bytes'%len(filestr)
    except Exception, e:
        print>>sys.stderr, "opt.filename:"
        print>>sys.stderr, type(e), str(e)
        sys.exit(1)

    
    if opt.maxSymbols < 2 or opt.maxSymbols > 256:
        print>>sys.stderr, "opt.maxSymbols should be in 2 ... 256"
        sys.exit(1)

    
        
    try:
        strings = re.findall(opt.formatRe, filestr,flags=re.DOTALL )
        print 'found %s entries with %s'%(
            len(strings), 
            str((opt.formatRe,))[2:-3]
            )
        print 'some begins of the first entries:'
        print "\n".join(map( lambda s: s.encode('string escape'), [ i[:32] for i in  strings[:20]] ))
    except Exception, e:
        print>>sys.stderr, "formatRe:", type(e), e
        sys.exit(1)

    
    if opt.input_coding != None:
        ind = 1
        if opt.input_decode:
            ind = 2
        print opt.input_coding
        strings = map( lambda myS: getcoding(myS,opt.input_coding)[ind], strings)
	
        print 'some begins of the first entries:'
        print "\n".join(map( lambda s: "".join(s).encode('string escape'), [ i[:32] for i in  strings[:20]] ))
        
        if None in strings:
             print>>sys.stderr, "coding error"
             print strings
             sys.exit(1)

    if opt.asbits:
        strings = map(chrsToBitString,strings)
        opt.maxSymbols = 2

    try:
        opt.offset_of_read_samples = int(opt.offset_of_read_samples)
    except Exception, e:
        print>>sys.stderr, "offset_of_read_samples:", type(e), e
        sys.exit(1)
    try:
        if opt.number_of_read_samples != None:
            opt.number_of_read_samples = int(opt.number_of_read_samples)
    except Exception, e:
        print>>sys.stderr, "number_of_read_samples:", type(e), e
        sys.exit(1)

    for i in range(len(strings)):
        if opt.number_of_read_samples == None:
            strings[i] = strings[i][opt.offset_of_read_samples:]
            print 'recording %d read samples %d'%(i, len(strings[i]) )
        else:
            strings[i] = strings[i][opt.offset_of_read_samples:opt.offset_of_read_samples+opt.number_of_read_samples]
            print 'recording %d read samples %d'%(i, len(strings[i]) )

    print 'sorting empty ones out'
    strings = [ i for i in strings if len(i) != 0]
                                    
    print '# of recordings:',len(strings)
    
                                    
    """at this phase cmd line typechecks should be done"""
    return opt, strings #, dst



def tobits(x,digits=16):
    r = []    
    for i in range(digits):
        r.insert(0,x % 2)
        x >>= 1
    return r


def chrsToBitString(s):
    out = []
    for c in s:
        bits = tobits(ord(c), digits=8)
        bits = map(str,bits)
        out += bits
    return "".join(out)

    
if __name__ == "__main__":
    label = "" #label for plotting: TODO(?): move to classes?
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    print 'reading parameters'
    #opt, strings , dst = getOptStringsDst()
    opt, strings = getOptStringsDst()
    
    if opt.indicator == "p":
        calc = FieldPermutations()
        label += 'Variations / (max amount of variations) '
    if opt.indicator == "e":
        calc = FieldEntropyRate()
        label += 'Entropyrate '
    if opt.indicator == "s":
        calc = FieldJSD()
        label += 'column\'s entropy rate - expected column entropy rate for window'
    if opt.indicator == "S":
        calc = IndexJSD()
        label += 'Jenssen shanon divergense over two adjacent windows '
    if opt.indicator == "w":
        calc = FieldSubWords()
        label += 'Amount of subwords in the sliding window '

    if opt.indicator == "ws":
        calc = CommonFieldSubWords()
        label += 'Frequencies of common substrings in adjacent windows multiplicated '

    if opt.indicator == "ifi":
        calc = IdenticalFieldIndexes()
        label += 'Number of identical Indexes in adjacent windows divided by length'

    if opt.smoothingFilter == 'mean':
        calc.resultClass = MyResult
        
    if opt.smoothingFilter == 'max':
        calc.resultClass = MaxResult

    if opt.smoothingFilter == 'min':
        calc.resultClass = MinResult         
    
    if opt.indicator == "es":
        calc = FieldEntropyRate()
        calc2 = FieldJSD()
    
    def setCalcOpt(calc, opt):
        calc.differentLengths = opt.differentLengths
        calc.fieldMaxSize = opt.fieldMaxSize
        calc.fieldMinSize = opt.fieldMinSize
        calc.maxSymbols = opt.maxSymbols    
        calc.strings = strings
        
        if opt.forced_subfield_length != None:
             calc.fixedSubFieldSize = opt.forced_subfield_length
    
    setCalcOpt(calc, opt)
    if opt.indicator == "es":
        setCalcOpt(calc2, opt)

    
    print 'calculation starts'
    result = calc.calculate()



    if opt.indicator == "es":
        print 'calculation phase 2'
        result2 = calc2.calculate()
        def mul(a,b):
            return a*b
        def div(a,b):
            return b/(a+1)
        
        result.forEach(div,result2)
    if opt.excess:
        print 'calculating the difference between the lines'
        label += ' substacked by values of smaller window size'
        result.calculateExcess()

    if opt.delta:
        print 'calculating deltas'
        label += ' substacked by previous index\'s value'
        result.delta()
    
    if opt.normalize:
        print 'normalizing'
        label += ' normalized for each window size'
        result.normalize()

    Z = result.rowsAsFloat()

    
    
    print 'plotting'
    plt.figure()
    mycolormap = cm.gist_rainbow
    if opt.grayscale:
        mycolormap = cm.gist_gray

    if opt.contourLines:
        contour = plt.contour(Z)
    #im = plt.imshow(Z, interpolation='bilinear', origin='lower',cmap=mycolormap)
    pColor = plt.pcolor(pylab.array(Z), cmap= mycolormap)
    #plt.pcolor(Z,cmap =  mycolormap)
    #imCb = plt.colorbar(im, orientation='horizontal')
    if opt.contourLines:
        contourCb = plt.colorbar(contour, shrink = 0.8,cmap= mycolormap)
    pColorCb = plt.colorbar(pColor, shrink = 0.8,cmap= mycolormap)#, orientation='horizontal')
    #plt.cool()
    plt.yticks([0.5 +i for i in range(len(Z))],range(result.fieldMinSize,result.fieldMinSize + len(Z)))
    
    #The labels
    #plt.label(
    plt.xlabel("The index of files\' inspected elements")
    plt.ylabel("The size of the sliding window over the files\' elements")

    pColorCb.set_label('Mapping from the colors to the numbers')
    plt.title(label)
    plt.show()

    

    """
    if opt.delta:
        result = [0] + [result[i]-result[i-1] for i in range(1,len(result))]
        #result = [0] + [result[i]-result[i-1] for i in range(1,len(result))]
    
    
    mean = sum(result) / len(result)
    sampleStandardDeviation = (sum([(i-mean)**2 for i in result]) / (len(result) -1)) ** 0.5
    print "mean", float(mean)
    print "sampleStandardDeviation", sampleStandardDeviation 
    if opt.normalize:
        result = [(i-mean)/sampleStandardDeviation for i in result]
    resultArray = array.array('d', result)
    print "samples", len(resultArray)
    resultArray.tofile(dst)
    #print result
    dst.close()
    """
