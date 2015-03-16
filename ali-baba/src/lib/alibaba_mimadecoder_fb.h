#ifndef INCLUDED_ALIBABA_MIMADECODER_FB_H
#define INCLUDED_ALIBABA_MIMADECODER_FB_H

#include <gr_block.h>

class alibaba_mimadecoder_fb;

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
typedef boost::shared_ptr<alibaba_mimadecoder_fb> alibaba_mimadecoder_fb_sptr;

/*!
 * This class is supposed to find out which data encoding schemes the blocks within a communication have. 
 * Supported communication schemes are Modified Miller and Manchester encoding (as used by 14443-A).
 * Either Miller encoded or Manchester encoded data is decoded into bytes and outputed seperated by a seperation value for either manchester or miller decoded data.
 * Precondition: The communicatin blocks at the input side have to be separated by a separation value given in block_separation_value.
 * Errors that are outputed to the output stream:
 * "-1" error during decoding
 * "-2" error during parity check
 * "-3" CRC error
 * @param sampling_frequency the sampling frequency
 * @param data_rate the data rate of the encoded tata
 * @param thres_mi indicates the decision threshold for a binary one and a binary zero
 * @param thres_ma indicates the decision threshold for a binary one and a binary zero
 * @param block_separation_value gives the value with which two blocks are separated.
 * @param decode_miller_or_manchester indicates, wheather manchester encoded data (1) or miller encoded data (2) or both (0)is decoded and outputed
 * @param separation_value_for_manchester indicator for manchester decoded data in output stream
 * @param separation_value_for_miller indicator for miller decoded data in output stream
 * @param enable_parity_check enables parity check for each byte.
 * @param enable_crc_check enables crc check for each block.
 */
alibaba_mimadecoder_fb_sptr alibaba_make_mimadecoder_fb (float sampling_frequency, float data_rate, float thres_mi, float thres_ma, char decode_miller_or_manchester, float block_separation_value, char separation_value_for_miller, char separation_value_for_manchester, bool enable_parity_check, bool enable_crc_check, int* send_state);

/*!
 * This class is supposed to find out which data encoding schemes the blocks within a communication have. 
 * Supported communication schemes are Modified Miller and Manchester encoding (as used by 14443-A).
 * Either Miller encoded or Manchester encoded data is decoded into bytes and outputed seperated by a seperation value for either manchester or miller decoded data.
 * Precondition: The communicatin blocks at the input side have to be separated by a separation value given in block_separation_value.
 * Errors that are outputed to the output stream:
 * "-1" error during decoding
 * "-2" error during parity check
 * "-3" CRC error
 */
class alibaba_mimadecoder_fb : public gr_block
{
private:
  // The friend declaration allows alibaba_make_demodulate_ff to
  // access the private constructor.

  friend alibaba_mimadecoder_fb_sptr alibaba_make_mimadecoder_fb (float sampling_frequency, float data_rate, float thres_mi, float thres_ma, char decode_miller_or_manchester, float block_separation_value, char separation_value_for_miller, char separation_value_for_manchester, bool enable_parity_check, bool enable_crc_check, int* send_state);

  alibaba_mimadecoder_fb (float sampling_frequency, float data_rate, float thres_mi, float thres_ma, char decode_miller_or_manchester, float block_separation_value, char separation_value_for_miller, char separation_value_for_manchester, bool enable_parity_check, bool enable_crc_check, int* send_state);  	// private constructor
  int output_function(std::vector<short> *out_buffer, short *out, int available_output_items, int out_counter);



  /**
   * Funcitions used to calculate the CRC according to the ISO 14443-3 (Type A) Standard. The Code is closely related to
   * the sample code found in Annex B of the ISO 14443-3 Standard document.
   */
  void ComputeCrc(unsigned char *Data, int Length,unsigned char *TransmitFirst, unsigned char *TransmitSecond);
  unsigned short UpdateCrc(unsigned char ch, unsigned short *lpwCrc);
  
  /**
   * converts bits into bytes and checks the parity!
   */
  short convertIntoBytes(std::vector<char> buffer);

  /**
   * handle Iso 14443 commands, that are only 7 bit long.
   * Supported commands: Req-A (0x26), Wake-up (0x52), optional time slot (0x35) 
   * But all other commands are also converted and outputed.
   */
  short convertSevenBitCommandsIntoBytes(std::vector<char> buffer);


  
  /**
   * function that is called for decoding of blocks
   */
  std::vector<short> decodeBlock(std::vector<float> buffer,char encoding, float threshold);
  
  /**
   * performs Manchester decoding.
   */
  char decodeManchester(std::vector<char>& symbol_buffer, std::vector<float>& buffer, int ones_in_first_half, int ones_in_second_half);
   /**
   * performs modified Miller decoding.
   */
  char decodeModifiedMiller(std::vector<char>& symbol_buffer, std::vector<float>& buffer, int ones_in_first_half, int ones_in_second_half);

  int check_modified_miller_encoding(std::vector<float> buff);
  int check_manchester_encoding(std::vector<float> buff);

  float sampling_frequency_;
  float data_rate_;
  int samples_per_symbol_;
  float thres_mi_;
  float thres_ma_;
  float separation_val_;
  char separation_value_for_miller_;
  char separation_value_for_manchester_;
  char decode_miller_or_manchester_;
  bool enable_parity_check_;
  bool enable_crc_check_;
  int state;
  int encoding_scheme;
  char last_symbol;
  bool initial_fill;
  bool split_block;
  int initial_fill_count;
  std::vector<float> tmp_buffer;
  std::vector<float> tmp_out_buffer;
  std::vector<short> out_buffer;
  int* send_state_;

 public:
  ~alibaba_mimadecoder_fb ();	// public destructor

  // Where all the action really happens

  int general_work (int noutput_items,
		    gr_vector_int &ninput_items,
		    gr_vector_const_void_star &input_items,
		    gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_MIMADECODER_FB_H */
