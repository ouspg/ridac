#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alibaba_char_converter_bch.h>
#include <gr_io_signature.h>


alibaba_char_converter_bch_sptr 
alibaba_make_char_converter_bch ()
{
  return alibaba_char_converter_bch_sptr (new alibaba_char_converter_bch ());
}


static const int MIN_IN = 1;	// mininum number of input streams
static const int MAX_IN = 1;	// maximum number of input streams
static const int MIN_OUT = 1;	// minimum number of output streams
static const int MAX_OUT = 1;	// maximum number of output streams

/*
 * The private constructor
 */
alibaba_char_converter_bch::alibaba_char_converter_bch ()
  : gr_block ("binarychar_bch",
	      gr_make_io_signature (MIN_IN, MAX_IN, sizeof (char)),
	      gr_make_io_signature (MIN_OUT, MAX_OUT, sizeof (char)))
{
}


alibaba_char_converter_bch::~alibaba_char_converter_bch ()
{
}


int 
alibaba_char_converter_bch::general_work (int noutput_items,
			       gr_vector_int &ninput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
  const char *in = (const char *) input_items[0];
  char *out = (char *) output_items[0];
  int out_counter=0;

  for (int i = 0; i < noutput_items; i++)
  {
        if(in[i]==0)
        {
		out[out_counter]='0';
                out_counter++;
        }
	else if(in[i]==1)
        {
		out[out_counter]='1';
                out_counter++;
        }
        else if(in[i]==-100)      
        {
                out[out_counter]='\n';
                out_counter++;
        }
        else if(in[i]==-10)      
        {
                out[out_counter]='M';
                out_counter++;
        }
        else
        {
                out[out_counter]='E';
                out_counter++;
        }
  }
  
  consume_each (noutput_items);

  // Tell runtime system how many output items we produced.
  return out_counter;
}
