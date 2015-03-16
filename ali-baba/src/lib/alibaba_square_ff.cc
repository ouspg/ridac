/*
 * config.h is generated by configure.  It contains the results
 * of probing for features, options etc.  It should be the first
 * file included in your .cc file.
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alibaba_square_ff.h>
#include <gr_io_signature.h>

/*
 * Create a new instance of alibaba_square_ff and return
 * a boost shared_ptr.  This is effectively the public constructor.
 */
alibaba_square_ff_sptr 
alibaba_make_square_ff ()
{
  return alibaba_square_ff_sptr (new alibaba_square_ff ());
}

/*
 * Specify constraints on number of input and output streams.
 * This info is used to construct the input and output signatures
 * (2nd & 3rd args to gr_block's constructor).  The input and
 * output signatures are used by the runtime system to
 * check that a valid number and type of inputs and outputs
 * are connected to this block.  In this case, we accept
 * only 1 input and 1 output.
 */
static const int MIN_IN = 1;	// mininum number of input streams
static const int MAX_IN = 1;	// maximum number of input streams
static const int MIN_OUT = 1;	// minimum number of output streams
static const int MAX_OUT = 1;	// maximum number of output streams

/*
 * The private constructor
 */
alibaba_square_ff::alibaba_square_ff ()
  : gr_sync_block ("square_ff",
	      gr_make_io_signature (MIN_IN, MAX_IN, sizeof (float)),
	      gr_make_io_signature (MIN_OUT, MAX_OUT, sizeof (float)))
{

}

/*
 * Our virtual destructor.
 */
alibaba_square_ff::~alibaba_square_ff ()
{
}

int 
alibaba_square_ff::work (int noutput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
  const float *in = (const float *) input_items[0];
  float *out = (float *) output_items[0];


  for (int i = 0; i < noutput_items; i++)
  {
        out[i]=in[i]*in[i];
  }

  // Tell runtime system how many output items we produced.
  return noutput_items;
}