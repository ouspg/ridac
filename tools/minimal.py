#!/usr/bin/env python2.5

print "Loading gnuradio..."
from gnuradio import gr
from gnuradio import audio
from gnuradio import blks2
print

def build_graph ():
    rf_rate = 256000
    ampl = 0.1
    src0 = gr.sig_source_f (rf_rate, gr.GR_SIN_WAVE, 1000, ampl)
    
    audio_samplerate = 48000
    audio_interpolation = 3
    audio_decimation = 16
    sound = audio.sink (audio_samplerate)
    resampler = blks2.rational_resampler_fff(audio_interpolation,
                                             audio_decimation,
                                             taps=None)

    fg = gr.flow_graph ()
    fg.connect (src0, resampler)
    fg.connect (resampler, sound)

    return fg

if __name__ == '__main__':
    fg = build_graph ()
    fg.start ()
    raw_input ('Press Enter to quit: ')
    fg.stop ()

