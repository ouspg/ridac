/*
 * config.h is generated by configure.  It contains the results
 * of probing for features, options etc.  It should be the first
 * file included in your .cc file.
 */
#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alibaba_normalizer_ff.h>
#include <gr_io_signature.h>

/*
 * Create a new instance of alibaba_normalizer_ff and return
 * a boost shared_ptr.  This is effectively the public constructor.
 */
alibaba_normalizer_ff_sptr 
alibaba_make_normalizer_ff (float block_separation_value, float value_to_normalize_to)
{
  return alibaba_normalizer_ff_sptr (new alibaba_normalizer_ff (block_separation_value, value_to_normalize_to));
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
alibaba_normalizer_ff::alibaba_normalizer_ff (float block_separation_value, float value_to_normalize_to)
  : gr_block ("normalizer_ff",
	      gr_make_io_signature (MIN_IN, MAX_IN, sizeof (float)),
	      gr_make_io_signature (MIN_OUT, MAX_OUT, sizeof (float)))
{
	block_separation_value_=block_separation_value;
	value_to_normalize_to_=value_to_normalize_to; 
        initial_fill=false;
        split_block=false;
        initial_fill_count=0;
        //just to be sure, that vectors are empty;
        tmp_buffer.clear();
        out_buffer.clear();
        max_item=0;
        state=0;

}

/*
 * Our virtual destructor.
 */
alibaba_normalizer_ff::~alibaba_normalizer_ff ()
{
}

int alibaba_normalizer_ff::output_function(std::vector<float> *ob, float *out, int available_output_items, int out_counter)
{
        int tmp_size=ob->size();
        int min=std::min(tmp_size,available_output_items);
        if(min==0) return 0;
        if(tmp_size<=min)
        {
                std::copy(ob->begin(), ob->end(), &out[out_counter]);
                ob->clear();
        }
        else 
        {
                std::copy(ob->begin(), ob->begin()+min, &out[out_counter]);
                ob->erase(ob->begin(), ob->begin()+min);
        }
        return min;
}

int 
alibaba_normalizer_ff::general_work (int noutput_items,
			       gr_vector_int &ninput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
  const float *in = (const float *) input_items[0];
  float *out = (float *) output_items[0];

  int out_counter=0;
  int initial_fill_number=5;
  int norm_factor=0;
  int items_written=0;

  if(split_block==true) //check, if there is still data from previous call!
  {
        int items_avail=noutput_items-out_counter;
        items_written= output_function(&out_buffer, out, items_avail, out_counter);  //out counter should be 0 here!
        out_counter+=items_written;
        if(items_written==items_avail)
        {
                consume_each (0); //we haven't consumed one single input item yet!
                return out_counter;
        }
        else
        {
                state=0;
                split_block=false;
                out_buffer.clear();   
        }
  }

  for (int i = 0; i < noutput_items; i++)
  {


        if(!initial_fill)
        {
              tmp_buffer.push_back(in[i]);
              initial_fill_count++; 
              if(initial_fill_count>=initial_fill_number)
                initial_fill=true;
              continue;
        }
        else
        {
         tmp_buffer.push_back(in[i]);
        }


        switch (state)
        {
                case 0: if(tmp_buffer[0]==block_separation_value_ && tmp_buffer[1]!=block_separation_value_) state=1;
                        else tmp_buffer.erase(tmp_buffer.begin());
                        break; 
                case 1: out_buffer.push_back(tmp_buffer[0]);
                        if(tmp_buffer[0]>max_item) max_item=tmp_buffer[0];
                        if(tmp_buffer[0]!=block_separation_value_ && tmp_buffer[1]==block_separation_value_) //Normalize the block and output it!
                        {
                                norm_factor=max_item/value_to_normalize_to_;
                                for(int k=1;k<out_buffer.size();k++) out_buffer[k]=out_buffer[k]/norm_factor; //normalize here, do not normalize block separation value
                                max_item=0; //delete for next turn!
                                int items_avail=noutput_items-out_counter;
                                items_written= output_function(&out_buffer, out, items_avail, out_counter);
                                out_counter+=items_written;
                                if(items_written==items_avail)
                                {
                                        if(!out_buffer.empty()) split_block=true;
                                }
                                else
                                {
                                        state=0;
                                        split_block=false;
                                        out_buffer.clear();   
                                }
                                tmp_buffer.erase(tmp_buffer.begin());//we don't need that item any more!
                                consume_each (i+1);
                                return out_counter;
                        }
                        tmp_buffer.erase(tmp_buffer.begin());
                        break;
                default: max_item=0;
                         state=0;
                         out_buffer.clear();
  
        }

  }

     

  // Tell runtime system how many input items we consumed on
  // each input stream.

  consume_each (noutput_items);

  // Tell runtime system how many output items we produced.
  return out_counter;
}