/* -*- c++ -*- */

%feature("autodoc", "1");		// generate python docstrings

%include "exception.i"
%import "gnuradio.i"			// the common stuff

%{
#include "gnuradio_swig_bug_workaround.h"	// mandatory bug fix

#include "alibaba_controlled_signalsource_bc.h"
#include "alibaba_checkid_bb.h"
#include "alibaba_fsk_demodulator_fb.h"
#include "alibaba_combine_symbols_bb.h"
#include "alibaba_char_converter_bch.h"
#include "alibaba_blocksplitter_ff.h"
#include "alibaba_mimadecoder_fb.h"
#include "alibaba_square_ff.h"
#include "alibaba_normalizer_ff.h"
#include "alibaba_file_sink_hex.h"
#include "alibaba_readersource_bf.h"
#include "alibaba_tagsource_bf.h"
#include "alibaba_sequence_repeater_bb.h"
#include "alibaba_file_ring_source.h"
#include <stdexcept>


%}



%include "cpointer.i"

/* Create some functions for working with "int *" */
%pointer_functions(int, intp);

%include "std_string.i"
%include "std_vector.i"
namespace std {
   %template(ShortVector) vector<short>;
   %template(CharVector) vector<char>;
}




// ----------------------------------------------------------------


GR_SWIG_BLOCK_MAGIC(alibaba,controlled_signalsource_bc);


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
  alibaba_controlled_signalsource_bc (double sampling_freq, double frequency_one,
double frequency_zero, double ampl, gr_complex offset, int zycles_per_symbol);
};




// ----------------------------------------------------------------


GR_SWIG_BLOCK_MAGIC(alibaba,checkid_bb);


/*!
 * This class checks a binary stream for id. It has a public member "id_found", that
 * is changed to true if a valid id could be found.
 * @ param starting_sequence: the binary start sequence of the id
 * @ param how_many_equals: indicates how many equal ids have to be found, that 
 */
alibaba_checkid_bb_sptr alibaba_make_checkid_bb (std::vector<char> starting_sequence, int how_many_equals);


/*!
 * This class checks a binary stream for id. It has a boolean member "id_found", that
 * is changed to true if a valid id could be found
 */
class alibaba_checkid_bb : public gr_block
{
private:
  alibaba_checkid_bb (std::vector<char> starting_sequence, int how_many_equals);
public:
  /*!
   *get funktion for the boolean indicating if a id was found.
   */
  bool get_found_id();
  std::vector<char> get_transponder_ID();
};

// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC(alibaba,fsk_demodulator_fb);


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
  alibaba_fsk_demodulator_fb (float sampling_frequency, float frequency_one, float frequency_zero);
};

// ----------------------------------------------------------------

/*
 * First arg is the package prefix.
 * Second arg is the name of the class minus the prefix.
 *
 * This does some behind-the-scenes magic so we can
 * access combine_binarysymbols_bb from python as combine.binarysymbols_bb
 */
GR_SWIG_BLOCK_MAGIC(alibaba,combine_symbols_bb);


/*
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
  alibaba_combine_symbols_bb (int min_number_of_symbols_representing_one_binary_value, int max_number_of_symbols_representing_one_binary_value);
};

// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC(alibaba,char_converter_bch);

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
  alibaba_char_converter_bch ();
};


// ----------------------------------------------------------------

/*
 * First arg is the package prefix.
 * Second arg is the name of the class minus the prefix.
 */
GR_SWIG_BLOCK_MAGIC(alibaba,blocksplitter_ff);


/*!
 * This class searches for a long sequence of zeros (how_many) and replaces them 
 * with the number block_separation_value. This is used to separate communication blocks
 * between tag and reaer. The offset parameter is used to set a limit for the 
 * decision zero/one.
 * @ param offset: the edge for decision zero/one
 * @ param how_many: how many zeros have to pass between blocks...
 * @ param block_separation_value: value that is placed instead of a series of zeros to separate blocks
 */
alibaba_blocksplitter_ff_sptr alibaba_make_blocksplitter_ff (float offset, int how_many, float block_separation_value);


/*!
 * This class searches for a long sequence of zeros (how_many) and replaces them 
 * with the number -100000. This is used to separate communication blocks
 * between tag and reaer. The offset parameter is used to set a limit for the 
 * decision zero/one.
 */
class alibaba_blocksplitter_ff : public gr_block
{
private:
  alibaba_blocksplitter_ff (float offset, int how_many, float block_separation_value);
};

// ----------------------------------------------------------------


GR_SWIG_BLOCK_MAGIC(alibaba, square_ff);


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
  alibaba_square_ff ();
};

// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC(alibaba, normalizer_ff);


