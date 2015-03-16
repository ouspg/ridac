#!/usr/bin/env python2.5
from gnuradio import gr, gru, eng_notation, optfir, modulation_utils, blks2
from gnuradio import usrp
from gnuradio import blks
from gnuradio import alibaba
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import slider, powermate
from gnuradio.wxgui import stdgui, form, fftsink, waterfallsink
from optparse import OptionParser


#some installation problems?
try:
    import usrp_dbid
except:
    from usrpm import usrp_dbid

import sys
import math
import wx
import wx.lib.evtmgr as em

import myRx

plot1 = True
plot2 = True
plot3 = False

class am_plasma_rx_graph (stdgui.gui_flow_graph):
    def __init__(self,frame,panel,vbox,argv):
        stdgui.gui_flow_graph.__init__ (self,frame,panel,vbox,argv)

        parser=OptionParser(option_class=eng_option)
        parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-f", "--freq", type="eng_float", default=3e6,
                          help="set frequency to FREQ", metavar="FREQ")
        parser.add_option("-g", "--gain", type="int", default=10,
                          help="set gain in dB (default is midpoint)")

        parser.add_option("-S","--target-sample-rate",
                          type = "eng_float",
                          default = 500000,
                          help="Try to decimate the samplerate near this. default 500000"
                          )
                
        parser.add_option("", "--source-file", default=None,
                          help="set rx to come from this file.")
        
        parser.add_option("", "--source-file-repeat", default=False,
                          action='store_true',
                          help="is the file repeated. default %default")

        #parser.add_option("-d","--rx-decim", 
        #                  type = "int", 
        #                  default = 250,
        #                  help="Set this or target samplerate. possible values for this 4,6, ... ,256 (even)."
        #                  )
        #print 'for recorded files, use waterfall.py'
        (options, args) = parser.parse_args()
        
        if len(args) != 0:
            parser.print_help()
            sys.exit(1)
        
        self.frame = frame
        self.panel = panel
        
        self.vol = 0
        self.state = "FREQ"
        self.freq = 13.5e6
        
        self.rxtuner = None
        
        # build graph
        #TODO: target decim
        self.rxtuner = myRx.RxTuner(
            number_channels = 1,
            #rx_decim = options.rx_decim, 
            gains = [options.gain],
            frequencies = [options.freq],
            board = options.rx_subdev_spec,
            target_sample_rate = options.target_sample_rate,
            file_source_name = options.source_file,
            repeat = options.source_file_repeat
            )
        to_connect = self.rxtuner.connect_these()
        if to_connect:
            self.connect(*to_connect)

        
        usrp_rate = self.rxtuner.rx_sampling_rate

        print "usrp_rate:  %s" % usrp_rate
        print "usrp_decim: %s" % self.rxtuner.rx_decim
        
        # now wire it all together
        self.connect (self.rxtuner.get_rx(),
                      #self.lpfilter,
                      gr.null_sink(gr.sizeof_gr_complex))
        
        self._build_gui(vbox, usrp_rate )
        
        
        if not(self.set_freq(options.freq)):
            self._set_status_msg("Failed to set initial frequency")
        
        # set initial values
        self.set_gain(options.gain)
        
        print 'initialization done'


    def _set_status_msg(self, msg, which=0):
        self.frame.GetStatusBar().SetStatusText(msg, which)

    def _build_gui(self, vbox, usrp_rate):# , demod_rate, audio_rate):

        def _form_set_freq(kv):
            return self.set_freq(kv['freq'])

        if plot1:
            self.src_water = waterfallsink.waterfall_sink_c (
                self, self.panel, title="Data from Sensor",
                sample_rate=usrp_rate,
                fft_size=512,
                fft_rate=10,
                size=(50,100))
            print self.src_water.fft_size
            self.connect (self.rxtuner.get_rx(), self.src_water)
            vbox.Add (self.src_water.win, 1, wx.EXPAND)

        if plot2:
            self.src_fft = fftsink.fft_sink_c (
                self, self.panel, title="Data from Sensor",
                sample_rate=usrp_rate,
                fft_size=1024,
                fft_rate=15,
                size=(50,100))
            print self.src_fft.fft_size
            self.connect (self.rxtuner.get_rx(), self.src_fft)
            vbox.Add (self.src_fft.win, 1, wx.EXPAND)

        # control area form at bottom
        self.myform = myform = form.form()
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        myform['freq'] = form.float_field(
            parent=self.panel, sizer=hbox, label="Carrier Freq", weight=1,
            callback=myform.check_input_and_call(_form_set_freq, self._set_status_msg))

        hbox.Add((5,0), 0)
        myform['freq_slider'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox, weight=3,
                                        range=(0, 32e6, 0.001e6),
                                        callback=self.set_freq)
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        
        myform['gain'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox, label="Gain",
                                        weight=3, range=self.rxtuner.gain_range,
                                        callback=self.set_gain)
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)

        print 'GUI done'

    def set_freq(self, target_freq):
        """
        Set the center frequency we're interested in.

        @param target_freq: frequency in Hz
        @type: bool

        Tuning is a two step process.  First we ask the front-end to
        tune as close to the desired frequency as it can.  Then we use
        the result of that operation and our target_frequency to
        determine the value for the digital down converter.
        """
        
        self.rxtuner.set_freq(0,target_freq)
        r = self.rxtuner.tune_freq()[0]
        
        if r:
            target_freq = r
            self.freq = target_freq
            self.myform['freq'].set_value(target_freq)         # update displayed value
            self.myform['freq_slider'].set_value(target_freq)  # update displayed value
            self.update_status_bar()
            self._set_status_msg("OK", 0)
            return True

        self._set_status_msg("Failed", 0)
        return False

    def set_gain(self, gain):
        self.rxtuner.set_gain(0,gain)
        g = self.rxtuner.tune_gains()[0]
        if g:
            self.myform['gain'].set_value(g)     # update displayed value
            self.update_status_bar ()
            self._set_status_msg("OK", 0)
            return True

        self._set_status_msg("Failed", 0)
        return False


    def update_status_bar (self):
        # FIXME: refactor -> update_ui_values
        msg = "Gain:%r  Setting:%s" % (self.rxtuner.gains[0], self.state)
        self._set_status_msg(msg, 1)
        if plot1: 
            self.src_water.set_baseband_freq(self.freq)
        if plot2: 
            self.src_fft.set_baseband_freq(self.freq)

    
if __name__ == '__main__':
    app = stdgui.stdapp (am_plasma_rx_graph, "Spectrum analyzer")
    app.MainLoop ()



