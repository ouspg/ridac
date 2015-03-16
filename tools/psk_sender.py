#!/usr/bin/env python2.5

import sys
import time

print "Loading gnuradio..."
from optparse import OptionParser
from gnuradio import gr, gru, eng_notation, optfir
from gnuradio import usrp
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
from gnuradio.alibaba import sequence_repeater_bb


def make_constellation(m):
    return [cmath.exp(i * 2 * pi / m * 1j) for i in range(m)]
        
# Common definition of constellations for Tx and Rx
constellation = {
    2 : make_constellation(2),           # BPSK
    4 : make_constellation(4),           # QPSK
    8 : make_constellation(8)            # 8PSK
    }

binary_to_ungray = {
    2 : (0, 1),
    4 : (0, 1, 2, 3),
    8 : (0, 1, 2, 3, 4, 5, 6, 7)
    }

class cmdlineSender(gr.top_block):
    def __init__(self, options, args):
        gr.top_block.__init__(self)
        
        # File source

        arity = 2
        
        #this could be done this way, but what about 
        #if the amount of bits % 8 != 0 ?
        # turn bytes into k-bit vectors
        #self.bytes2chunks = \
        #    gr.packed_to_unpacked_bb(self.bits_per_symbol(), gr.GR_MSB_FIRST)
        
        self.src = gr.file_source(
            gr.sizeof_char,
            options.file,
            options.no_repeat_file)
        asciimaps = [0]*256
        asciimaps[ord('1')] = 1
        asciimaps[1] = 1
        self.symbol_mapper = gr.map_bb(tuple(asciimaps))
        
        self.repeater = sequence_repeater_bb()
        self.repeater.set_repeat_count(options.repeat_factor)
        
        self.diffenc = gr.diff_encoder_bb(arity)
        
        self.chunks2symbols = gr.chunks_to_symbols_bc(constellation[arity])
        
        # DSB modulator
        self.bfo = gr.sig_source_f(options.target_samplerate,
                                   gr.GR_COS_WAVE,
                                   options.bfo_freq,
                                   8000,
                                   0)
        self.bfo_c = gr.float_to_complex()
        self.connect(self.bfo, self.bfo_c)
        self.dsb_mod = gr.multiply_cc()
        txtuner = myTx.TxTuner(options.target_samplerate, #target samplerate
                               options.freq, #mixing freq
                               options.gain)
	if options.differential_encoding:
		encodingpoint = self.diffenc
	else:
		encodingpoint = self.repeater
        # Connect blocks
        self.connect(self.bfo_c, (self.dsb_mod, 1))
        self.connect(self.src, 
                     self.symbol_mapper)
	
	
	if options.differential_encoding:
		self.connect(
			self.symbol_mapper,
			self.diffenc,
			self.repeater)
	else:
		self.connect(
			self.symbol_mapper,
			self.repeater)
	self.connect(
		self.repeater,
		self.chunks2symbols, 
		#self.upsampler,
		(self.dsb_mod, 0)
		)
        self.connect(self.dsb_mod, gr.add_const_cc(8000),
                     txtuner.get_tx())

if __name__ == "__main__":
        parser=OptionParser(option_class=eng_option)
        parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-B", "--bfo_freq", type="eng_float", default=0,
                          help="set BFO frequency to FREQ (to do DSB modulation)", metavar="FREQ")
        parser.add_option("-f", "--freq", type="eng_float", default=125e3,
                          help="set carrier frequency to FREQ", metavar="FREQ")
        parser.add_option("-L", "--repeat-factor", type="int", default=32,
                          help="repeat factor.")
        parser.add_option("-S", "--target-samplerate", type="eng_float", default=250000,
                          help="target samplerate .. datarate * repeats = target samplerate")
        parser.add_option("-g", "--gain", type="int", default=1,
                          help="set gain in dB (default is 1)")
        parser.add_option("-F", "--file", default="",
                          help="sent signal ascii file")
        parser.add_option("-r", "--no-repeat-file", default=True, action='store_false',
                         help="do NOT repeat the file. default is True")
	
	parser.add_option("-D", "--differential-encoding",
                          default=True,
			  action="store_false",
                         help="default is True")
        
	
        parser.add_option("-b", "--bits-per-symbol", type="int",
                          default=2,
                         help="default is 2")
                     
        (options, args) = parser.parse_args()
        
        print 'called', time.strftime("%Y-%m-%d %H:%M:%S")
        sender = cmdlineSender(options, args)
        print 'start', time.strftime("%Y-%m-%d %H:%M:%S")
        try:
                sender.run()
        except KeyboardInterrupt:
                raise SystemExit
        print 'end', time.strftime("%Y-%m-%d %H:%M:%S")
    
    
