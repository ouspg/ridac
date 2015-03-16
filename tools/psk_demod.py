#!/usr/bin/env python2.5

from gnuradio import gr, gru, eng_notation, optfir, modulation_utils, blks2
from gnuradio import usrp
from gnuradio import blks
from gnuradio import alibaba
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import slider, powermate
from gnuradio.wxgui import stdgui, form, fftsink, waterfallsink, scopesink
from optparse import OptionParser
from gnuradio.blks2impl import psk
from math import pi, sqrt, log10
import math, cmath

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

verbose = True
logging = True

# default values (used in __init__ and add_options)
_def_samples_per_symbol = 32
_def_excess_bw = 0.35
_def_gray_code = True
_def_verbose = False
_def_log = False

_def_costas_alpha = 0.1
_def_gain_mu = None
_def_mu = 0.5
_def_omega_relative_limit = 0.005



class psk_demod_demo_graph (stdgui.gui_flow_graph):
    def __init__(self,frame,panel,vbox,argv):
        stdgui.gui_flow_graph.__init__ (self,frame,panel,vbox,argv)

        self.parser=OptionParser(option_class=eng_option)
        self._add_options()
        (options, args) = self.parser.parse_args()
        
        if len(args) != 0:
            self.parser.print_help()
            sys.exit(1)
        
        self.frame = frame
        self.panel = panel
        
        self.rxtuner = None
        self.usrp_rate = None
        
        # build graph
        
        #TODO: target decim
        self.rxtuner = myRx.RxTuner(
            number_channels = 1,
            rx_decim = 128, 
            gains = [options.gain],
            frequencies = [options.freq],
            board = options.rx_subdev_spec,
            drop_I = False,
            drop_Q = False,
            target_sample_rate = options.target_sample_rate,
            file_source_name = options.source_file,
            repeat = options.source_file_repeat
            )
        
        to_connect = self.rxtuner.connect_these()
        if to_connect:
            self.connect(*to_connect)

        self.usrp_rate = self.rxtuner.rx_sampling_rate
        chanfilt_decim = 4
        self.chanfilt_rate = self.rxtuner.rx_sampling_rate / chanfilt_decim
        
        print "usrp_rate: %s" % self.usrp_rate
        print "chanfilt_rate: %s" % self.chanfilt_rate
        
        self.lpf_cutofffreq = 48e3
        self.lpf_trans = 4e3
        lpfcoeffs = gr.firdes.low_pass(1, self.usrp_rate, self.lpf_cutofffreq, self.lpf_trans)
        self.lpf = gr.fir_filter_ccf(chanfilt_decim, lpfcoeffs)
        
        
        self._samples_per_symbol=options.samples_per_symbol
        self._excess_bw=_def_excess_bw
        self._costas_alpha=_def_costas_alpha
        self._mm_gain_mu=_def_gain_mu
        self._mm_mu=_def_mu
        self._mm_omega_relative_limit=_def_omega_relative_limit
        self._gray_code=_def_gray_code
        
        if self._samples_per_symbol < 2:
            raise TypeError, "samples_per_symbol must be >= 2, is %r" % (self._samples_per_symbol,)
        
        self.bits_per_symbol = 1

        arity = pow(2,self.bits_per_symbol)

        # Automatic gain control
        scale = (1.0/16384.0)
        self.pre_scaler = gr.multiply_const_cc(scale)   # scale the signal from full-range to +-1
        self.agc = gr.feedforward_agc_cc(16, 2.0)

        # RRC data filter
        ntaps = 11 * self._samples_per_symbol
        self.rrc_taps = gr.firdes.root_raised_cosine(
            1.0,                      # gain
            self._samples_per_symbol, # sampling rate
            1.0,                      # symbol rate
            self._excess_bw,          # excess bandwidth (roll-off factor)
            ntaps)
        self.rrc_filter=gr.interp_fir_filter_ccf(1, self.rrc_taps)        

        # symbol clock recovery
        if not self._mm_gain_mu:
            self._mm_gain_mu = 0.1
            
        self._mm_omega = self._samples_per_symbol
        self._mm_gain_omega = .25 * self._mm_gain_mu * self._mm_gain_mu
        self._costas_beta  = 0.25 * self._costas_alpha * self._costas_alpha
        fmin = -0.025
        fmax = 0.025
        
        self.receiver=gr.mpsk_receiver_cc(arity, 0,
                                         self._costas_alpha, self._costas_beta,
                                         fmin, fmax,
                                         self._mm_mu, self._mm_gain_mu,
                                         self._mm_omega, self._mm_gain_omega,
                                         self._mm_omega_relative_limit)
        
        # Do differential decoding based on phase change of symbols
        self.diffdec = gr.diff_phasor_cc()

        # find closest constellation point
        rot = 1
        rotated_const = map(lambda pt: pt * rot, psk.constellation[arity])
        self.slicer = gr.constellation_decoder_cb(rotated_const, range(arity))

        if self._gray_code:
            self.symbol_mapper = gr.map_bb(psk.gray_to_binary[arity])
        else:
            self.symbol_mapper = gr.map_bb(psk.ungray_to_binary[arity])
        
        # unpack the k bit vector into a stream of bits
        self.unpack = gr.unpack_k_bits_bb(self.bits_per_symbol)
        
        # Connect
        self.connect(self.rxtuner.get_rx(), self.lpf, self.pre_scaler, self.agc,
                     self.rrc_filter, self.receiver, self.diffdec,
                     self.slicer, self.symbol_mapper, self.unpack, 
                     gr.char_to_float(),gr.add_const_ff(48),gr.float_to_char(),
                     gr.file_sink(gr.sizeof_char, options.data_destination_file)
                     )
        if verbose:
                self._print_verbage()
        if logging:
                self._setup_logging()

        # Debug
        self.c2r = gr.complex_to_real()
        self.c2i = gr.complex_to_imag()
        self.c2f = gr.char_to_float()
        self.connect(self.receiver, self.c2r)
        self.connect(self.receiver, self.c2i)
        self.connect(self.slicer, self.c2f)
        #self.connect(self.c2r, gr.file_sink(gr.sizeof_float, 'PSKrecording.raw'))

        
        self._build_gui(vbox)
        self.update_status_bar()
        #if abs(options.freq) < 1e6:
        #    options.freq *= 1e6
        
        if not(self.set_freq(options.freq)):
            self._set_status_msg("Failed to set initial frequency")
        
        self.set_lpf_trans(self.lpf_trans)
        
        # set initial values
        self.set_gain(options.gain)
        
        print 'initialization done'


    def _set_status_msg(self, msg, which=0):
        self.frame.GetStatusBar().SetStatusText(msg, which)

    def _build_gui(self, vbox):

        
        # Scope
        self.scope = scopesink.scope_sink_f(self, self.panel,
                                             title="Data from Sensor",
                                             v_scale = 0.5,
                                             t_scale = 250e-6,
                                             sample_rate=self.chanfilt_rate)
        self.connect(self.c2r, (self.scope, 0))
        self.connect(self.c2i, (self.scope, 1))
        #self.connect(self.c2f, (self.scope, 2))
        self.connect(self.c2f, gr.null_sink(gr.sizeof_float))
        vbox.Add(self.scope.win, 1, wx.EXPAND)

        # control area form at bottom
        self.myform = myform = form.form()
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        def _form_set_freq(kv): return self.set_freq(kv['freq'])
        myform['freq'] = form.float_field(
            parent=self.panel, sizer=hbox, label="Carrier Freq", weight=1,
            callback=myform.check_input_and_call(_form_set_freq, self._set_status_msg))

        hbox.Add((5,0), 0)
        myform['freq_slider'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox, weight=3,
                                        range=(0, 500e3, 1e3),
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
        def _form_set_lpf_trans(kv): return self.set_lpf_trans(kv['lpf_trans'])
        myform['lpf_trans'] = form.float_field(
            parent=self.panel, sizer=hbox, label="Cutoff trans freq", weight=1,
            callback=myform.check_input_and_call(_form_set_lpf_trans, self._set_status_msg))

        hbox.Add((5,0), 0)
        myform['lpf_cutoff_slider'] = \
            form.quantized_slider_field(parent=self.panel, label="cut freq",sizer=hbox, weight=3,
                                        range=(1e3, self.chanfilt_rate/2, 1e3),
                                        callback=self.set_lpf_cutofffreq)     
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
            self.myform['freq'].set_value(target_freq)         # update displayed value
            self.myform['freq_slider'].set_value(target_freq)  # update displayed value
            self.update_status_bar()
            self._set_status_msg("OK", 0)
            return True

        self._set_status_msg("Failed", 0)
        return False
    
    def _update_lpf(self):
        lpfcoeffs = gr.firdes.low_pass(1, self.usrp_rate, self.lpf_cutofffreq, self.lpf_trans)
        self.lpf.set_taps(lpfcoeffs)
        self.update_status_bar()
        self._set_status_msg("OK", 0)

    def set_lpf_cutofffreq(self, cut):
        self.lpf_cutofffreq = cut
        self.myform['lpf_cutoff_slider'].set_value(cut)         # update displayed value
        self._update_lpf()
  
    def set_lpf_trans(self, trans):
        self.lpf_trans = trans     
        self.myform['lpf_trans'].set_value(trans) 
        self._update_lpf()

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
        msg = "Gain:%r lpfcut:%.0f lpftrans:%.0f" % (self.rxtuner.gains[0],self.lpf_cutofffreq,self.lpf_trans)
        self._set_status_msg(msg, 1)

    def _print_verbage(self):
        print "\nDemodulator:"
        print "bits per symbol:     %d"   % self.bits_per_symbol
        print "Gray code:           %s"   % self._gray_code
        print "RRC roll-off factor: %.2f" % self._excess_bw
        print "Costas Loop alpha:   %.2e" % self._costas_alpha
        print "Costas Loop beta:    %.2e" % self._costas_beta
        print "M&M mu:              %.2f" % self._mm_mu
        print "M&M mu gain:         %.2e" % self._mm_gain_mu
        print "M&M omega:           %.2f" % self._mm_omega
        print "M&M omega gain:      %.2e" % self._mm_gain_omega
        print "M&M omega limit:     %.2f" % self._mm_omega_relative_limit

    def _setup_logging(self):
        print "Modulation logging turned on."
        self.connect(self.pre_scaler,
                     gr.file_sink(gr.sizeof_gr_complex, "rx_prescaler.raw"))
        self.connect(self.agc,
                     gr.file_sink(gr.sizeof_gr_complex, "rx_agc.raw"))
        self.connect(self.rrc_filter,
                     gr.file_sink(gr.sizeof_gr_complex, "rx_rrc_filter.raw"))
        self.connect(self.receiver,
                     gr.file_sink(gr.sizeof_gr_complex, "rx_receiver.raw"))
        #self.connect(self.diffdec,
        #             gr.file_sink(gr.sizeof_gr_complex, "rx_diffdec.raw"))        
        #self.connect(self.slicer,
        #             gr.file_sink(gr.sizeof_char, "rx_slicer.raw"))
        #self.connect(self.symbol_mapper,
        #             gr.file_sink(gr.sizeof_char, "rx_symbol_mapper.raw"))
        #self.connect(self.unpack,
        #             gr.file_sink(gr.sizeof_char, "rx_unpack.raw"))

    def _add_options(self):
        parser = self.parser
        parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=None,
                          help="select USRP Rx side A or B (default=A)")
        parser.add_option("-f", "--freq", type="eng_float", default=125e3,
                          help="set frequency to FREQ", metavar="FREQ")
        parser.add_option("-g", "--gain", type="int", default=10,
                          help="set gain in dB (default is midpoint)")
        # Adds DBPSK demodulation-specific options to the standard parser
        parser.add_option("", "--excess-bw", type="float", default=_def_excess_bw,
                          help="set RRC excess bandwith factor [default=%default] (PSK)")
        parser.add_option("", "--no-gray-code", dest="gray_code",
                          action="store_false", default=_def_gray_code,
                          help="disable gray coding on modulated bits (PSK)")
        parser.add_option("", "--costas-alpha", type="float", default=None,
                          help="set Costas loop alpha value [default=%default] (PSK)")
        parser.add_option("", "--gain-mu", type="float", default=_def_gain_mu,
                          help="set M&M symbol sync loop gain mu value [default=%default] (GMSK/PSK)")
        parser.add_option("", "--mu", type="float", default=_def_mu,
                          help="set M&M symbol sync loop mu value [default=%default] (GMSK/PSK)")
        parser.add_option("", "--omega-relative-limit", type="float", default=_def_omega_relative_limit,
                          help="M&M clock recovery omega relative limit [default=%default] (GMSK/PSK)")
        parser.add_option("", "--samples-per-symbol", type="int", default=_def_samples_per_symbol,
                          help="Samples per symbol (how many samples there are in each symbol)")
        
        parser.add_option("","--data-destination-file",default = 'PSKrecording.b',help="filename for demodulated data. default = 'PSKrecording.b'")
        
        parser.add_option("-S","--target-sample-rate",
                          type = "eng_float",
                          default = None,
                          help="Try to decimate the samplerate near this."
                          )

        parser.add_option("", "--source-file", default=None,
                          help="set rx to come from this file.")

        parser.add_option("", "--source-file-repeat", default=False,
                          action='store_true',
                          help="is the file repeated. default %default")


if __name__ == '__main__':
    app = stdgui.stdapp (psk_demod_demo_graph, "psk demod demo")
    app.MainLoop ()



