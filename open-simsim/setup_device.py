from gnuradio import gr
from gnuradio import gru
from gnuradio import usrp
from gnuradio import alibaba
import sys


class configurator:
    def __init__(self):
        
        self.rx_nchan=0
        self.tx_nchan=0
        self.rx_interp=0
        self.tx_interp=0
        self.rx_gain=0
        self.tx_gain=0
        self.rx_if_freq=0
        self.tx_if_freq=0
        self.transmit_freq=0
        self.tx_amplitude=0
        self.dst_file=""
        
        self.source_file=""
        self.cycles_per_symbol=0

        self.buffer_file_suffix = ""
        self.buffer_file_count = 0
        
        self.repeats_per_key = 0
        self.keys_in_buffer = 0

        
        
        self.freq_one=0
        self.freq_zero=0
        
        
        self.dst_file_reader=""
        self.rx_if_freq_2=0
        self.block_sep_val=0
        self.char_block_sep_val_miller=0
        self.char_block_sep_val_manchester=0
        self.data_rate=0
        
        self.blocksplitter_offset_channel_one=0
        self.blocksplitter_offset_channel_two=0
        #self.blocksplitter_how_many_zeros = 0
        
        self.normalizer_value=0
        self.check_crc=False
        self.check_parity=False
        self.manchester_offset_channel_one=0
        self.miller_offset_channel_one=0
        self.manchester_offset_channel_two=0
        self.miller_offset_channel_two=0
        self.output_channel_one=0
        self.output_channel_two=0

        self.lowpass_cutoff_channel_one=0
        self.lowpass_transition_width_channel_one=0
        self.lowpass_cutoff_channel_two=0
        self.lowpass_transition_width_channel_two=0
        


class my_top_block(gr.top_block):
    def __init__ (self):
        gr.top_block.__init__(self)
        
        self.tx_sampling_rate=0
        self.rx_sampling_rate=0
        
        #generate a int*. It is used as a shared data object between two signal processing blocks.
        self.send_state=alibaba.new_intp()
        alibaba.intp_assign(self.send_state,0)

            
    def setup_sender(self, number_channels, tx_interp, tx_gain, tune_frequency):
        #64 Mhz is the frequency of the ADC, reduced by the decimation of the DDC
    
        
        #the DAC in the transmit path is operated with 128MhZ. Samples are interpolated according to the interp- variable.
        self.tx_sampling_rate=128e6/tx_interp
        # get USRP transmitter
        self.tx = usrp.sink_c (0, tx_interp)
        self.tx_subdev = usrp.selected_subdev(self.tx, (0,0))
        self.tx.tune(0, self.tx_subdev, tune_frequency)
        self.tx.set_pga(0,tx_gain)
        self.tx.set_mux(gru.hexint(0x98))
        
        
    def setup_receiver(self,  number_channels, rx_interp, rx_gain, tune_frequency_channel_one, tune_frequency_channel_two):
        self.rx_sampling_rate=64e6/rx_interp
        self.rx = usrp.source_c(decim_rate=rx_interp, nchan=number_channels)
        self.rx_subdev = usrp.selected_subdev(self.rx, (0,0))
        self.rx.tune(0, self.rx_subdev, tune_frequency_channel_one)
        if number_channels == 2:
            self.rx.tune(1, self.rx_subdev, tune_frequency_channel_two)
        
        self.rx.set_pga(0,rx_gain)
        self.rx.set_mux(gru.hexint(0xf0f0f0f0))
        
    def generate_file_sink(self, size, dst_filename):
        #generate signal source and receive sink (head is used to reduce the number of samples)
        sink = gr.file_sink(size, dst_filename)
        return sink
    
    def generate_file_source(self,size, filename, repeat):
        src = gr.file_source(size, filename,repeat)
        return src
    
    def generate_signal_source(self, waveform, frequency, amplitude):
        siggen = gr.sig_source_c (self.tx_sampling_rate,waveform,frequency,amplitude,0)
        return siggen
        

