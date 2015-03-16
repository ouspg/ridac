#!/usr/bin/env python2.6

import sys
import os
import numpy
import array
import pylab
from optparse import OptionParser


#have complex in the name, if returns a complex array
fileTypes = ['float-complex-signal','float-signal','ascii-binary','uchar-binary' ,'raw-data']
typeSizes = {'float-complex-signal':2*4,'float-signal':4,'ascii-binary':1,'uchar-binary':1,'raw-data':None}

def samples_in_file_and_seek(afile,ftype, offset):
    try:
       set = os.SEEK_SET 
       end = os.SEEK_END
    except:
        end = 2
        set = 0
    
    afile.seek(0,set)
    fbegin = afile.tell()
    afile.seek(0,end)
    fend = afile.tell()
    

    fsize = fend - fbegin
    
    if ftype == 'raw-data':
        afile.seek(offset / 8 ,set)
        return (fsize * 8, 0)
    else:
        seekedBytes = offset * typeSizes[ftype]
        print seekedBytes, set, type( seekedBytes), type(set)
        afile.seek(seekedBytes, set)
        return (fsize / typeSizes[ftype], fsize % typeSizes[ftype])



def float_complex_signal_array(signalfile,offset,count):
    aArray = numpy.fromfile(signalfile,numpy.dtype('c8'),count)
    return aArray
    

def float_signal_array(signalfile,offset,count):
    aArray = numpy.fromfile(signalfile,numpy.dtype('f4'),count)
    return numpy.array(aArray,dtype=float)
    
    
def toAutocorrelationBinarySignal(aArray):
    """convert 0101010 --> -1 1 -1 1 -1 ..."""
    aArray = aArray * 2
    aArray = aArray - numpy.repeat(1, len(aArray))
    return aArray

def ascii_binary_array(signalfile,offset,count):
    aArray = numpy.fromfile(signalfile,numpy.dtype('u1'),count)
    
    if aArray[-1] == ord('\n'):
        aArray = aArray[:-1]
        
    aArray = aArray - numpy.repeat(ord('0'), len(aArray))
    
    if not( numpy.min(aArray) in [0,1] and  numpy.max(aArray) in  [0,1]):
        print>>sys.stderr, 'invalid character in the file'
        sys.exit(1)
        
    return toAutocorrelationBinarySignal(numpy.array(aArray,dtype=float))


def uchar_binary_array(signalfile,offset,count):
    aArray = numpy.fromfile(signalfile,numpy.dtype('u1'),count)
    return  toAutocorrelationBinarySignal(numpy.array(aArray,dtype=float))

    
def raw_data_array(signalfile,offset,count):
    aArray = numpy.fromfile(signalfile,numpy.dtype('u1'),count)
    zerosAndOnes = numpy.array([[(c&2**i)>>i for i in range(8)] for c in aArray], dtype = numpy.dtype('u1'))
    return toAutocorrelationBinarySignal(numpy.reshape(zerosAndOnes, len(zerosAndOnes) * 8 ))



arrayConverters = {
    'float-complex-signal':float_complex_signal_array,
    'float-signal':float_signal_array,
    'ascii-binary':ascii_binary_array,
    'uchar-binary':uchar_binary_array,
    'raw-data':raw_data_array
    }

def main():
    parser = OptionParser()
    parser.add_option("-s",
                      "--signal-file",
                      default="",
                      help="Signal file")
    parser.add_option("-t",
                      "--file-type",
                      default="",
                      help="Choose one from %s"%fileTypes)
    parser.add_option("-q",
                      "--print-number-of-samples-and-quit",
                      default = False,
                      action = 'store_true',
                      help="...")
    parser.add_option("-o","--offset",default = "0",
                      help = "set the offset (as samples)")
    parser.add_option("-n","--number-of-samples",default = "-1",
                      help = "set the number of samples (-1 meas all)")

    #parser.add_option("-N","--number-of-samples",default = "-1",
    #                  help = "set the number of samples (-1 meas all)")
    
    
    
    (options, args) = parser.parse_args()
    
    try:
        options.offset = int(options.offset)
    except ValueError:
        print>>sys.stderr, 'invalid offset'
        sys.exit(1)
    
    try:
        options.number_of_samples = int(options.number_of_samples)
    except ValueError:
        print>>sys.stderr, 'invalid number of samples'
        sys.exit(1)
    
    if options.file_type not in fileTypes:
        print>>sys.stderr, 'file_type not in fileTypes'
        sys.exit(1)
    
    signalFile = open(options.signal_file,'rb')
    
    samples, modulobytes = samples_in_file_and_seek(signalFile, options.file_type, options.offset)
    
    print 'samples %s, excess bytes %s (invalid chars included, if any)'%(samples, modulobytes)
    if options.print_number_of_samples_and_quit:
        return
    
    #seekFile(signalFile,options.file_type)
    
    aArray = arrayConverters[options.file_type](signalFile, options.offset, options.number_of_samples)



    fft = numpy.fft.fft(aArray)
    #print fft
    #cor = numpy.abs(fft)
    #print cor
    #cor = (cor * cor) / len(cor)
    specdens = fft * numpy.conj(fft) /  len(fft)

    autocorr = numpy.fft.ifft(specdens)
    autocorr = autocorr[:len(autocorr) / 2 +1]
    


    pylab.plot(numpy.real(autocorr))
    pylab.show()
    


if __name__ == '__main__':
    try:
        main()
    except IOError, e:
        print "Error: %s" %e

