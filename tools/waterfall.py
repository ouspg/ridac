#!/usr/bin/env python2.5

from optparse import OptionParser
from gnuradio import gr, gru, eng_notation, optfir, window
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import stdgui2, waterfallsink2, form
import wx
from math import log
import cmd

class waterfall_top_block (stdgui2.std_top_block):
    def __init__(self, frame, panel, vbox, argv):
        stdgui2.std_top_block.__init__ (self, frame, panel, vbox, argv)

        fft_size = 512
        input_rate = options.sample_rate
        complex = False
        # Blocks
        self.src = gr.file_source(gr.sizeof_gr_complex, options.recorded_file, True)
        self.c2r = gr.complex_to_real()
        if complex:
                self.gain = gr.multiply_const_cc(1)
                self.thr = gr.throttle(gr.sizeof_gr_complex, input_rate)
                waterfall = waterfallsink2.waterfall_sink_c
        else:
                self.gain = gr.multiply_const_ff(1)
                self.thr = gr.throttle(gr.sizeof_float, input_rate)
                waterfall = waterfallsink2.waterfall_sink_f
        self.waterfall = waterfall(panel,
                            title="Waterfall graph", fft_size=fft_size,
                            fft_rate=15, sample_rate=input_rate, baseband_freq=0)
        # Connect blocks together
        if complex:
                self.connect(self.src, self.thr, self.gain, self.waterfall)
        else:
                self.connect(self.src, self.c2r, self.thr, self.gain, self.waterfall)

        self.build_gui(frame, panel, vbox, argv)
        self.set_gain(options.gain)
    
    def build_gui(self, frame, panel, vbox, argv):
        self.form = {}
        vbox.Add (self.waterfall.win, 1, wx.EXPAND)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        self.form['gain'] = form.quantized_slider_field(parent=panel, sizer=hbox, label="Gain",
                                        weight=3, range=(-30., 30., 0.5),
                                        callback=self.set_gain)
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)
    
    def set_gain(self, gain):
        self.gain.set_k(pow(10, gain/10))
        result = abs(self.gain.k())
        self.form['gain'].set_value(gain)
        print "Set gain to %s dB (%s)." % (gain, result)

def main ():
    app = stdgui2.stdapp (waterfall_top_block, "Waterfall")
    app.MainLoop ()

if __name__ == '__main__':
        parser=OptionParser(option_class=eng_option)
        parser.add_option("-S", "--sample-rate", type="eng_float",
                          help="sample rate of the file (set lower to slow down, default 256k)", metavar="FREQ",
                          default=256e3)
        parser.add_option("-g", "--gain", type="int", default=0,
                          help="set gain in dB (default is 0 dB)")
        parser.add_option("-F", "--recorded-file",
                          help="captured data file")
        (options, args) = parser.parse_args()
        if not options.recorded_file:
                raise SystemExit("Filename not specified. See help, -h")
        main ()