class my_top_block_125(my_top_block):
    def __init__ (self, config):
        my_top_block.__init__(self)
        

        
        self.tx_freqency= config.transmit_freq
        self.frequency_one=config.freq_one
        self.frequency_zero=config.freq_zero
        
        self.dst= self.generate_file_sink(gr.sizeof_char, config.dst_file)
        
        self.setup_sender(config.tx_nchan, config.tx_interp, config.tx_gain, config.tx_if_freq)
        self.setup_receiver(config.rx_nchan, config.rx_interp, config.rx_gain, config.rx_if_freq,0)
        
        self.siggen= self.generate_signal_source(gr.GR_SIN_WAVE,self.tx_freqency,config.tx_amplitude)
        self.configure_graph()
        
        

        
    def configure_graph(self):
        
        if self.frequency_one > self.frequency_zero:
            highest_frequency=self.frequency_one
        else:
            highest_frequency=self.frequency_zero
            
        lowpass=gr.firdes.low_pass(1,self.rx_sampling_rate, highest_frequency*1.1, highest_frequency*1.2, gr.firdes.WIN_HAMMING)
        fir_low= gr.fir_filter_fff (1,lowpass)
        
        demodulator=alibaba.fsk_demodulator_fb(self.rx_sampling_rate,self.frequency_one,self.frequency_zero)
        
        symbol_combiner=alibaba.combine_symbols_bb(3,7)
        
        #create a vector with the start sequence of the ID
        start_sequence = alibaba.CharVector(6)
        start_sequence[0]=0
        start_sequence[1]=0
        start_sequence[2]=0
        start_sequence[3]=1
        start_sequence[4]=1
        start_sequence[5]=1

        
        #this module will ensure, that an id is valid (id is found ten times)
        self.check=alibaba.checkid_bb(start_sequence, 1)
        
        #bring the vector in readable form...
        binarytocharconverter=alibaba.char_converter_bch()
        
        #convert the complex signal in a signal represented by float values
        floatconverter=gr.complex_to_float();
        
        #connect receive path
        self.connect(self.rx, floatconverter, fir_low,demodulator,symbol_combiner,self.check, binarytocharconverter, self.dst)

        #connect transmit path
        self.connect(self.siggen,self.tx)
        
        
        
class my_top_block_125_send(my_top_block):
    def __init__ (self,config):
        my_top_block.__init__(self)
        
        
        self.setup_sender(
            config.tx_nchan, config.tx_interp, 
            config.tx_gain,
            config.tx_if_freq)
        self.sigsource=alibaba.controlled_signalsource_bc(
            self.tx_sampling_rate, 
            config.freq_one,
            config.freq_zero, 
            config.tx_amplitude, 
            0,
            config.cycles_per_symbol)
        
        #instantiate and connect transmit path
        self.src = self.generate_file_source(gr.sizeof_char, config.source_file,True)
        
        self.connect(self.src, self.sigsource, self.tx)

        

class my_top_block_125_send_brute(my_top_block):
    def __init__ (self,config):
        my_top_block.__init__(self)
        
        self.setup_sender(
            config.tx_nchan, config.tx_interp, 
            config.tx_gain,
            config.tx_if_freq)
        self.sigsource=alibaba.controlled_signalsource_bc(
            self.tx_sampling_rate, 
            config.freq_one,
            config.freq_zero, 
            config.tx_amplitude, 
            0,
            config.cycles_per_symbol)
        
        self.repeater = alibaba.sequence_repeater_bb()
        self.repeater.set_repeat_count(config.repeats_per_key)
        self.repeater.set_sequence_length(96)
        
        
        self.bsuffix = config.buffer_file_suffix
       
        self.buffers = config.buffer_file_count

        self.keys_in_buffer = config.keys_in_buffer


        self.src = alibaba.file_ring_source(gr.sizeof_char)
        
        for fnam in self.yieldTmpFiles(False):
            self.src.append_filename(fnam)
            
        self.connect(self.src, self.repeater, self.sigsource, self.tx)

    def yieldTmpFiles(self, repeat = True):
        for i in (range(self.buffers)):
            yield "%d%s"%(i,self.bsuffix)
        while repeat:
            for i in (range(self.buffers)):
                yield "%d%s"%(i,self.bsuffix)
        
        
