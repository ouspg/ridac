/*
 * config.h is generated by configure.  It contains the results
 * of probing for features, options etc.  It should be the first
 * file included in your .cc file.
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alibaba_sequence_repeater_bb.h>
#include <gr_io_signature.h>

/*
 * Create a new instance of alibaba_sequence_repeater_bb and return
 * a boost shared_ptr.  This is effectively the public constructor.
 */
alibaba_sequence_repeater_bb_sptr 
alibaba_make_sequence_repeater_bb ()
{
  return alibaba_sequence_repeater_bb_sptr (new alibaba_sequence_repeater_bb ());
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
alibaba_sequence_repeater_bb::alibaba_sequence_repeater_bb ()
  :gr_block ("sequence_repeater_bb",
	      gr_make_io_signature (MIN_IN, MAX_IN, sizeof (char)),
	      gr_make_io_signature (MIN_OUT, MAX_OUT, sizeof (char)))
{
  this->d_offset = 0;
  this->d_sequence_length = 1;
  this->d_repeat_count = 1;

  this->d_repeat_counter = 0;
  this->set_relative_rate(this->d_repeat_count);
}

/*
 * Our virtual destructor.
 */
alibaba_sequence_repeater_bb::~alibaba_sequence_repeater_bb ()
{
}


void
alibaba_sequence_repeater_bb::forecast (int noutput_items, 
					gr_vector_int &ninput_items_required)
{
  unsigned ninputs = ninput_items_required.size ();

  if (this->d_repeat_counter != 0)
    noutput_items = 0;

  for (unsigned i = 0; i < ninputs; i++)
    ninput_items_required[i] = noutput_items;
    }


int
alibaba_sequence_repeater_bb::general_work (int noutput_items,
					    gr_vector_int &ninput_items,
					    gr_vector_const_void_star &input_items,
					    gr_vector_void_star &output_items)
{
  const char *in = (const char *) input_items[0];
  char *out = (char *) output_items[0];
  int consumed = 0;

  for (consumed = 0; consumed < noutput_items && this->d_offset < ninput_items[0];
       this->d_offset ++)
  {
    if(this->d_offset >=  this->d_sequence_length)
    {
      this->d_offset = 0;
      this->d_repeat_counter ++;
      if(this->d_repeat_counter >= this->d_repeat_count)
      {
	this->d_repeat_counter =0;
	consume_each (this->d_sequence_length);
	return consumed;
      }
    }
    out[consumed]=in[this->d_offset];
    consumed ++;
  }
  //consume_each (noutput_items);
  // Tell runtime system how many output items we produced.
  return consumed;
}