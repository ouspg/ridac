#ifndef INCLUDED_ALIBABA_SQUARE_FF_H
#define INCLUDED_ALIBABA_SQUARE_FF_H

#include <gr_sync_block.h>

class alibaba_square_ff;

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
typedef boost::shared_ptr<alibaba_square_ff> alibaba_square_ff_sptr;

/*!
 * A simple block to square a signal. Each sample is squared... 
 */
alibaba_square_ff_sptr alibaba_make_square_ff ();

/*!
 * A simple class to square a signal. Each sample is squared... 
 */
class alibaba_square_ff : public gr_sync_block
{
private:


  friend alibaba_square_ff_sptr alibaba_make_square_ff ();

  alibaba_square_ff ();  	// private constructor

 public:
  ~alibaba_square_ff ();	// public destructor

  // Where all the action really happens

  int work (int noutput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_SQUARE_FF_H */
