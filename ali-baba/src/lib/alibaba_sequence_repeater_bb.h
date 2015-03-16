#ifndef INCLUDED_ALIBABA_SEQUENCE_REPEATER_BB_H
#define INCLUDED_ALIBABA_SEQUENCE_REPEATER_BB_H


#include <gr_block.h>

class alibaba_sequence_repeater_bb;

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
typedef boost::shared_ptr<alibaba_sequence_repeater_bb> alibaba_sequence_repeater_bb_sptr;

/*!
 * A simple block to square a signal. Each sample is squared... 
 */
alibaba_sequence_repeater_bb_sptr alibaba_make_sequence_repeater_bb ();

/*!
 * A simple class to square a signal. Each sample is squared... 
 */
class alibaba_sequence_repeater_bb : public gr_block
{
private:

  
  friend alibaba_sequence_repeater_bb_sptr alibaba_make_sequence_repeater_bb ();

  alibaba_sequence_repeater_bb ();  	// private constructor

  int d_offset;
  int d_sequence_length;
  int d_repeat_count;

  int d_repeat_counter;

 public:
  ~alibaba_sequence_repeater_bb ();	// public destructor

  // the data out / in rate is 2:1 so this needs a rewrite
  virtual void forecast (int noutput_items,
			 gr_vector_int &ninput_items_required);


  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);


  int get_offset(){return this->d_offset;}
  void set_offset(int n){this->d_offset = n;}

  int get_sequence_length(){return this->d_sequence_length;}
  void set_sequence_length(int n){this->d_sequence_length = n;}
  
  int get_repeat_count(){return this->d_repeat_count;}
  
  void set_repeat_count(int n)
  {
    this->d_repeat_count = n;
    this->set_relative_rate(n);
  }
  

};

#endif /* INCLUDED_ALIBABA__SEQUENCE_REPEATER_BB_H*/
