#ifndef INCLUDED_ALIBABA_BLOCKSPLITTER_FF_H
#define INCLUDED_ALIBABA_BLOCKSPLITTER_FF_H

#include <gr_block.h>

class alibaba_blocksplitter_ff;

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
typedef boost::shared_ptr<alibaba_blocksplitter_ff> alibaba_blocksplitter_ff_sptr;

/*!
 * This class searches for a long sequence of zeros (how_many) and replaces them 
 * with the number block_separation_value. This is used to seperate communication blocks
 * between tag and reaer. The offset parameter is used to set a limit for the 
 * decision zero/one.
 * @param offset: the edge for decision zero/one
 * @param how_many: how many zeros have to pass between blocks...
 * @param block_separation_value: value that is placed instead of a series of zeros to seperate blocks
 */
alibaba_blocksplitter_ff_sptr alibaba_make_blocksplitter_ff (float offset, int how_many, float block_separation_value);

/*!
 * This class searches for a long sequence of zeros (how_many) and replaces them 
 * with the number -1000000. This is used to seperate communication blocks
 * between tag and reaer. The offset parameter is used to set a limit for the 
 * decision zero/one.
 */
class alibaba_blocksplitter_ff : public gr_block
{
private:
  // The friend declaration allows alibaba_make_demodulate_ff to
  // access the private constructor.

  friend alibaba_blocksplitter_ff_sptr alibaba_make_blocksplitter_ff (float offset, int how_many, float block_separation_value);

  alibaba_blocksplitter_ff (float offset, int how_many, float block_separation_value);  	// private constructor
  int output_function(std::vector<float> *out_buffer, float *out, int available_output_items, int out_counter, int zero_count);

  float offset_;
  int how_many_;
  float block_separation_value_;
  int zero_counter;
  std::vector<float> tmp_buffer;

 public:
  ~alibaba_blocksplitter_ff ();	// public destructor

  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_BLOCKSPLITTER_FF_H */
