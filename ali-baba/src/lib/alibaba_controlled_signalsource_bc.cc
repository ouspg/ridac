#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alibaba_controlled_signalsource_bc.h>
#include <gr_io_signature.h>
#include <gr_complex.h>
#include <stdexcept>


alibaba_controlled_signalsource_bc_sptr 
alibaba_make_controlled_signalsource_bc (double sampling_freq, double frequency_one,
				double frequency_zero, double ampl, gr_complex offset, int zycles_per_symbol)
{
  return alibaba_controlled_signalsource_bc_sptr (new alibaba_controlled_signalsource_bc (sampling_freq, frequency_one, frequency_zero, ampl, offset, zycles_per_symbol));
}


static const int MIN_IN = 1;	// mininum number of input streams
static const int MAX_IN = 1;	// maximum number of input streams
static const int MIN_OUT = 1;	// minimum number of output streams
static const int MAX_OUT = 1;	// maximum number of output streams

/*
 * The private constructor
 */
alibaba_controlled_signalsource_bc::alibaba_controlled_signalsource_bc (double sampling_freq, double frequency_one,
				double frequency_zero, double ampl, gr_complex offset, int zycles_per_symbol)
  : gr_block ("alibaba_controlled_signalsource_bc",
	      gr_make_io_signature (MIN_IN, MAX_IN, sizeof (char)),
	      gr_make_io_signature (MIN_OUT, MAX_OUT, sizeof (gr_complex)))
{
                d_sampling_freq=sampling_freq;
                d_frequency1=frequency_one;
                d_frequency2=frequency_zero;
                d_ampl=ampl;
                d_offset=offset;
                d_zycles_per_symbol=zycles_per_symbol;
               
                d_nco.set_freq (0);
}


alibaba_controlled_signalsource_bc::~alibaba_controlled_signalsource_bc ()
{
}


int 
alibaba_controlled_signalsource_bc::general_work (int noutput_items,
			       gr_vector_int &ninput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
        const char *in = (const char *) input_items[0];
        gr_complex *out = (gr_complex *) output_items[0];

        double samples_one=(d_sampling_freq/d_frequency1)*d_zycles_per_symbol;  //esitmate the samples needed for output (consuning one input bit)
        double samples_zero=(d_sampling_freq/d_frequency2 )*d_zycles_per_symbol;
        int minimum=0;
              
        if(in[0]=='1' || in[0]==1) //take binary represented as numbers or as chars.
        {
              d_nco.set_freq (2 * M_PI * d_frequency1 / d_sampling_freq); //set the signal frequency for one
              minimum=std::min((double) noutput_items, samples_one);
        }
        else if(in[0]=='0' || in[0]==0)
        { 
              d_nco.set_freq (2 * M_PI * d_frequency2 / d_sampling_freq); //set signal frequency for zero
              minimum=std::min((double) noutput_items, samples_zero);
        }
        else 
        {
              throw std::runtime_error ("gr_alibaba_controlled_signalsource: invalid binary symbol"); //no binary stream!
        }

        
        //Code here is the same as for a sine wave in gr_sigsource_cc
        #if 1	// complex?
            d_nco.sincos (out, minimum, d_ampl);
            if (d_offset != gr_complex(0,0))
            {
                for (int i = 0; i < minimum; i++)
                {
                         out[i] += d_offset;
                }
            }
        #else			// nope...
            d_nco_one.sin (out, minimum, d_ampl);
            if (d_offset != 0)
            {
                for (int i = 0; i < minimum; i++)
                {
                        out[i] += d_offset;
                }
            }
        #endif
  
        consume_each (1); //only one input item per output

        // Tell runtime system how many output items we produced.
        return minimum;
}
