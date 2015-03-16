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
from gnuradio.wxgui import stdgui, fftsink, form, scopesink
from optparse import OptionParser
from usrpm import usrp_dbid
import sys
import math
import wx

import myRx


class wfm_rx_block (stdgui.gui_flow_graph):
    def __init__(self,frame,panel,vbox,argv):
        stdgui.gui_flow_graph.__init__ (self,frame,panel,vbox,argv)

        parser=OptionParser(option_class=eng_option)
        parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-f", "--freq", type="eng_float", default=1008.0e3,
                          help="set frequency to FREQ", metavar="FREQ")
        parser.add_option("-I", "--use-if-freq", action="store_true", default=False,
                          help="use intermediate freq (compensates DC problems in quadrature boards)" )
        parser.add_option("-S","--target-sample-rate",
                          type = "eng_float",
                          default = 500000,
                          help="Try to decimate the rx samplerate near this. default %default"
                          )
        parser.add_option("-g", "--gain", type="eng_float", default=10.0,
                          help="set gain in dB (default is the midpoint)")

        parser.add_option("", "--low-pass-freq", type="eng_float", default=24e3,
                          help="the signal is lowpassed before combining to one float. default lowpass is %default.")

        parser.add_option("", "--high-pass-freq", type="eng_float", default=8e3,
                          help="the signal is filtered before futher processing. default is %default.")
        
        
        parser.add_option("", "--symbol-one-frequency", type="eng_float", default=12500.0,
                          help="set the frequency of symbol 1. default is %default")
        parser.add_option("", "--symbol-zero-frequency", type="eng_float", default=15625.0,
                          help="set the frequency of symbol 0. default is %default")
        
        parser.add_option("", "--goertz-samples", type="int", default=None,
                          help="set the goertz samples by hand. default is calculated from frequencies and samplerate")
        parser.add_option("", "--minimum-repeats", type="int", default=2,
                          help="when combining symbols, the minimum samples of one symbol. default is %default.")
        parser.add_option("", "--maximum-repeats", type="int", default=3,
                          help="when combining symbols, the minimum samples of one symbol. default is %default.")
        
        parser.add_option("", "--source-file", default=None,
                          help="set rx to come from this file.")

        parser.add_option("", "--source-file-repeat", default=False,
                          action='store_true',
                          help="is the file repeated. default %default")
        
        parser.add_option("-F", "--output-file", default='keydata.txt',
                          help="the recorded data file. default is %default")
        
        
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
        
        self.freq = 0
        
                
        self.rxtuner = myRx.RxTuner(
            number_channels = 1,
            rx_decim = None,
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

        # build graph
        
        #TODO: add an AGC after the channel filter and before the AM_demod
        
        self.u = self.rxtuner.get_rx()           # usrp is data source
        
        usrp_rate = self.rxtuner.rx_sampling_rate
        
        chanfilt_decim = 1 # if you chance this, check the goertz samples
        demod_rate = usrp_rate / chanfilt_decim
        
        ################
        
        self.chan_filt = gr.fir_filter_ccf(chanfilt_decim, [1])
        self.bpf = gr.fir_filter_fff(chanfilt_decim, [1])
        self.lpfreq = options.low_pass_freq
        self.hpfreq = options.high_pass_freq
        
        self.am_demod = gr.complex_to_mag()
        
        # now wire it all together
        """Goertzel single-bin DFT calculation. 
        see http://en.wikipedia.org/wiki/Goertzel_algorithm"""
        
        """ nyquist frequency. TODO: own amounts for both"""
        if options.goertz_samples != None:
            self.goertz_samples = options.goertz_samples#80
        else:
            self.goertz_samples = usrp_rate * 2.1 / min(options.symbol_one_frequency, 
                                                         options.symbol_zero_frequency)
        self.goertz_samples = int(self.goertz_samples + 0.5)
        
        self.sym_a = gr.goertzel_fc(
            demod_rate, self.goertz_samples, int(options.symbol_one_frequency+0.5))
        self.sym_b = gr.goertzel_fc(
            demod_rate, self.goertz_samples, int(options.symbol_zero_frequency+0.5))
        
        self.connect(self.u, self.chan_filt, self.am_demod, self.bpf, self.sym_a)
        self.connect(self.bpf, self.sym_b)
        
        self.data = gr.add_ff()
        self.slicer = gr.binary_slicer_fb()
        
        #TODO: find a better way to correct errors. viterbi smth ...?
        self.combiner = alibaba.combine_symbols_bb(
            options.minimum_repeats, options.maximum_repeats)#2,3
        
        self.connect(self.sym_a, gr.complex_to_mag(), (self.data,0))
        self.connect(self.sym_b, gr.complex_to_mag(), gr.multiply_const_ff(-1), (self.data,1))
        self.connect(self.data, self.slicer, self.combiner, gr.char_to_float(),
                     gr.add_const_ff(48), gr.float_to_char(),
                     gr.file_sink(gr.sizeof_char, options.output_file))
        
        self._build_gui(vbox, usrp_rate, demod_rate)
        
        
        self.gain = options.gain
        
        
        if abs(options.freq) < 1e3:
            options.freq *= 1e3
        
        # set initial values
        
        self.usrp_rate = usrp_rate
        self.set_gain(options.gain)
        self.set_lpf(self.lpfreq)
        if not(self.set_freq(options.freq)):
            self._set_status_msg("Failed to set initial frequency")

    def design_filters():
        
        """
        low_pass (double gain, 
                  double sampling_freq, 
                  double cutoff_freq, 
                  double transition_width, 
                  win_type window=WIN_HAMMING, double beta=6.76)
        """
        chan_filt_coeffs = gr.firdes.low_pass(1, self.usrp_rate, self.lpfreq, 16e3)
        
        """
        band_pass (double gain,
                   double sampling_freq, 
                   double low_cutoff_freq, 
                   double high_cutoff_freq, 
                   double transition_width, 
                   win_type window=WIN_HAMMING, double beta=6.76)
        """
        
        bpf_filt_coeffs = gr.firdes.band_pass(1, self.usrp_rate, self.hpfreq, self.lpfreq, 1e3)

        self.chan_filt.set_taps(chan_filt_coeffs)
        self.bpf.set_taps(bpf_filt_coeffs)
        


    def _set_status_msg(self, msg, which=0):
        self.frame.GetStatusBar().SetStatusText(msg, which)


    def _build_gui(self, vbox, usrp_rate, demod_rate):

        def _form_set_freq(kv):
            return self.set_freq(kv['freq'])


        if 0:
            self.src_fft = fftsink.fft_sink_c(self.panel, title="Data from USRP",
                                               fft_size=256, sample_rate=usrp_rate,
                                               ref_scale=32768.0, ref_level=0.0, y_divs=12)
            self.connect (self.u, self.src_fft)
            vbox.Add (self.src_fft.win, 4, wx.EXPAND)

        if 1:
            self.post_filt_fft = fftsink.fft_sink_c(self, self.panel, title="Post Channel filter",
                                               fft_size=512, sample_rate=demod_rate)
            self.connect (self.chan_filt, self.post_filt_fft)
            vbox.Add (self.post_filt_fft.win, 4, wx.EXPAND)

        if 0:
            post_demod_fft = fftsink.fft_sink_f(self, self.panel, title="Post Demod", 
                                                fft_size=1024, sample_rate=demod_rate,
                                                y_per_div=10, ref_level=0)
            self.connect (self.am_demod, post_demod_fft)
            vbox.Add (post_demod_fft.win, 4, wx.EXPAND)

        if 1:
            post_demod_scope = scopesink.scope_sink_f(self, self.panel,
                                                 title="Data from Sensor",
                                                 sample_rate=demod_rate/self.goertz_samples,
                                                 v_scale=2,
                                                 t_scale=2e-3,
                                                 size=(512,100))
            self.connect(self.sym_a, gr.complex_to_mag(), (post_demod_scope,0))
            self.connect(self.sym_b, gr.complex_to_mag(), (post_demod_scope,1))
            self.connect(self.slicer, gr.char_to_float(), gr.multiply_const_ff(100), (post_demod_scope,2))
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
            form.quantized_slider_field(parent=self.panel, sizer=hbox, label="Channel bandwidth",
                                        weight=3, range=(4e3, usrp_rate/2, 2e3),
                                        callback=self.set_lpf)
        hbox.Add((5,0), 1)

        myform['gain'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox, label="Gain",
                                        weight=3, range=self.rxtuner.gain_range,
                                        callback=self.set_gain)
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)

    def set_lpf (self, lpfreq):
        self.update_status_bar()
        self.lpfreq = lpfreq
        
        chan_filt_coeffs = gr.firdes.low_pass(1, self.usrp_rate, lpfreq, 16e3)
        bpf_filt_coeffs = gr.firdes.band_pass(1, self.usrp_rate, 8e3, lpfreq, 1e3)
        self.chan_filt.set_taps(chan_filt_coeffs)
        self.bpf.set_taps(bpf_filt_coeffs)
        

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

        #TODO: check if db is inverting the spectrum or not to decide if we should do + self.IF_freq  or - self.IF_freq
        
        self.rxtuner.set_freq(0,target_freq+ self.IF_freq)
        r = self.rxtuner.tune_freq()[0] 
        if r:
            target_freq = r
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
        msg = "Chanfilt BW:%.0fk  gain:%.0fdB" % (self.lpfreq/1000, self.gain)
        self._set_status_msg(msg, 1)
        try:
          self.src_fft.set_baseband_freq(self.freq)
        except:
          None
          
        

if __name__ == '__main__':
    app = stdgui.stdapp (wfm_rx_block, "FSK demod demo")
    app.MainLoop ()
