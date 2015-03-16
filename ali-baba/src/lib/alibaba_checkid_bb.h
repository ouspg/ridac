#ifndef INCLUDED_ALIBABA_CHECKID_BB_H
#define INCLUDED_ALIBABA_CHECKID_BB_H

#include <gr_block.h>

class alibaba_checkid_bb;

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
typedef boost::shared_ptr<alibaba_checkid_bb> alibaba_checkid_bb_sptr;

/*!
 * This class checks a binary stream for id. It has a boolean member "id_found", that
 * is changed to true if a valid id could be found.
 * @ param starting_sequence: the binary start sequence of the id
 * @ param how_many_equals: indicates how many equal ids have to be found, that 
 */
alibaba_checkid_bb_sptr alibaba_make_checkid_bb (std::vector<char> starting_sequence, int how_many_equals);

/*!
 * This class checks a binary stream for id. It has a public member "id_found", that
 * is changed to true if a valid id could be found.
 */
class alibaba_checkid_bb : public gr_block
{
private:
  // The friend declaration allows fsk_make_demodulate_fb to
  // access the private constructor.

  friend alibaba_checkid_bb_sptr alibaba_make_checkid_bb (std::vector<char> starting_sequence, int how_many_equals);

  alibaba_checkid_bb (std::vector<char> starting_sequence, int how_many_equals);  	// private constructor
  std::vector<char> decodeID(std::vector<char> id,int start_seq_size);

  std::vector<char> start_seq;
  //to ensure that all possible start sequences are found, it has to be ensured that they are checked even if work is called more often...      
  std::vector<char> tmp_buffer;

  //holds the first id found in sequence
  std::vector<char> initial_id;
  //holds all newly found ids
  std::vector<char> id_to_compare;
  //counts how many equal ids could be found

  //ID is finally stored in this vector:
  std::vector<char> transponder_id;
  int number_of_matches;
  int state;
  int num_equals;
  int initial_fill_count;
  bool found_id;
  bool initial_fill;
  int buffer_size;


 public:
  ~alibaba_checkid_bb ();	// public destructor

  std::vector<char> get_transponder_ID();
  
  /*
   *get funktion for the boolean indicating if a id was found.
   */
  bool get_found_id();

   /*
   *returns true, if the sequences match
   */
  bool check_start_sequence(std::vector<char> sequence, std::vector<char> sequence_to_check);
  

  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_CHECKID_BB_H */
