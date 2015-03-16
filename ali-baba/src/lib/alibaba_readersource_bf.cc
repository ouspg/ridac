/*
 * config.h is generated by configure.  It contains the results
 * of probing for features, options etc.  It should be the first
 * file included in your .cc file.
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alibaba_readersource_bf.h>
#include <gr_io_signature.h>

/*
 * Create a new instance of alibaba_readersource_bf and return
 * a boost shared_ptr.  This is effectively the public constructor.
 */
alibaba_readersource_bf_sptr 
alibaba_make_readersource_bf (float sampling_frequency, float data_rate, float amplitude)
{
  return alibaba_readersource_bf_sptr (new alibaba_readersource_bf (sampling_frequency, data_rate,amplitude));
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
alibaba_readersource_bf::alibaba_readersource_bf (float sampling_frequency, float data_rate, float amplitude)
  : gr_sync_block ("readersource_bf",
	      gr_make_io_signature (MIN_IN, MAX_IN, sizeof (char)),
	      gr_make_io_signature (MIN_OUT, MAX_OUT, sizeof (float)))
{
	sampling_frequency_=sampling_frequency;
	data_rate_=data_rate;
        samples_per_symbol_=rint(sampling_frequency_/data_rate_);
	amplitude_=amplitude;
        previous_symbol_=2;  //start indicator!
}

/*
 * Our virtual destructor.
 */
alibaba_readersource_bf::~alibaba_readersource_bf ()
{
}

int alibaba_readersource_bf::output_function(std::vector<float> &out_buffer, float *out, int available_output_items, int out_counter)
{
        int tmp_size=out_buffer.size();
        int min=std::min(tmp_size,available_output_items);
        if(min==0) return 0;
        std::copy(out_buffer.begin(), out_buffer.begin()+min, &out[out_counter]);
        out_buffer.erase(out_buffer.begin(), out_buffer.begin()+min);
        return min;
}

int 
alibaba_readersource_bf::work (int noutput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
  const char *in = (const char *) input_items[0];
  float *out = (float *) output_items[0];
  int out_counter=0;
  int items_written=0;


  //FIXME unfinished code! This block does not work as intended!!!

  if(!tmp_buffer.empty()) //there are still samples from the previous run!
  {
        items_written= output_function(tmp_buffer, out, noutput_items-out_counter, out_counter);
        if(items_written==noutput_items-out_counter)
        {
                consume_each (0); //we haven't consumed one single input item yet!
                return out_counter+=items_written;
        }
        else
        {
                out_counter+=items_written; 
        }
  }


  for (int i = 0; i < noutput_items; i++)
  {
        

        if(in[i]==2)
        {
                for(int j=0;j<samples_per_symbol_*50;j++) 
                {
                        tmp_buffer.push_back(amplitude_);
                }
        }
        else if(in[i]==1)
        {
                for(int j=0;j<samples_per_symbol_;j++) 
                {
                        if(j< samples_per_symbol_/2) tmp_buffer.push_back(amplitude_);
                        else if(j>= samples_per_symbol_/2 && j< ((samples_per_symbol_/2) + (samples_per_symbol_/4))) tmp_buffer.push_back(0);
                        else tmp_buffer.push_back(amplitude_);
                }
        }
        else if(in[i]==0 && previous_symbol_==1)
        {
                for(int j=0;j<samples_per_symbol_;j++) 
                {
                        tmp_buffer.push_back(amplitude_);
                }        
        }
        else if(in[i]==0)
        {
                for(int j=0;j<samples_per_symbol_;j++) 
                {
                        if(j< samples_per_symbol_/4) tmp_buffer.push_back(0);
                        else tmp_buffer.push_back(amplitude_);
                }
        }
        previous_symbol_=in[i];
  }
  
  items_written= output_function(tmp_buffer, out, noutput_items-out_counter, out_counter);

  // Tell runtime system how many output items we produced.
  return out_counter+items_written;
}