/*!
 * This class takes a stream of blocks separated by block_separation_value and
 * searches for the maximum value in one of this blocks. After that it normalizes
 * the whole block to the value_to_normalize_to (maximum value is not higher than value_to_normalize_to)
 * it outputs a stream of normalized blocks separated by block_separation_value.
 * @ param block_separation_value: the value that indicates the start of a new block
 * @ param value_to_normalize_to: is the value that block has to be normalized to
 */
alibaba_normalizer_ff_sptr alibaba_make_normalizer_ff (float block_separation_value, float value_to_normalize_to);


/*!
 * This class takes a stream of blocks separated by block_separation_value and
 * searches for the maximum value in one of this blocks. After that it normalizes
 * the whole block to the value_to_normalize_to (maximum value is not higher than value_to_normalize_to)
 * it outputs a stream of normalized blocks separated by block_separation_value.
 */
class alibaba_normalizer_ff : public gr_block
{
private:
  alibaba_normalizer_ff (float block_separation_value, float value_to_normalize_to);
};


// ----------------------------------------------------------------


GR_SWIG_BLOCK_MAGIC(alibaba,file_sink_hex)

  /** 
   * Code based on the gr_file_sink. It takes unsigned char items and writes them to a file char file in hex-Format.
   * If a block separation value accures, it is handled as Return.
   * @param itemsize: always has to be char!
   * @param filename: the filename
   * @param separation_value_reader: the indicator that a reader communication block starts...
   * @param separation_value_tag: the indicator that a tag communication block starts...
   * @param block_separation_value: the indicator that a new block starts...
   * @param separate_by_space: if true, a space is added after every single value.
   */
alibaba_file_sink_hex_sptr 
alibaba_make_file_sink_hex (size_t itemsize, const char *filename,char separation_value_reader, char separation_value_tag ,bool separate_by_space);

  /** 
   * Code based on the gr_file_sink. It takes unsigned char items and writes them to a file char file in hex-Format.
   * If a block separation value accures, it is handled as Return.
   */
class alibaba_file_sink_hex : public gr_block, public gr_file_sink_base
{
 protected:
  alibaba_file_sink_hex (size_t itemsize, const char *filename,char separation_value_reader, char separation_value_tag ,bool separate_by_space);

 public:
  ~alibaba_file_sink_hex ();

  /*! 
   * \brief open filename and begin output to it.
   */
  bool open(const char *filename);

  /*!
   * \brief close current output file.
   */
  void close();
};

// ----------------------------------------------------------------


GR_SWIG_BLOCK_MAGIC(alibaba,mimadecoder_fb);


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
  alibaba_mimadecoder_fb (float sampling_frequency, float data_rate, float thres_mi, float thres_ma, char decode_miller_or_manchester, float block_separation_value, char separation_value_for_miller, char separation_value_for_manchester, bool enable_parity_check, bool enable_crc_check, int* send_state);
  //static short sequence_number_;
};


// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC(alibaba, readersource_bf);


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
  alibaba_readersource_bf (float sampling_frequency, float data_rate, float amplitude);
};

// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC(alibaba, tagsource_bf);


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
alibaba_tagsource_bf_sptr alibaba_make_tagsource_bf (float sampling_frequency, float data_rate, float amplitude, int* send_state, std::string source_filename);

/*
 * This class takes a binary stream of data and and generates samples according to the 14443-2 
 * communication for a transponder (Miller encoded). The class outputs a constant amplitude, if carryer should be on and
 * zero, if carryer should be off. If there is no communication, the carryer is off! 
 * The transmition unit has to be tuned to 847.5KHz, 
 * to generate a 847.5Khz carryer, if the output of this class is different than zero.
 */
class alibaba_tagsource_bf : public gr_sync_block
{
private:
  alibaba_tagsource_bf (float sampling_frequency, float data_rate, float amplitude, int* send_state, std::string source_filename);
};



// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC(alibaba, sequence_repeater_bb);


/*!
 *  
 */
alibaba_sequence_repeater_bb_sptr alibaba_make_sequence_repeater_bb ();


/*!
 * 
 */
class alibaba_sequence_repeater_bb : public gr_block
{
private:
  alibaba_sequence_repeater_bb ();

public:
  ~alibaba_sequence_repeater_bb ();

  int get_offset();
  void set_offset(int n);

  int get_sequence_length();
  void set_sequence_length(int n);
  
  int get_repeat_count();
  void set_repeat_count(int n);
  
};

// ----------------------------------------------------------------

GR_SWIG_BLOCK_MAGIC(alibaba, file_ring_source);


/*!
 *  
 */
alibaba_file_ring_source_sptr alibaba_make_file_ring_source (size_t itemsize);


/*!
 * 
 */
class alibaba_file_ring_source : public gr_sync_block
{
private:
  alibaba_file_ring_source (size_t itemsize);

public:
  ~alibaba_file_ring_source ();
  void append_filename(std::string s);
  int get_open_file_index();
  void set_open_file_index(int n);

};

