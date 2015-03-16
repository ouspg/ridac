#!/usr/bin/env python2.5
import sys
import time

print "Loading gnuradio..."
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

class cmdlineSender(gr.top_block):
    def __init__(self, options, args):
        gr.top_block.__init__(self)
        
        # File source
        fs = 250000
        src = gr.sig_source_c(fs, gr.GR_SIN_WAVE, options.freq, 30000)

        # RF TX
        txtuner = myTx.TxTuner(fs, #target samplerate
                               0, #mixing freq
                               options.gain)
        # Connect blocks
        self.connect(src, txtuner.get_tx())

if __name__ == "__main__":
        parser=OptionParser(option_class=eng_option)
        parser.add_option("-T", "--tx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-f", "--freq", type="eng_float", default=125e3,
                          help="set sine frequency to FREQ", metavar="FREQ")
        parser.add_option("-g", "--gain", type="int", default=1,
                          help="set gain in dB (default is 1)")
        (options, args) = parser.parse_args()
        
        print 'called', time.strftime("%Y-%m-%d %H:%M:%S")
        sender = cmdlineSender(options, args)
        print 'start', time.strftime("%Y-%m-%d %H:%M:%S")
        try:
                sender.run()
        except KeyboardInterrupt:
                raise SystemExit
        print 'end', time.strftime("%Y-%m-%d %H:%M:%S")
    
    
