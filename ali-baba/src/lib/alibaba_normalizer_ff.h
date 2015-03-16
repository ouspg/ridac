#ifndef INCLUDED_ALIBABA_NORMALIZER_FF_H
#define INCLUDED_ALIBABA_NORMALIZER_FF_H

#include <gr_block.h>

class alibaba_normalizer_ff;

/*
 * We use boost::shared_ptr's instead of raw pointers for all access
 * to gr_blocks (and many other data structures).  The shared_ptr gets
 * us transparent reference counting, which greatly simplifies storage
 * management issues.  This is especially helpful in our hybrid
 * C++ / Python system.
 *
 * See http://www.boost.org/libs/smart_ptr/smart_ptr.htm
 *
 * As a convention, the _sptr suffix indicates a boost::shared_ptr
 */
typedef boost::shared_ptr<alibaba_normalizer_ff> alibaba_normalizer_ff_sptr;

/*!
 * This class takes a stream of blocks seperated by block_separation_value and
 * searches for the maximum value in one of this blocks. After that it normalizes
 * the whole block to the value_to_normalize_to (maximum value is not higher than value_to_normalize_to)
 * it outputs a stream of normalized blocks seperated by block_separation_value.
 * @ param block_separation_value: the value that indicates the start of a new block
 * @ param value_to_normalize_to: is the value that block has to be normalized to
 */
alibaba_normalizer_ff_sptr alibaba_make_normalizer_ff (float block_separation_value, float value_to_normalize_to);

/*!
 * This class takes a stream of blocks seperated by block_separation_value and
 * searches for the maximum value in one of this blocks. After that it normalizes
 * the whole block to the value_to_normalize_to (maximum value is not higher than value_to_normalize_to)
 * it outputs a stream of normalized blocks seperated by block_separation_value.
 */
class alibaba_normalizer_ff : public gr_block
{
private:


  friend alibaba_normalizer_ff_sptr alibaba_make_normalizer_ff (float block_separation_value, float value_to_normalize_to);

  alibaba_normalizer_ff (float block_separation_value, float value_to_normalize_to);  	// private constructor
  int output_function(std::vector<float> *out_buffer, float *out, int available_output_items, int out_counter);
  	
  float block_separation_value_;
  float value_to_normalize_to_; 

  bool initial_fill;
  int initial_fill_count;
  bool split_block;

  //to ensure that all possible frequency cycles are found, it has to be ensured that they are checked even if work is called more often...      
  std::vector<float> tmp_buffer;
  std::vector<float> out_buffer;
  int state;

  float max_item;

 public:
  ~alibaba_normalizer_ff ();	// public destructor

  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_NORMALIZER_FF_H */
