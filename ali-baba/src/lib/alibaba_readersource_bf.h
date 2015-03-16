#ifndef INCLUDED_ALIBABA_READERSOURCE_BF_H
#define INCLUDED_ALIBABA_READERSOURCE_BF_H

#include <gr_sync_block.h>

class alibaba_readersource_bf;

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
typedef boost::shared_ptr<alibaba_readersource_bf> alibaba_readersource_bf_sptr;

/*!
 * This class takes a binary stream of data and and generates samples according to the 14443-2 
 * communication for a reader. The class outputs a constant amplitude, if carryer should be on and
 * zero, if carryer should be off. The transmition unit has to be tuned to 13.56MHz, 
 * to generate a 13.56Mhz carryer, if the output of this class is different than zero.
 * @param sampling_frequency the sampling frequency
 * @param data_rate the data rate, the information is modulated onto the carryer
 * @param amplitude the amplitude of the signal.
 */
alibaba_readersource_bf_sptr alibaba_make_readersource_bf (float sampling_frequency, float data_rate, float amplitude);

/*!
 * This class takes a binary stream of data and and generates samples according to the 14443-2 
 * communication for a reader. The class outputs a constant amplitude, if carryer should be on and
 * zero, if carryer should be off. The transmition unit has to be tuned to 13.56MHz, 
 * to generate a 13.56Mhz carryer, if the output of this class is different than zero.
 */
class alibaba_readersource_bf : public gr_sync_block
{
private:


  friend alibaba_readersource_bf_sptr alibaba_make_readersource_bf (float sampling_frequency, float data_rate, float amplitude);

  alibaba_readersource_bf (float sampling_frequency, float data_rate, float amplitude);  	// private constructor

  int output_function(std::vector<float> &out_buffer, float *out, int available_output_items, int out_counter);

  float sampling_frequency_;
  float data_rate_;
  int samples_per_symbol_;
  float amplitude_;
  char previous_symbol_;
  std::vector<float> tmp_buffer;

 public:
  ~alibaba_readersource_bf ();	// public destructor

  // Where all the action really happens

  int work (int noutput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_READERSOURCE_BF_H */
