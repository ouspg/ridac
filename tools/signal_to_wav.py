#!/usr/bin/env python2.5
from optparse import OptionParser

#from sys import argv
from os import path
import sys

print "Loading gnuradio..."
from gnuradio import gr
from gnuradio import audio


fileTypes = ['float-complex-signal', 'float-signal']
class my_top_block(gr.top_block):
    def __init__(self, options):
        gr.top_block.__init__(self)
        srcfile = options.source_file 
        dstfile = options.destination_file
        print "srcfile =", srcfile
        print "dstfile =", dstfile
        print 'type',
        if options.source_file_type == 'float-complex-signal':
            src = gr.file_source(gr.sizeof_gr_complex, srcfile, False)
            real = gr.complex_to_real()
            self.connect(src, real)
        elif options.source_file_type == 'float-signal':
            real = gr.file_source(gr.sizeof_float, srcfile, False)
        #short = gr.float_to_short()
        dst = gr.wavfile_sink(dstfile, 1, 96000, 16)
        sound = audio.sink(96000)
        self.connect(real, 
                     #short, 
                     dst)




if __name__ == '__main__':
    parser = parser = OptionParser()
    parser.add_option(
        "-d",
        "--destination-file",
        default=None,
        help="The destination file.")
    
    parser.add_option(
        "-s",
        "--source-file",
        default=None,
        help="The source file.")
    
    parser.add_option("-t",
                      "--source-file-type",
                      default="",
                      help="Choose one from %s"%fileTypes)
    (options, args) = parser.parse_args()
    
    if options.source_file_type not in fileTypes:
        print>>sys.stderr, 'source_file_type not in fileTypes'
        sys.exit(1)
        
    
    my_top_block(options).run()

