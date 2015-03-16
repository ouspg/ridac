#!/usr/bin/env python2.5

from gnuradio import gr, gru, eng_notation, optfir, modulation_utils, blks2
from gnuradio import usrp
from gnuradio import blks
from gnuradio import alibaba
from gnuradio.eng_option import eng_option
from gnuradio.wxgui import slider, powermate
from gnuradio.wxgui import stdgui, form, fftsink, waterfallsink, scopesink
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
        parser.add_option("-f", "--freq", type="eng_float", default=125e3,
                          help="set frequency to FREQ. default %default", metavar="FREQ")
        parser.add_option("-T","--target-sample-rate", 
                          type = "int", 
                          default = int(64e6 / 128.),
                          help="sample rate from rx. default %default")
        parser.add_option("-g", "--gain", type="int", default=10,
                          help="set gain in dB (default is midpoint)")

        parser.add_option("", "--source-file", default=None,
                          help="set rx to come from this file.")

        parser.add_option("-F", "--recorded-file", default=None,
                          help="directs recording to this file if set.")
        
        parser.add_option("", "--source-file-repeat", default=False,
                          action='store_true',
                          help="is the file repeated. default %default")

        parser.add_option("-S","--file-sample-rate", 
                          type = "int", 
                          default = 8e6,
                          help="sample rate of the recorded file. default %default"
                          )
        parser.add_option("-c",
                          "--cutoff-freq",
                          type = "float",
                          default = 10e3,
                          help = "")
                          

        (options, args) = parser.parse_args()
        
        if len(args) != 0:
            parser.print_help()
            sys.exit(1)
        
        self.frame = frame
        self.panel = panel
        
        self.vol = 0
        self.state = "FREQ"
        self.freq = 125e3

        self.rxtuner = None
        self.usrp_rate = None

        
        self.rxtuner = myRx.RxTuner(
            number_channels = 1,
            target_sample_rate = options.target_sample_rate,
            gains = [options.gain],
            frequencies = [options.freq],
            board = options.rx_subdev_spec,
            file_source_name = options.source_file,
            repeat = options.source_file_repeat
            )
        
        to_connect = self.rxtuner.connect_these()
        if to_connect:
            self.connect(*to_connect)
        
        self.usrp_rate = self.rxtuner.rx_sampling_rate
        chanfilt_decim = 2 #fixthis
        
        #chanfilt_decim = 512
        print "usrp_rate: %s" % self.usrp_rate
        demod_rate = None
        
        # Channelize the signal (bandpass freq+fc)
        fc = -64.25e3
        bw = 32e3
        trans = 4e3
        bpfcoeffs = gr.firdes.complex_band_pass(10, self.usrp_rate, fc-bw/2,
                                                fc+bw/2, trans)
        self.bpf =  gr.fir_filter_ccc(1, bpfcoeffs)
        self.c2r = gr.complex_to_real()
        self.square = gr.multiply_ff()
        
        #slider callback uses this one 
        self.lowpasscut = options.cutoff_freq#10e3
        self.lowpasstrans = 4e3
        self.lpfcoeffs = gr.firdes.low_pass(1, self.usrp_rate, self.lowpasscut,
                                            self.lowpasstrans)
        self.lpf =  gr.fir_filter_fff (1, self.lpfcoeffs)
        
        self.null = gr.null_sink(gr.sizeof_float)
        self.connect(self.rxtuner.get_rx(), self.bpf, self.c2r)
        self.connect(self.c2r, (self.square,0))
        self.connect(self.c2r, (self.square,1))
        self.connect(self.square, self.lpf, self.null)

        if options.recorded_file != None:
            self.connect(self.lpf, gr.file_sink(gr.sizeof_float, options.recorded_file))
        
        self.source = self.lpf
        
        
        self._build_gui(vbox, demod_rate)
        
        #if abs(options.freq) < 1e6:
        #    options.freq *= 1e6
        
        if not(self.set_freq(options.freq)):
            self._set_status_msg("Failed to set initial frequency")
        
        # set initial values
        self.set_gain(options.gain)
        self.set_lowpasscut(self.lowpasscut)
        
        print 'initialization done'


    def _set_status_msg(self, msg, which=0):
        self.frame.GetStatusBar().SetStatusText(msg, which)

    def _build_gui(self, vbox, demod_rate):

        def _form_set_freq(kv):
            return self.set_freq(kv['freq'])
        source = self.source
        if plot1:
            self.scope = scopesink.scope_sink_f (
                self, self.panel, title="Data from Sensor",
                sample_rate= self.usrp_rate,
                size=(512,100))
            self.connect (source, self.scope)
            vbox.Add (self.scope.win, 1, wx.EXPAND)

        if plot2:
            self.src_fft = fftsink.fft_sink_f (
                self, self.panel, title="Frequency/amplitude",
                sample_rate= self.usrp_rate,
                fft_size=1024,
                fft_rate=15,
                size=(512,200))
            print self.src_fft.fft_size
            self.connect (self.lpf, self.src_fft)
            vbox.Add (self.src_fft.win, 1, wx.EXPAND)

        # control area form at bottom
        self.myform = myform = form.form()
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        myform['freq'] = form.float_field(
            parent=self.panel, sizer=hbox, label="Carrier Freq", weight=1,
            callback=myform.check_input_and_call(_form_set_freq,
                                                 self._set_status_msg))

        hbox.Add((5,0), 0)
        myform['freq_slider'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox, weight=3,
                                        range=(0, 500e3, 0.001e6),
                                        callback=self.set_freq)
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        
        myform['gain'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox,
                                        label="Gain", weight=3,
                                        range=self.rxtuner.gain_range,
                                        callback=self.set_gain)
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        
        myform['lowpasscut'] = \
            form.quantized_slider_field(parent=self.panel, sizer=hbox,
                                        label="Lowpass cut", weight=3,
                                        range=(0,51e3, 1e3),
                                        callback=self.set_lowpasscut)
        
        hbox.Add((5,0), 0)
        vbox.Add(hbox, 0, wx.EXPAND)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((5,0), 0)
        
        print 'GUI done'

    def set_volume(self, target_volume):
        self.volume_control.set_k( target_volume)
        result = self.volume_control.k()
        self.myform['volume_slider'].set_value(result)  # update displayed value
        self.update_status_bar()
        self._set_status_msg("OK", 0)
        return True
            
    def on_button (self, event):
        if event.value == 0:        # button up
            return
        self.rot = 0
        if self.state == "FREQ":
            self.state = "GAIN"
        else:
            self.state = "FREQ"
        self.update_status_bar ()
        
                                        
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
            self.myform['freq'].set_value(target_freq)
            self.myform['freq_slider'].set_value(target_freq)
            self.update_status_bar()
            self._set_status_msg("OK", 0)
            return True

        self._set_status_msg("Failed", 0)
        return False

    def set_lowpasscut(self, cut):
        
        try:
            newlpfcoeffs = gr.firdes.low_pass(1, self.usrp_rate, cut,
                                              self.lowpasstrans)        
            self.lpf.set_taps(newlpfcoeffs)
        except Exception, e:
            print type(e), e
            newlpfcoeffs = self.lpfcoeffs
            cut = self.lowpasscut
            self.lpf.set_taps(newlpfcoeffs)
            pass

        self.lowpasscut = cut
        self.lpfcoeffs = newlpfcoeffs

        self.update_status_bar()


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
        msg = "Gain:%r  Setting:%s cut:%s" % (self.rxtuner.gains[0],
                                              self.state,
                                              self.lowpasscut)
        self._set_status_msg(msg, 1)
        if plot1: pass
        #self.src_water.set_baseband_freq(self.freq)
        if plot2: 
            self.src_fft.set_baseband_freq(self.freq)

    
if __name__ == '__main__':
    app = stdgui.stdapp (am_plasma_rx_graph, "PPM demodulation demo")
    app.MainLoop ()



