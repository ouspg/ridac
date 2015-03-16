#!/usr/bin/env python2.5

from gnuradio import gr
from gnuradio import gru
from gnuradio import usrp
#from gnuradio import alibaba

from usrpm import usrp_dbid

import sys




class RxTuner:
    """
    It would be stupid to do all this in every tool.
    """
    def __init__(
        self,
        number_channels = None,
        rx_decim = None,
        gains = None,
        frequencies = None,
        board = None,
        drop_Q = False,
        drop_I = False,
        target_sample_rate = None,
        file_source_name=None,
        repeat = False):
        """
        number_of_channels : currently 1 is tested enough.
        rx_decim, target_sample_rate both are for same thing. target_sample_rate overrides
        board: the used daughter board
        drop_I, drop_Q are for mux. juast sets the other one zero
        gains and frequencies are lists of gains and frequencies. one element for each channel
        """
        

        """Some constants (in our environment):"""
        """
        param subdev_spec: return value from subdev option parser.  
        type  subdev_spec: (side, subdev), where side is 0 or 1 and subdev is 0 or 1
        """

        """ the sampling rate of the rx module before downsampling"""
        #self.hw_sampling_rate = 64e6

        
        """set these parameters"""
        self.number_channels = number_channels
        """how many samples are 'skipped'(-1) in the downsampling"""
        self.rx_decim = rx_decim
        self.gains = gains
        self.frequencies = frequencies
        self.board = board
        self.drop_Q = drop_Q
        self.drop_I = drop_I 
        """if set, find the best rx_decim automatically"""
        self.target_sample_rate = target_sample_rate
        
        self.file_source_name = file_source_name
        self.repeat = repeat

        
        """these are set by setvalues. DO NOT SET THESE BY YOURSELF, please."""
        self.to_connect= []
        self.subdev_spec = None 
        self.rx_sampling_rate = None
        self.filesource = None

        self.rx = None
        self.rx_subdev = None
        self.muxsettings = None
        self.hw_sampling_rate = None
        self.freq_tune_infos = None
        self.gain_range = None

        self.setvalues()

    def connect_these(self):
        """ ui done using flowgraph, which does not work with hierblocks"""
        return self.to_connect

    def get_rx(self):
        return self.rx

    def get_rx_subdev(self,):
        return self.rx_subdev

    def get_gain_range(self):
        return self.gain_range

    def set_freq(self, nmbr,freq):
        """ remember to call the right tune"""
        self.frequencies[nmbr] = freq

    def set_gain(self, nmbr,gain):
        """ remember to call the right tune"""
        self.gains[nmbr] = gain
    
    def set_decim(self, decim):
        if self.rx.set_decim_rate(decim):
            self.rx_decim = decim
            return True
        return False

    def validate(self):
        if self.gains != None and len(self.gains) != self.number_channels:
            raise ValueError(
                "self.gains != None and len(self.gains) != self.number_channels: %s"%str(
                    self.gains))
                
        #if self.target_sample_rate != None and self.rx_decim != None:
        #    raise ValueError('self.target_samplerate and self.rx_decim both set')
        
        if self.target_sample_rate == None and self.rx_decim == None:
            raise ValueError('self.target_samplerate and self.rx_decim both None')
        
        if self.frequencies == None:
            raise ValueError("self.frequencies was None")
        
        
        if self.number_channels not in [1,2,4]:
            raise ValueError(
                "self.number_channels %s not in [1,2,4]"%str(self.number_channels))
        
        if len(self.frequencies) != self.number_channels:
            raise ValueError(
                "len(self.frequencies) != self.number_channels: %s vs. %s"%(
                    str(len(self.frequencies)),
                    str(self.number_channels)))
        
        if self.board not in [usrp_dbid.TV_RX,usrp_dbid.TV_RX_REV_2,usrp_dbid.BASIC_RX, None]:
            raise  ValueError(
                "self.board not in [usrp_dbid.TV_RX,usrp_dbid.TV_RX_REV_2,usrp_dbid.BASIC_RX, None]: %s"%str(self.board))
        
        if self.file_source_name != None and type(self.file_source_name) != type(""):
            raise  ValueError('file_source_name should be none or string')
        
        if  self.file_source_name != None and self.target_sample_rate == None:
            raise ValueError('file source (target) samplerate was not given')
        
    def tune_freq(self):
        """ if source is a file, frequencies can be anything"""
        if self.file_source_name != None:
            return self.frequencies
        """
from http://www.mail-archive.com/discuss-gnuradio@gnu.org/msg04956.html:

Also, the return value from tune is an instance of tune_result which
can be examined to see how everything was setup.  baseband_freq is the
RF frequency that corresponds to DC in the RF front-end's IF output
(the input to the A/D's and from there to the digital down-converter).
Note that this isn't necessarily the location of the signal of
interest.  Some daughterboards have the signal of interest at a
non-zero IF frequency.  dxc_freq is the frequency value used in the
digital down or up converter.  residual_freq is a very small number on
the order of 1/100 of a Hz.  It can be ignored.  Inverted is true if
the spectrum is inverted, and we weren't able to fix it for you.

On the receive path, the end result of tune is that the signal at the
given target RF frequency ends up at DC in the complex baseband input
from the USRP.
"""
        self.freq_tune_infos = []
        setfreqs = []
        for i, freq in enumerate(self.frequencies):
            r = self.rx.tune(i, self.rx_subdev, freq)
            self.freq_tune_infos.append(r)
            if r:
                r = - r.dxc_freq
                self.frequencies[i] = r
            setfreqs.append(r)
            #print 'baseband_freq',r.baseband_freq
            #print 'dxc_freq',r.dxc_freq 
            #print 'inverted',r.inverted 
            #print 'residual_freq', r.residual_freq

        return setfreqs


    def tune_gains(self):
        if self.file_source_name != None:
            return self.gains
                
        """
Help on method set_pga in module gnuradio.usrp1:

set_pga(*args) method of gnuradio.usrp1.usrp1_source_c_sptr instance
    set_pga(self, int which, double gain_in_db) -> bool

"""
        success = []
        for i, g in enumerate(self.gains):
            if self.rx.set_pga(i, int(g+0.5)):
                self.gains[i] = self.rx.pga(i)
                success.append( self.gains[i] )
            else:
                success.append(None)

        return success


    def setvalues(self):
        self.validate()
        
        if self.file_source_name != None:
            print 'file source'
            self.filesource =  gr.file_source(
                gr.sizeof_gr_complex, 
                self.file_source_name, 
                self.repeat)



            self.subdev_spec = 'file source' 
            self.rx_sampling_rate = self.target_sample_rate

            self.rx = gr.throttle(gr.sizeof_gr_complex, self.rx_sampling_rate)
            
            self.to_connect.append(self.filesource)
            self.to_connect.append(self.rx)

            
            self.rx_subdev = 'file source' 
            self.muxsettings = 'file source' 
            self.hw_sampling_rate = 1
            self.freq_tune_infos = None
            self.gain_range = (0.0, 20.0, 1.0)
            # if no gain was specified, use the mid-point in dB            
            if self.gains == None:
                g = self.get_gain_range()
                self.gains = [float(g[0]+g[1])/2]*self.number_channels
            if None in self.gains:
                g = self.get_gain_range()
                midpoint = float(g[0]+g[1])/2
                self.gains = [i if i!= None else midpoint for i in self.gains]
            return
        """Gnuradio 3.1.2:
>>> from gnuradio import usrp
>>> rx = usrp.source_c(decim_rate=4, nchan=1)
>>> dir(rx)
['__class__', '__del__', '__delattr__', '__dict__', '__doc__', '__getattr__', '__getattribute__', '__hash__', '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__str__', '__weakref__', '_fpga_caps', '_u', 'db', 'has_rx_halfband', 'has_tx_halfband', 'nddc', 'nduc', 'tune']
"""

        """
        in gnuradio 3.1.2:
        __init__(
        self, which=0, 
        decim_rate=64, nchan=1, 
        mux=839922192, mode=0, 
        fusb_block_size=0, fusb_nblocks=0, 
        fpga_filename='', firmware_filename='')
        """
        
        """set the decim before creating the source. see the chicken egg problem here:
        you have to know the valid values before setting em or try something like:
        while exception: { try: ... except: ... }  
        so this is more or less hard coded for now"""
        
        if self.target_sample_rate != None:
            _decims = [
                (abs(64e6/_decim - self.target_sample_rate), 
                 _decim ) for _decim in range(4,257) if _decim % 2 == 0]
            _, self.rx_decim = min(_decims) 
        self.rx_decim = int(self.rx_decim)
        self.rx = usrp.source_c(decim_rate=self.rx_decim, nchan=self.number_channels)
        
        self.subdev_spec = self.board
        
        if self.board == None:
            self.subdev_spec = usrp.pick_subdev(
                self.rx, 
                (usrp_dbid.TV_RX,usrp_dbid.TV_RX_REV_2,usrp_dbid.BASIC_RX)
                )
            
        self.hw_sampling_rate = self.rx.adc_rate()

        
        """
selected_subdev(u, subdev_spec)
    Return the user specified daughterboard subdevice.
    
    @param u: an instance of usrp.source_* or usrp.sink_*
    @param subdev_spec: return value from subdev option parser.  
    @type  subdev_spec: (side, subdev), where side is 0 or 1 and subdev is 0 or 1
    @returns: an weakref to an instance derived from db_base
    """

        self.rx_subdev = usrp.selected_subdev(self.rx, self.subdev_spec)
        
        self.rx_sampling_rate = self.hw_sampling_rate/self.rx_decim
        print 'self.rx_sampling_rate', self.rx_sampling_rate
        
        self.gain_range = self.rx_subdev.gain_range()
        
        if self.gains == None:
            # if no gain was specified, use the mid-point in dB
            g = self.get_gain_range()
            self.gains = [float(g[0]+g[1])/2]*self.number_channels
        if None in self.gains:
            g = self.get_gain_range()
            midpoint = float(g[0]+g[1])/2
            self.gains = [i if i!= None else midpoint for i in self.gains]

                
            
        #TODO: mode

        """Set input mux configuration.
This determines which ADC (or constant zero) is connected to each DDC input. There are 4 DDCs. Each has two inputs.

 Mux value:

    3                   2                   1                       
  1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
 +-------+-------+-------+-------+-------+-------+-------+-------+
 |   Q3  |   I3  |   Q2  |   I2  |   Q1  |   I1  |   Q0  |   I0  |
 +-------+-------+-------+-------+-------+-------+-------+-------+

 Each 4-bit I field is either 0,1,2,3
 Each 4-bit Q field is either 0,1,2,3 or 0xf (input is const zero)
 All Q's must be 0xf or none of them may be 0xf

default value:
 hex(839922192) = 0x32103210 = 0011 0010 0001 0000 0011 0010 0001 0000 bin 
"""
        self.muxsettings =      0x32103210
        if self.drop_Q:
            self.muxsettings &= 0x0f0f0f0f
        if self.drop_I:
            self.muxsettings &= 0xf0f0f0f0
        self.rx.set_mux(gru.hexint(self.muxsettings))
        
        #TODO: check the return values
        self.tune_freq()
        self.tune_gains()

