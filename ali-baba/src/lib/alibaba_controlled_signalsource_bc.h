#ifndef INCLUDED_ALIBABA_CONTROLLED_SIGNALSOURCE_BC_H
#define INCLUDED_ALIBABA_CONTROLLED_SIGNALSOURCE_BC_H

#include <gr_block.h>
#include <gr_fxpt_nco.h>

class alibaba_controlled_signalsource_bc;

typedef boost::shared_ptr<alibaba_controlled_signalsource_bc> alibaba_controlled_signalsource_bc_sptr;

/*!
 * Implements a controlled signal source. Converts the binary input into complex sine waves of a adjustable freqency.
 * @ param sampling_freq: the sampling frequency
 * @ param frequency_one: the freqency representing a binary one
 * @ param frequency_zero: the frequency representing a binary zero
 * @ param ampl: the amplitude
 * @ param offset: the offset from zero
 * @ param waves_per_symbol: wave zycles per input bit
 */
alibaba_controlled_signalsource_bc_sptr alibaba_make_controlled_signalsource_bc (double sampling_freq, double frequency_one,
				double frequency_zero, double ampl, gr_complex offset, int zycles_per_symbol);

/*!
 * Implements a controlled signal source. Converts the binary input into complex sine waves of a adjustable freqency.
 */
class alibaba_controlled_signalsource_bc : public gr_block
{
private:

  friend alibaba_controlled_signalsource_bc_sptr alibaba_make_controlled_signalsource_bc (double sampling_freq, double frequency_one,
				double frequency_zero, double ampl, gr_complex offset, int cycles_per_symbol);

  alibaba_controlled_signalsource_bc (double sampling_freq, double frequency_one,
				double frequency_zero, double ampl, gr_complex offset, int zycles_per_symbol);  	// private constructor

  double		d_sampling_freq;
  double		d_frequency1;
  double		d_frequency2;
  double		d_ampl;
  gr_complex		d_offset;
  gr_fxpt_nco		d_nco;
  int                   d_zycles_per_symbol;
  
  

 public:
  ~alibaba_controlled_signalsource_bc ();	// public destructor

  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_CONTROLLED_SIGNALSOURCE_BC_H */
