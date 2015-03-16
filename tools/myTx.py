#!/usr/bin/env python2.5

from gnuradio import gr

from gnuradio import gru
from gnuradio import usrp
#from gnuradio import alibaba

from usrpm import usrp_dbid


class TxTuner:
    def __init__(
        self,
        targetsamplerate,
        usedmixingfreq,
        gain = 1
        ):
        
        self.usedmixingfreq = usedmixingfreq
        self.gain = gain
        """TODO: fix the chicken egg problem here. setinterpolate or smth"""
        self.hw_tx_sample_rate =  128e6
        
        if self.hw_tx_sample_rate % targetsamplerate != 0:
            print 'HOX!:  self.hw_tx_sample_rate % targetsamplerate ==', self.hw_tx_sample_rate % targetsamplerate
            
        #self.sendinterpolate =  int(self.hw_tx_sample_rate / targetsamplerate)
        #todo: optimize
        _, self.sendinterpolate = min( 
            [(abs(targetsamplerate - self.hw_tx_sample_rate / float(inter)), inter) for inter in range(4,513) if inter % 4 == 0]
            )
        
            
        
        #not used to set a thing
        self.tx_sampling_rate = self.hw_tx_sample_rate / self.sendinterpolate
        
        print "interpolation (anti decimation)", self.sendinterpolate
        print "targetsamplerate", targetsamplerate
        print "self.tx_sampling_rate", self.tx_sampling_rate
        
        #Todo: get the used board like it should be done
        self.tx = usrp.sink_c (0, self.sendinterpolate)
        #Todo: get the used board like it should be done ..
        self.tx_subdev = usrp.selected_subdev(self.tx, (0,0))
        #TODO: different channels
        self.tx.tune(0, self.tx_subdev, self.usedmixingfreq)
        self.tx.set_pga(0, self.gain)
        self.got_hw_tx_sample_rate = self.tx.dac_rate()
        if self.got_hw_tx_sample_rate != self.hw_tx_sample_rate:
            raise SyntaxError('fix the hardcoded value of self.hw_tx_sample_rate to %s'%self.got_hw_tx_sample_rate)
        """
        
        Set output mux configuration.
        
     3                   2                   1                       
   1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
  +-------------------------------+-------+-------+-------+-------+
  |                               | DAC3  | DAC2  | DAC1  |  DAC0 |
  +-------------------------------+-------+-------+-------+-------+

  There are two interpolators with complex inputs and outputs.
  There are four DACs.

  Each 4-bit DACx field specifies the source for the DAC and
  whether or not that DAC is enabled.  Each subfield is coded
  like this:

     3 2 1 0
    +-+-----+
    |E|  N  |
    +-+-----+

  Where E is set if the DAC is enabled, and N specifies which
  interpolator output is connected to this DAC.

   N   which interp output
  ---  -------------------
   0   chan 0 I
   1   chan 0 Q
   2   chan 1 I
   3   chan 1 Q

   1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0 9 8 7 6 5 4 3 2 1 0
  +-------------------------------+-------+-------+-------+-------+
                                   1       1       1     1 1      
   ----------------------------------------------------------------

   == 0x98
 """
        self.tx.set_mux(gru.hexint(0x98))
        
        
    def get_tx(self):
        return self.tx
