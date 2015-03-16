#!/usr/bin/env python2.5
import sys
import time

from optparse import OptionParser
from gnuradio import gr, gru, eng_notation, optfir
from gnuradio import usrp
from gnuradio.eng_option import eng_option
from numpy import add
#some installation problems?
try:
        import usrp_dbid
except:
        from usrpm import usrp_dbid
import myTx


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
                True)
        fs = options.sample_rate
	
        # Filter
        if not options.recorded_file or not options.low_cut or not options.high_cut or not options.transition or not options.carrier:
                print "Not using filter"
                filter = gr.multiply_const_cc(1.)
        else:
                fc = options.carrier
                flow = options.low_cut
                fhigh = options.high_cut
                trans = options.transition
                bandpass_coeffs = bandpass_design(fs, fc, flow, fhigh, trans)
                print "fc = %s, flow = %s, fhigh = %s, trans = %s" % (\
                        fc, flow, fhigh, trans)
                filter = gr.fir_filter_ccf(1, bandpass_coeffs)
	
        # RF TX
        txtuner = myTx.TxTuner(fs,
                               options.freq,
                               options.gain)
        # Connect blocks
        self.connect(src, filter, txtuner.get_tx())

if __name__ == "__main__":
        parser=OptionParser(option_class=eng_option)
        parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-f", "--freq", type="eng_float", default=0,
                          help="set mixing frequency to FREQ", metavar="FREQ")
        parser.add_option("-S", "--sample-rate", type="eng_float",
                          help="sample rate of the file", metavar="FREQ")
        parser.add_option("-g", "--gain", type="int", default=1,
                          help="set gain in dB (default is 1)")
        parser.add_option("-F", "--recorded-file",
                          help="captured data file")
        parser.add_option("-c", "--carrier", type="eng_float",
                          help="Carrier frequency (to block)")
        parser.add_option("-l", "--low-cut", type="eng_float",
                          help="Lower cutoff frequency")
        parser.add_option("-i", "--high-cut", type="eng_float",
                          help="Higher cutoff frequency")
        parser.add_option("-t", "--transition", type="eng_float",
                          help="Transition bandwidth", default=8e3)
        (options, args) = parser.parse_args()
        if not options.recorded_file:
                raise SystemExit("Filename not specified. See help, -h")
        if not options.sample_rate:
                raise SystemExit("Samplerate not specified. See help -h")
        print 'called', time.strftime("%Y-%m-%d %H:%M:%S")
        sender = cmdlineSender(options, args)
        print 'start', time.strftime("%Y-%m-%d %H:%M:%S")
        try:
                sender.run()
        except KeyboardInterrupt:
                raise SystemExit
        print 'end', time.strftime("%Y-%m-%d %H:%M:%S")
    
    
