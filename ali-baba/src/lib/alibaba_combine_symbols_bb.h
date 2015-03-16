#ifndef INCLUDED_ALIBABA_COMBINE_SYMBOLS_BB_H
#define INCLUDED_ALIBABA_COMBINE_SYMBOLS_BB_H

#include <gr_block.h>

class alibaba_combine_symbols_bb;

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
typedef boost::shared_ptr<alibaba_combine_symbols_bb> alibaba_combine_symbols_bb_sptr;

/*!
 * This class takes a charfile containing zeros and ones. If one symbol is represented
 * by more than one zeros or ones, this class combines them and returns only one symbol.
 * Returns: a reduced stream of chars
 * @ param min_number_of_symbols_representing_one_binary_value: the minimum number of zeros or ones that represent one symbol.
 * @ param max_number_of_symbols_representing_one_binary_value: the maximum number of zeros or ones that represent one symbol.
 */
alibaba_combine_symbols_bb_sptr alibaba_make_combine_symbols_bb (int min_number_of_symbols_representing_one_binary_value, int max_number_of_symbols_representing_one_binary_value);

/*!
 * This class takes a charfile containing zeros and ones. If one symbol is represented
 * by more than one zeros or ones, this class combines them and returns only one symbol.
 * Returns: a reduced stream of chars
 */
class alibaba_combine_symbols_bb : public gr_block
{
private:

  friend alibaba_combine_symbols_bb_sptr alibaba_make_combine_symbols_bb (int min_number_of_symbols_representing_one_binary_value, int max_number_of_symbols_representing_one_binary_value);

  alibaba_combine_symbols_bb (int min_number_of_symbols_representing_one_binary_value, int max_number_of_symbols_representing_one_binary_value);  	// private constructor
  int printsymbols(char *output_file, int file_position, int counter, char symbol);

  int max_num;
  int min_num;
  int init;
  int counter;
  char symbol; 

 public:
  ~alibaba_combine_symbols_bb ();	// public destructor

  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_COMBINE_SYMBOLS_BB_H */
