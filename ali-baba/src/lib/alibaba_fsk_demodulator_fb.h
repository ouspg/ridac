#ifndef INCLUDED_ALIBABA_FSK_DEMODULATOR_FB_H
#define INCLUDED_ALIBABA_FSK_DEMODULATOR_FB_H

#include <gr_block.h>

class alibaba_fsk_demodulator_fb;

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
typedef boost::shared_ptr<alibaba_fsk_demodulator_fb> alibaba_fsk_demodulator_fb_sptr;

/*!
 * Class to demodulate FSK. This only works, if the binary symbols are represented by two frequencies.
 * Premises: Carrier frequency is already removed and the resulting signal containing the data frequencies 
 * oszilates around zero...
 * Returns: a stream containing binary symbols at reduced data rate
 * @ param sampling_frequency: the sampling frequency of the signal
 * @ param frequency_one: the freqency representing a binary one
 * @ param frequency_zero: the freqency representing a binary zero
 */
alibaba_fsk_demodulator_fb_sptr alibaba_make_fsk_demodulator_fb (float sampling_frequency, float frequency_one, float frequency_zero);

/*!
 * Class to demodulate FSK. This only works, if the binary symbols are represented by two frequencies.
 * Premises: Carrier frequency is already removed and the resulting signal containing the data frequencies 
 * oszilates around zero...
 */
class alibaba_fsk_demodulator_fb : public gr_block
{
private:
  // The friend declaration allows alibaba_make_fsk_demodulator_fb to
  // access the private constructor.

  friend alibaba_fsk_demodulator_fb_sptr alibaba_make_fsk_demodulator_fb (float sampling_frequency, float frequency_one, float frequency_zero);

  alibaba_fsk_demodulator_fb (float sampling_frequency, float frequency_one, float frequency_zero);  	// private constructor

  float sampl_freq;
  float freq_one;
  float freq_zero;

  bool initial_fill;
  int initial_fill_count;

  //to ensure that all possible frequency cycles are found, it has to be ensured that they are checked even if work is called more often...      
  std::vector<float> tmp_buffer;
  int counter;

  int num_samples_one;
  int num_samples_zero;
  int maximum;

 public:
  ~alibaba_fsk_demodulator_fb ();	// public destructor

  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_FSK_DEMODULATOR_FB_H */