class my_top_block_1356(my_top_block):
    def __init__ (self, config):
        my_top_block.__init__(self)
        
        self.separation_value=config.block_sep_val
        self.separation_value_miller=config.char_block_sep_val_miller
        self.separation_value_manchester=config.char_block_sep_val_manchester
        self.data_rate=config.data_rate
        
        
        self.block_splitter_offset_channel_one=config.blocksplitter_offset_channel_one
        self.block_splitter_offset_channel_two=config.blocksplitter_offset_channel_two
        self.normalizer_value=config.normalizer_value
        self.check_crc=config.check_crc
        self.check_parity=config.check_parity
        self.manchester_offset_channel_one=config.manchester_offset_channel_one
        self.miller_offset_channel_one=config.miller_offset_channel_one
        self.manchester_offset_channel_two=config.manchester_offset_channel_two
        self.miller_offset_channel_two=config.miller_offset_channel_two
        self.output_channel_one=config.output_channel_one
        self.output_channel_two=config.output_channel_two

        self.lowpass_cutoff_channel_one=config.lowpass_cutoff_channel_one
        self.lowpass_transition_width_channel_one=config.lowpass_transition_width_channel_one
        self.lowpass_cutoff_channel_two=config.lowpass_cutoff_channel_two
        self.lowpass_transition_width_channel_two=config.lowpass_transition_width_channel_two
        
        self.setup_receiver(config.rx_nchan, config.rx_interp, config.rx_gain, config.rx_if_freq,config.rx_if_freq_2)
        #self.dst_data= self.generate_file_sink(gr.sizeof_float, config.dst_file)
        self.dst_data= self.generate_file_sink_hex(config.dst_file, self.separation_value_miller, self.separation_value_manchester, True)
        self.dst_reader=self.generate_file_sink_hex(config.dst_file_reader, self.separation_value_miller, self.separation_value_manchester, True)

    
        self.configure_graph()
        


    def generate_file_sink_hex(self, filename, separation_value_miller, separation_value_manchester, separate_by_space):
        data = alibaba.file_sink_hex(gr.sizeof_char, filename, separation_value_miller, separation_value_manchester, separate_by_space)
        return data


    def configure_graph (self):

        float_converter=gr.complex_to_float()
        float_converter_reader=gr.complex_to_float()

        zero_count=8*int(round(self.rx_sampling_rate/self.data_rate))

        splitter_reader=alibaba.blocksplitter_ff(self.block_splitter_offset_channel_two, zero_count, self.separation_value) # for Iffreq=0! Since the reader speaks so much louder, it is possible to cut out the tag part by taking a offset value that is high enough!
        splitter=alibaba.blocksplitter_ff(self.block_splitter_offset_channel_one, zero_count, self.separation_value)
        
        square=alibaba.square_ff()
        square_reader=alibaba.square_ff()
        
        normalizer=alibaba.normalizer_ff(self.separation_value, self.normalizer_value) #1000 is the value we want to normalize to...
        normalizer_reader=alibaba.normalizer_ff(self.separation_value, self.normalizer_value) #1000 is the value we want to normalize to...
        
        self.tmp=alibaba.new_intp() #Note: just a dummy pointer passed to mimadecoder. not actually used...
        alibaba.intp_assign(self.tmp,0)
                

        mimadecoder=alibaba.mimadecoder_fb(
            self.rx_sampling_rate, 
            self.data_rate, 
            self.miller_offset_channel_one, 
            self.manchester_offset_channel_one, 
            self.output_channel_one, 
            self.separation_value,
            self.separation_value_miller, 
            self.separation_value_manchester, 
            self.check_parity,
            self.check_crc,
            self.tmp)

        mimadecoder_reader=alibaba.mimadecoder_fb(
            self.rx_sampling_rate, 
            self.data_rate, 
            self.miller_offset_channel_two, 
            self.manchester_offset_channel_two,
            self.output_channel_two,
            self.separation_value,
            self.separation_value_miller,
            self.separation_value_manchester, 
            self.check_parity,
            self.check_crc,
            self.send_state)
        
                
        lowpass=gr.firdes.low_pass(
            1,
            self.rx_sampling_rate, 
            self.lowpass_cutoff_channel_one, 
            self.lowpass_transition_width_channel_one, 
            gr.firdes.WIN_HAMMING)
        
        fir_low= gr.fir_filter_fff (1,lowpass)
        
        lowpass_reader=gr.firdes.low_pass(
            1,
            self.rx_sampling_rate, 
            self.lowpass_cutoff_channel_two, 
            self.lowpass_transition_width_channel_two, 
            gr.firdes.WIN_HAMMING)
        
        fir_low_reader= gr.fir_filter_fff (1,lowpass_reader)
        
        
        di = gr.deinterleave(gr.sizeof_gr_complex)
        self.connect(self.rx, di)

        self.connect((di,0), 
                     float_converter, 
                     square,
                     fir_low,
                     splitter, 
                     normalizer,
                     mimadecoder, 
                     self.dst_data)

        self.connect((di,1), 
                     float_converter_reader, 
                     square_reader, 
                     fir_low_reader,
                     splitter_reader, 
                     normalizer_reader,
                     mimadecoder_reader, 
                     self.dst_reader)
        
        #self.connect((di,1), float_converter,  splitter, self.dst_data)
        
        
        
class my_top_block_1356_transponder(my_top_block_1356):
    def __init__ (self, config):
        my_top_block_1356.__init__(self,config)
        
        self.data_rate=config.data_rate
        self.amplitude=config.tx_amplitude
        self.source_file=config.source_file
        
        self.setup_sender(config.tx_nchan, config.tx_interp, config.tx_gain, config.tx_if_freq)
        self.configure_graph_send()
        
        
    def configure_graph_send(self):
        complexconverter=gr.float_to_complex()
        
        print self.source_file
        
        #data= (2,2,0,0,1,1,0,0,1,0,0,2,2)
        #data= (2,2,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,2,2)
        #data= (0,0,0,0,0,0,0,0,0,0,0,0,0,0)

        #datasource = gr.vector_source_b (data,True)
        
        #self.siggen=alibaba.readersource_bf(self.tx_sampling_rate, self.data_rate, self.amplitude)
        self.tagsiggen=alibaba.tagsource_bf(self.tx_sampling_rate, self.data_rate, self.amplitude,self.send_state, self.source_file)
        self.connect(self.tagsiggen, complexconverter, self.tx)
        #self.connect(datasource, self.siggen, complexconverter, self.tx)



        
