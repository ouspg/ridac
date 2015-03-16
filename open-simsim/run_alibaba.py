#!/usr/bin/env python

from gnuradio import gr, gru
from gnuradio import usrp
from gnuradio import alibaba
import sys
import thread
import time
from setup_device import *
import os
from ConfigParser import *

import generator
        
import time
        

        
              
def exit_threat(tb):  
    raw_input("Press Enter to Quit\n") 
    tb.stop()
    os._exit(99)
    
def choose_mode(options):
    print "First Argument has to be a mode. Valid modes are: \n"
    i=1
    dict={}
    for item in options:
        print "%d: %s" %(i, item)
        dict[i]=item
        i=i+1
    while True:
        print "\nChoose mode[1..%d]; press q to quit: " %(i-1),
        x=raw_input("")
        try:
            int_x=int(x)
            if int_x > 0 and int_x < i:
                break
        except:
            if x == 'q':
                os._exit(99)
    return dict.get(int_x)


def main ():
    
    configdict = ConfigParser()
    configdict.read('config.conf')
    section=0
    
    if len(sys.argv) <= 1:
        section=choose_mode(configdict.sections())
    else:
        if not configdict.has_section(sys.argv[1]):
            section=choose_mode(configdict.sections())
        else:
            section=sys.argv[1]
            
            
    config=configurator()

    
    def setConfig(target, convert, s):
        if target not in config.__dict__:
            raise  SyntaxError('no such variable: %s'%target)
        config.__dict__[target] = convert( configdict.get(section, s))
    
    if section in [
        "125kHz_FSK_receive",
        "125kHz_FSK_send",
        "125kHz_FSK_send_brute",
        "13.56MHz_NFC_send_as_transponder"]:
        setConfig('tx_interp',int ,'tx_interpolation')
        setConfig('tx_gain', int, 'tx_gain')
        setConfig('tx_if_freq',int, 'tx_intermediate_frequency_channel_one')
        setConfig('tx_nchan',int,'number_send_channels')
                
    
    if section in ["125kHz_FSK_receive","13.56MHz_NFC_receive","13.56MHz_NFC_send_as_transponder"]:
        setConfig('rx_nchan',int, 'number_receive_channels')
        setConfig('rx_interp',int,'rx_interpolation')
        setConfig('rx_gain',int, 'rx_gain')
        setConfig('rx_if_freq',int, 'rx_intermediate_frequency_channel_one')
        setConfig('dst_file',str, 'dst_filename')
        
    if section in ["125kHz_FSK_receive","13.56MHz_NFC_send_as_transponder"]:
        setConfig('transmit_freq',int, 'tx_carrier_frequency')
        
    
    if section in ["125kHz_FSK_receive","125kHz_FSK_send","125kHz_FSK_send_brute"]:
        setConfig('freq_one',int,'frequency_one')
        setConfig('freq_zero',int,'frequency_zero')
        setConfig('tx_amplitude',int,'signal_amplitude')
        
    if section in ["13.56MHz_NFC_receive","13.56MHz_NFC_send_as_transponder"]:
        setConfig('dst_file_reader',str,'dst_filename_reader')
        setConfig('rx_if_freq_2',int,'rx_intermediate_frequency_channel_two')
        setConfig('block_sep_val',int, 'block_separation_value')
        setConfig('char_block_sep_val_miller',int,'char_block_separation_value_miller')
        setConfig('char_block_sep_val_manchester',int,'char_block_separation_value_manchester')
        setConfig('data_rate',int,'data_rate')
        
        setConfig('blocksplitter_offset_channel_one',int,'blocksplitter_offset_channel_one')
        setConfig('blocksplitter_offset_channel_two',int,'blocksplitter_offset_channel_two')
        #not used...
        #setConfig('blocksplitter_how_many_zeros',int,'blocksplitter_how_many_zeros')
        setConfig('normalizer_value',int, 'normalizer_value')
        setConfig('manchester_offset_channel_one',int, 'manchester_offset_channel_one')
        setConfig('miller_offset_channel_one',int, 'miller_offset_channel_one')
        setConfig('manchester_offset_channel_two',int,'manchester_offset_channel_two')
        setConfig('miller_offset_channel_two',int,'miller_offset_channel_two')
        if configdict.get(section, 'check_crc')=="True":
            config.check_crc=True
        else:
            config.check_crc=False
            
        if configdict.get(section, 'check_parity')=="True":
            config.check_parity=True
        else:
            config.check_parity=False
        setConfig('output_channel_one',int,'output_channel_one')
        setConfig('output_channel_two',int,'output_channel_two')
        setConfig('lowpass_cutoff_channel_one',int, 'lowpass_cutoff_channel_one')
        setConfig('lowpass_transition_width_channel_one',int,'lowpass_transition_width_channel_one')
        setConfig('lowpass_cutoff_channel_two',int, 'lowpass_cutoff_channel_two')
        setConfig('lowpass_transition_width_channel_two',int,'lowpass_transition_width_channel_two')

    if section in ["125kHz_FSK_send","125kHz_FSK_send_brute"]:
        setConfig('cycles_per_symbol',int, 'cycles_per_symbol') 

    
    if section == "125kHz_FSK_receive":
        tb = my_top_block_125(config)
        
    if section == "13.56MHz_NFC_receive":
        tb = my_top_block_1356(config)

    if section == "125kHz_FSK_send":
        setConfig('source_file',str,'src_filename')
        tb=my_top_block_125_send(config)

    if section == "125kHz_FSK_send_brute":
        setConfig("buffer_file_suffix",str,"buffer_file_suffix")
        setConfig("buffer_file_count",int,"buffer_file_count")
        setConfig("repeats_per_key",int,"repeats_per_key")
        setConfig("keys_in_buffer",int,"keys_in_buffer")
        tb = my_top_block_125_send_brute(config)
        
    if section == "13.56MHz_NFC_send_as_transponder":
        setConfig('tx_amplitude',int,'signal_amplitude')
        setConfig('source_file',str,'src_filename')
        tb=my_top_block_1356_transponder(config)

    
    if section == "125kHz_FSK_send_brute":
        print "--"*60
        
        while True:
            start = 0#int( raw_input("start id") )
            cnt = 2**24#int( raw_input("cnt") )
            reps = int(raw_input("repeats"))
            tb.repeater.set_repeat_count(reps)
            
            def generateFiles():
                i = start
                #import os
                

                files = tb.yieldTmpFiles()
                gen = generator.yieldAllKeysInBinarySearchFashion()
                
                
                while i < start + cnt:
                    next = min(i+tb.keys_in_buffer, start + cnt)
                    bufferfile = files.next()
                    generator.writeKeyBlockToFile(gen, bufferfile, i, next)
                    i = next
                    yield i

            f = generateFiles()
            towait = reps * 0.041 * tb.keys_in_buffer / 2.0
            print towait, towait / 60, towait / 3600
            
            print f.next()
            print f.next()
            tb.start ()
            time.sleep(towait )
            for i in f:
                time.sleep(towait)
                print i
                        
            tb.stop()

    else:
        tb.start ()
        os.system('clear')


    if section== "125kHz_FSK_receive":
        thread.start_new(exit_threat,(tb,))
        while 1:
            if tb.check.get_found_id()==True:
                break
            else:
                time.sleep(1)
        id= alibaba.CharVector(tb.check.get_transponder_ID())
        sys.stdout.write("Found transponder ID: ")
        id = "".join([str(ord(item)) for item in id])
        #for item in id:
        #    sys.stdout.write(str(ord(item))) #ord converts a char value to a integer value!   
        #sys.stdout.write("\n")
        print id
        generator.printDataValues(id)
    else:
        raw_input("Press Enter to Stop!")

    tb.stop ()
    
   


if __name__ == '__main__':
        main()
