#!/usr/bin/env python2.5
import sys
import time

print "Loading gnuradio..."
from optparse import OptionParser
from gnuradio import gr, gru, eng_notation, optfir
from gnuradio.eng_option import eng_option
from numpy import add


def bandpass_design(fs, fc, flow, fhigh, trans):
    """Design FIR bandpass filter"""
    fir_l = gr.firdes.band_pass(10, fs, fc-fhigh, fc-flow, trans)
    fir_u = gr.firdes.band_pass(10, fs, fc+flow, fc+fhigh, trans)
    return add(fir_l, fir_u)

class cmdlineSender(gr.top_block):
    def __init__(self, options, args):
        gr.top_block.__init__(self)
        
        # File source
        src = gr.file_source(
                gr.sizeof_gr_complex,
                options.recorded_file,
                False)
        fs = options.sample_rate

        # Filter
        fc = options.center_frequency
        flow = options.low_frequency
        fhigh = options.high_frequency
        #trans = 8e3
        trans = options.transition_width

        bandpass_coeffs = bandpass_design(fs, fc, flow, fhigh, trans)
        filter = gr.fir_filter_ccf(1, bandpass_coeffs)
        
        # file sink
        out = gr.file_sink(gr.sizeof_gr_complex, options.recorded_file+".filtered")

        # Connect blocks
        self.connect(src, filter, out)

if __name__ == "__main__":
        parser=OptionParser(option_class=eng_option)
        parser.add_option("-S", "--sample-rate", type="eng_float",
                          help="sample rate of the file", metavar="FREQ")
        parser.add_option("-C", "--center-frequency", 
                          type="eng_float",default = 125e3,
                          help="The center frequency. default %default", metavar="FREQ")
        parser.add_option("-L", "--low-frequency", 
                          type="eng_float",default = 2e3,
                          help="The distance of pass from the center freq. default %default", metavar="FREQ")
        parser.add_option("-H", "--high-frequency", 
                          type="eng_float",default = 60e3,
                          help="The distance of the end of pass from the center freq. default %default", metavar="FREQ")
        parser.add_option("-T", "--transition-width", 
                          type="eng_float",default = 1e3,
                          help="The transition width of the filter. default %default", metavar="FREQ")



        parser.add_option("-F", "--recorded-file", default="newrecord.craw",
                          help="captured data file")
        (options, args) = parser.parse_args()
        
        print 'called', time.strftime("%Y-%m-%d %H:%M:%S")
        sender = cmdlineSender(options, args)
        print 'start', time.strftime("%Y-%m-%d %H:%M:%S")
        try:
                sender.run()
        except KeyboardInterrupt:
                raise SystemExit
        print 'end', time.strftime("%Y-%m-%d %H:%M:%S")
    
    
