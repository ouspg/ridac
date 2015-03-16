/* -*- c++ -*- */
/*
 * Copyright 2004,2007 Free Software Foundation, Inc.
 * 
 * This file is part of GNU Radio
 * 
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 * 
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_ALIBABA_FILE_SINK_HEX_H
#define INCLUDED_ALIBABA_FILE_SINK_HEX_H

#include <gr_block.h>
#include <gr_file_sink_base.h>

class alibaba_file_sink_hex;
typedef boost::shared_ptr<alibaba_file_sink_hex> alibaba_file_sink_hex_sptr;

  /** 
   * Code based on the alibaba_file_sink. It takes unsigned char items and writes them to a file char file in hex-Format.
   * If a block separation value accures, it is handled as Return.
   * @param itemsize: always has to be char!
   * @param filename: the filename
   * @param separation_value_reader: the indicator that a reader communication block starts...
   * @param separation_value_tag: the indicator that a tag communication block starts...
   * @param separate_by_space: if true, a space is added after every single value.
   */

alibaba_file_sink_hex_sptr alibaba_make_file_sink_hex(size_t itemsize, const char *filename,char separation_value_reader, char separation_value_tag ,bool separate_by_space);

  /** 
   * Code based on the alibaba_file_sink. It takes unsigned char items and writes them to a file char file in hex-Format.
   * If a block separation value accures, it is handled as Return.
   */

class alibaba_file_sink_hex : public gr_block, public gr_file_sink_base
{
  friend alibaba_file_sink_hex_sptr alibaba_make_file_sink_hex(size_t itemsize, const char *filename,char separation_value_reader, char separation_value_tag ,bool separate_by_space);

 private:
  size_t	d_itemsize;
  char separation_value_miller_;
  char separation_value_manchester_;
  bool seperate_by_space_;
  std::vector<unsigned char> tmp_buffer;

  
 /**
  *Function that takes a char value and converts one nipple into a hexadezimal char representation.
  *@param value: the char value
  *@param upper_nipple: converts the most significant nipple, if true. The least significant nipple, if false.
  */
 unsigned char hex_converter(unsigned char value, bool upper_nipple);

 protected:
  alibaba_file_sink_hex(size_t itemsize, const char *filename,char separation_value_reader, char separation_value_tag ,bool separate_by_space);

 public:
  ~alibaba_file_sink_hex();

  int general_work (int noutput_items,
			       gr_vector_int &ninput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items);
};

#endif /* INCLUDED_ALIBABA_FILE_SINK_HEX_H */
