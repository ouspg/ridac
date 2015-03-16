#!/usr/bin/env python2.5

import sys
import time

print "Loading gnuradio..."
from optparse import OptionParser
from gnuradio import gr, gru, eng_notation, optfir
from gnuradio import usrp, audio
from gnuradio.eng_option import eng_option
from numpy import add

from math import pi, sqrt
import cmath

#some installation problems?
try:
        import usrp_dbid
except:
        from usrpm import usrp_dbid
import myTx


#in new versions of gnuradio use gr_repeater
from gnuradio import alibaba

class cmdlineSender(gr.top_block):
    def __init__(self, options, args):
        gr.top_block.__init__(self)
        
        # Data source: file
        self.src = gr.file_source(
            gr.sizeof_char,
            options.file,
            options.do_not_repeat_file)
        # ascii or binary 0 and 1 represent symbols, everything else is mapped to 0.
        asciimaps = [0]*256
        asciimaps[ord('1')] = 1
        asciimaps[1] = 1
        self.symbol_mapper = gr.map_bb(tuple(asciimaps))
        
        sym_a_freq = options.symbol_one_frequency #125000./10
        sym_b_freq = options.symbol_zero_frequency #125000./8
        
	""" There is blocks in current version of gnuradio"""
        self.sigsource=alibaba.controlled_signalsource_bc(
            options.target_samplerate,
            sym_a_freq,
            sym_b_freq,
            1, # amplitude
            0,
            options.repeat_factor) # cycles per symbol

        """ DSB modulator """
	"""
	double sampling_freq, 
	gr_waveform_t waveform, 
	double frequency, 
	double ampl, 
	float offset"""
        self.bfo = gr.sig_source_f(
		options.target_samplerate,
		gr.GR_COS_WAVE,
		options.bfo_freq,
		8000,
		0)
        self.bfo_c = gr.float_to_complex()
        self.connect(self.bfo, self.bfo_c)
        self.dsb_mod = gr.multiply_cc()
        self.connect(self.bfo_c, (self.dsb_mod, 1))
        txtuner = myTx.TxTuner(
		options.target_samplerate, #target samplerate
		options.freq, #mixing freq
		options.gain)
	
        # Connect blocks
        self.connect(self.src, 
		     self.symbol_mapper, 
		     self.sigsource, 
                     gr.add_const_cc(2), # Add carrier
                     gr.complex_to_real(),
                     gr.float_to_complex(),
		     (self.dsb_mod, 0))
        self.connect(self.dsb_mod, txtuner.get_tx())

if __name__ == "__main__":
        parser=OptionParser(option_class=eng_option)
        parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-B", "--bfo_freq", type="eng_float", default=0,
                          help="set BFO frequency to FREQ (to do DSB modulation)", metavar="FREQ")
        parser.add_option("-f", "--freq", type="eng_float", default=125e3,
                          help="set carrier frequency to FREQ", metavar="FREQ")
        parser.add_option("-L", "--repeat-factor", type="int", default=32,
                          help="repeat factor. the duration of one symbol is cycle length * repeat factor. (cycle length comes from symbol's frequency). default is %default")
	parser.add_option("", "--symbol-one-frequency", type="eng_float", default=1000,
                          help="set the frequency of symbol 1. default is %default. Usually carrier freq/k1, where k1 is some uint.")
        parser.add_option("", "--symbol-zero-frequency", type="eng_float", default=2000,
                          help="set the frequency of symbol 0. default is %default. Usually carrier freq/k2, where k2 is some uint.")
        parser.add_option("-S", "--target-samplerate", type="eng_float", default=250000,
                          help="target samplerate .. datarate * repeats = samplerate")
        parser.add_option("-g", "--gain", type="int", default=1,
                          help="set gain in dB (default is 1)")
        parser.add_option("-F", "--file", default="",
                          help="sent signal ascii binary file")
        parser.add_option(
		"-r", "--do-not-repeat-file", default=True, action='store_false',
		help="repeat the file. default is false")
	
	
        (options, args) = parser.parse_args()
        
        print 'called', time.strftime("%Y-%m-%d %H:%M:%S")
        sender = cmdlineSender(options, args)
        print 'start', time.strftime("%Y-%m-%d %H:%M:%S")
        try:
                sender.run()
        except KeyboardInterrupt:
                raise SystemExit
        print 'end', time.strftime("%Y-%m-%d %H:%M:%S")
    
    
