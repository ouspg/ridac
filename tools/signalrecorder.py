#!/usr/bin/env python2.5

from gnuradio import gr, gru, eng_notation, optfir
from gnuradio import usrp
from gnuradio.eng_option import eng_option

import time
#from time import time

from optparse import OptionParser

#some installation problems?
try:
    import usrp_dbid
except:
    from usrpm import usrp_dbid

#from gnuradio import alibaba 


import myRx
import sys


class  cmdlineRecorder(gr.top_block):
    def __init__(self):
        #stdgui.gui_flow_graph.__init__ (self,frame,panel,vbox,argv)
        gr.top_block.__init__(self)
        parser=OptionParser(option_class=eng_option)
        parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        
        parser.add_option("-f", "--freq", type="eng_float", default=3e6,
                          help="set frequency to FREQ", metavar="FREQ")
        
        parser.add_option("-g", "--gain", type="int", default=1,
                          help="set gain in dB (default is 1)")
        
        parser.add_option("-d", "--decim", type="int", default=8,
                          help="set the decim [4...256]. default is 8")

        parser.add_option("-S","--target-sample-rate",
                          type = "eng_float",
                          default = None,
                          help="Try to decimate the samplerate near this. If set overrides the decim."
                          )
        
        parser.add_option("-F", "--recorded-file", default="newrecord.craw",
                          help="where the data is stored")
        
        #parser.add_option("-L", "--low-cutoff", type = "int", default=12000,
        #                  help="the lower cutoff freq")

        #parser.add_option("-H", "--high-cutoff", type = "int", default=16000,
        #                  help="the lower cutoff freq")

        #parser.add_option("-t", "--transition-width", type = "int", default=1000,
        #                  help="the transition width of the bandpass filter")
        
        
        
        #transition_width
        
        #firdes_complex_band_pass

        #parser.add_option("-h", "--help", default = False, 
        #                  action= "store_true", 
        #                  help = "show help")

        (options, args) = parser.parse_args()
        
        #if options.help:
        #    dir(options)
        #    sys.exit(0)
        self.rxtuner = myRx.RxTuner(
                number_channels = 1,
                rx_decim = options.decim,
                gains = [options.gain],
                frequencies = [options.freq],
                board = options.rx_subdev_spec,
                target_sample_rate = options.target_sample_rate
                )
        
        self.out = gr.file_sink(
            gr.sizeof_gr_complex,
            options.recorded_file
            )
        

        print "self.rxtuner.rx_sampling_rate", self.rxtuner.rx_sampling_rate
        
        #taps = gr.firdes_complex_band_pass(
        #    1, #gain
        #    self.rxtuner.rx_sampling_rate,
        #    options.low_cutoff,
        #    options.high_cutoff,
        #    options.transition_width)
        
        #self.filter = gr.fft_filter_ccc(
        #    1, #decimation
        #    taps
        #    )

        self.connect(self.rxtuner.get_rx(), self.out) #self.filter, self.out)




if __name__ == "__main__":
    print 'called', time.strftime("%Y-%m-%d %H:%M:%S")
    recorder = cmdlineRecorder()
    print 'start', time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        recorder.run()
    except Exception, e:
        print type(e), e
    
    print 'end', time.strftime("%Y-%m-%d %H:%M:%S")
    
    
