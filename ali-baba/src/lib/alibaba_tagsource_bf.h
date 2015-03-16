#ifndef INCLUDED_ALIBABA_TAGSOURCE_BF_H
#define INCLUDED_ALIBABA_TAGSOURCE_BF_H

#include <gr_sync_block.h>

#include <map>
#include <iostream>
#include <fstream>

using namespace std;

class alibaba_tagsource_bf;

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
typedef boost::shared_ptr<alibaba_tagsource_bf> alibaba_tagsource_bf_sptr;

/*!
 * This class takes a binary stream of data and and generates samples according to the 14443-2 
 * communication for a transponder (Miller encoded). The class outputs a constant amplitude, if carryer should be on and
 * zero, if carryer should be off. If there is no communication, the carryer is off! 
 * The transmition unit has to be tuned to 847.5KHz, 
 * to generate a 847.5Khz carryer, if the output of this class is different than zero.
 * @param sampling_frequency the sampling frequency
 * @param data_rate the data rate, the information is modulated onto the carryer
 * @param amplitude the amplitude of the signal.
 */
alibaba_tagsource_bf_sptr alibaba_make_tagsource_bf (float sampling_frequency, float data_rate, float amplitude, int* send_state, string source_filename);

/*!
 * This class takes a binary stream of data and and generates samples according to the 14443-2 
 * communication for a transponder (Miller encoded). The class outputs a constant amplitude, if carryer should be on and
 * zero, if carryer should be off. If there is no communication, the carrier is off! 
 * The transmition unit has to be tuned to 847.5KHz, 
 * to generate a 847.5Khz carrier, if the output of this class is different than zero.
 */
class alibaba_tagsource_bf : public gr_sync_block
{
private:


  friend alibaba_tagsource_bf_sptr alibaba_make_tagsource_bf (float sampling_frequency, float data_rate, float amplitude, int* send_state, string source_filename);

  alibaba_tagsource_bf (float sampling_frequency, float data_rate, float amplitude, int* send_state, string source_filename);  	// private constructor

  int output_function(std::vector<float> &out_buffer, float *out, int available_output_items, int out_counter);

  unsigned char hex_to_int(unsigned char value);

  vector<unsigned char> convertToNumbers(vector<unsigned char> input);

  vector<unsigned char> convertToBinaryAndAddParity(vector<unsigned char> input);

  map<vector<unsigned char> ,vector<unsigned char> > readFromFile(string filename);



  
  map<vector<unsigned char> ,vector<unsigned char> > comm_elements_;
  float sampling_frequency_;
  float data_rate_;
  int samples_per_symbol_;
  float amplitude_;
  std::vector<float> tmp_buffer;
  int* send_state_;

 public:
  ~alibaba_tagsource_bf ();	// public destructor

  // Where all the action really happens

  int work (int noutput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_TAGSOURCE_BF_H */
