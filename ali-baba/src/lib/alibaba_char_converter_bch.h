#ifndef INCLUDED_ALIBABA_CHAR_CONVERTER_BCH_H
#define INCLUDED_ALIBABA_CHAR_CONVERTER_BCH_H

#include <gr_block.h>

class alibaba_char_converter_bch;

typedef boost::shared_ptr<alibaba_char_converter_bch> alibaba_char_converter_bch_sptr;

/*!
 * Takes a file of binary values and converts them to readable chars.
 */
alibaba_char_converter_bch_sptr alibaba_make_char_converter_bch ();

/*!
 * Takes a file of binary values and converts them to readable chars.
 */
class alibaba_char_converter_bch : public gr_block
{
private:

  friend alibaba_char_converter_bch_sptr alibaba_make_char_converter_bch ();

  alibaba_char_converter_bch ();  	// private constructor
  

 public:
  ~alibaba_char_converter_bch ();	// public destructor

  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_CHAR_CONVERTER_BB_H */
