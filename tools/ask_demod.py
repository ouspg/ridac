#!/usr/bin/env python2.5

#
# Copyright 2005,2006,2007 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

from gnuradio import gr, gru, eng_notation, optfir
from gnuradio import usrp
from gnuradio import blks2
from gnuradio import alibaba
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import slider, powermate
from gnuradio.wxgui import stdgui2, fftsink2, form, scopesink2
from optparse import OptionParser
from usrpm import usrp_dbid
import sys
import math
import wx


import myRx

class wfm_rx_block (stdgui2.std_top_block):
    def __init__(self,frame,panel,vbox,argv):
        stdgui2.std_top_block.__init__ (self,frame,panel,vbox,argv)

        parser=OptionParser(option_class=eng_option)
        parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-f", "--freq", type="eng_float", default=1008.0e3,
                          help="set frequency to FREQ", metavar="FREQ")

        parser.add_option("-I", "--use-if-freq", action="store_true", default=False,
                          help="use intermediate freq (compensates DC problems in quadrature boards)" )
        
        parser.add_option("-L", "--lpfreq", type="eng_float", default=20e3,
                          help="set lp frequency to FREQ. default %default", metavar="FREQ")
        
        parser.add_option("-H", "--hpfreq", type="eng_float", default=4e3,
                          help="set hipass freq to FREQ. default is %default", metavar="FREQ")

        parser.add_option("-g", "--gain", type="eng_float", default=None,
                          help="set gain in dB (default is maximum)")

        parser.add_option("-O", "--file-output", type="string", default=None,
                          help="demodulated signal filename. default = None")

        
        parser.add_option("", "--source-file", default=None,
                          help="set rx to come from this file.")

        parser.add_option("", "--source-file-repeat", default=False,
                          action='store_true',
                          help="is the file repeated. default %default")

        parser.add_option("-S","--target-sample-rate",
                          type = "eng_float",
                          default = 1000000.,
                          help="Try to decimate the rx samplerate near this. default %default"
                          )


        print 'usrp -> lowpass -> am demod -> highpass -> scope (and float array file if output not None)'
        (options, args) = parser.parse_args()
        if len(args) != 0:
            parser.print_help()
            sys.exit(1)
        
        self.frame = frame
        self.panel = panel
        self.use_IF=options.use_if_freq
        if self.use_IF:
          self.IF_freq=64000.0 
        else:
          self.IF_freq=0.0
        
        self.freq = options.freq
        if abs(self.freq) < 1e3:
            self.freq *= 1e3

        self.hipassfreq = options.hpfreq
        
        
        #TODO: add an AGC after the channel filter and before the AM_demod

        # build graph 

        #set the usrp1
        self.rxtuner = myRx.RxTuner(
                number_channels = 1,
                gains = [options.gain],
                frequencies = [self.freq],
                board = options.rx_subdev_spec,
                target_sample_rate = options.target_sample_rate,
                file_source_name = options.source_file,
                repeat = options.source_file_repeat
                )
        
        to_connect = self.rxtuner.connect_these()
        if to_connect:
            self.connect(*to_connect)

        
        chanfilt_decim = 2
        demod_rate = self.rxtuner.rx_sampling_rate / chanfilt_decim
        
        ################
        
        self.chan_filt = gr.fir_filter_ccf(chanfilt_decim, [1])
        self.lpfreq = options.lpfreq 
        self.am_demod = gr.complex_to_mag()
        

        hpfcoeffs = gr.firdes.high_pass(1, self.rxtuner.rx_sampling_rate, self.hipassfreq, 4e3)
        self.hpf = gr.fir_filter_fff (1, hpfcoeffs)


        # sinks
        self.sink = gr.null_sink(gr.sizeof_float)
        if options.file_output != None:
            print 'recording to',options.file_output
            self.sink =  gr.file_sink(gr.sizeof_float,options.file_output)
        
        # now wire it all together
        #self.splitter = alibaba.blocksplitter_ff(20, 80, -200)
        self.connect (self.rxtuner.get_rx(), self.chan_filt, self.am_demod, self.hpf, 
                      #self.splitter, 
                      self.sink)

        self._build_gui(vbox, demod_rate)


        # set initial values
        
        #self.usrp_rate = usrp_rate
        self.set_gain(self.rxtuner.gains[0])
        self.set_lpf(self.lpfreq)
        if not(self.set_freq(options.freq)):
            self._set_status_msg("Failed to set initial frequency")


    def _set_status_msg(self, msg, which=0):
        self.frame.GetStatusBar().SetStatusText(msg, which)


    def _build_gui(self, vbox, demod_rate):

        def _form_set_freq(kv):
            return self.set_freq(kv['freq'])


        if 0:
            self.src_fft = fftsink2.fft_sink_c(self.panel,
                                               title="Data from USRP",
                                               fft_size=512,
                                               sample_rate=self.rxtuner.rx_sampling_rate,
                                               ref_scale=32768.0,
                                               ref_level=0.0,
                                               y_divs=12)
            self.connect (self.rxtuner.get_rx(), self.src_fft)
            vbox.Add (self.src_fft.win, 4, wx.EXPAND)

        if 1:
            self.post_filt_fft = fftsink2.fft_sink_c(self.panel, title="Post Channel filter",
                                               fft_size=512, sample_rate=demod_rate)
            self.connect (self.chan_filt, self.post_filt_fft)
            vbox.Add (self.post_filt_fft.win, 4, wx.EXPAND)

        if 0:
            post_demod_fft = fftsink2.fft_sink_f(self.panel, title="Post Demod", 
                                                fft_size=1024, sample_rate=demod_rate,
                                                y_per_div=10, ref_level=0)
            self.connect (self.am_demod, post_demod_fft)
            vbox.Add (post_demod_fft.win, 4, wx.EXPAND)

        if 1:
            post_demod_scope = scopesink2.scope_sink_f(self.panel,
                                                 title="Data from Sensor",
                                                 sample_rate=demod_rate,
                                                 size=(512,100))
            self.connect(self.hpf, post_demod_scope)
            vbox.Add(post_demod_scope.win, 4, wx.EXPAND)

        
        # control area form at bottom
        self.myform = myform = form.form()

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        myform['freq'] = form.float_field(
            parent=self.panel, sizer=hbox, label="Freq", weight=1,
            callback=myform.check_input_and_call(_form_set_freq, self._set_status_msg))

        hbox.Add((5,0), 0)
        myform['freq_slider'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox, weight=3,
                                        range=(64e3, 320e3, 1e3),
                                        callback=self.set_freq)
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)

        myform['chanfilt_freq'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox, label="lowpass freq",
                                        weight=3, range=(self.hipassfreq,self.rxtuner.rx_sampling_rate/2, 2e3),
                                        callback=self.set_lpf)
        hbox.Add((5,0), 1)

        myform['gain'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox, label="Gain",
                                        weight=3, range=self.rxtuner.get_gain_range(),
                                        callback=self.set_gain)
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)

    def set_lpf (self, lpfreq):
        self.update_status_bar()
        self.lpfreq = lpfreq
        chan_filt_coeffs = gr.firdes.low_pass(1, self.rxtuner.rx_sampling_rate, lpfreq, 16e3)
        self.chan_filt.set_taps(chan_filt_coeffs)



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
        msg = "Chanfilt BW:%.0fk  gain:%.0fdB" % (self.lpfreq/1000, self.rxtuner.gains[0])
        self._set_status_msg(msg, 1)
        try:
          self.src_fft.set_baseband_freq(self.freq)
        except:
          None
          
    def volume_range(self):
        return (-40.0, 0.0, 0.5)
        

if __name__ == '__main__':
    app = stdgui2.stdapp (wfm_rx_block, "ASK demod demo")
    app.MainLoop ()
