/* -*- c++ -*- */
/*
 * Copyright 2004,2006,2007 Free Software Foundation, Inc.
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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alibaba_file_sink_hex.h>
#include <gr_io_signature.h>
#include <stdexcept>


alibaba_file_sink_hex_sptr
alibaba_make_file_sink_hex (size_t itemsize, const char *filename,char separation_value_reader, char separation_value_tag ,bool separate_by_space)
{
  return alibaba_file_sink_hex_sptr (new alibaba_file_sink_hex (itemsize, filename, separation_value_reader, separation_value_tag, separate_by_space));
}

static const int MIN_IN = 1;	// mininum number of input streams
static const int MAX_IN = 1;	// maximum number of input streams


alibaba_file_sink_hex::alibaba_file_sink_hex(size_t itemsize, const char *filename,char separation_value_reader, char separation_value_tag ,bool separate_by_space)
  : gr_block ("alibaba_file_sink_hex",
	      gr_make_io_signature (MIN_IN, MAX_IN, sizeof (short)),
	      gr_make_io_signature (0, 0, 0)),
    gr_file_sink_base(filename, true),
    d_itemsize(itemsize)
{
  if (!open(filename))
    throw std::runtime_error ("can't open file");

  separation_value_miller_=separation_value_reader;
  separation_value_manchester_=separation_value_tag;
  seperate_by_space_=separate_by_space;
  tmp_buffer.clear();
}

alibaba_file_sink_hex::~alibaba_file_sink_hex ()
{
}

unsigned char alibaba_file_sink_hex::hex_converter(unsigned char value, bool upper_nipple)
{
        
        unsigned char out_value='0'; //FIXME delete debug statement
        if(upper_nipple) value=value >> 4;
        value=value & 0x000F;

        switch(value)
        {
                case 0x00: out_value='0';
                        break;
                case 0x01: out_value='1';
                        break;
                case 0x02: out_value='2';
                        break;
                case 0x03: out_value='3';
                        break;
                case 0x04: out_value='4';
                        break;
                case 0x05: out_value='5';
                        break;
                case 0x06: out_value='6';
                        break;
                case 0x07: out_value='7';
                        break;
                case 0x08: out_value='8';
                        break;
                case 0x09: out_value='9';
                        break;
                case 0x0A: out_value='A';
                        break;
                case 0x0B: out_value='B';
                        break;
                case 0x0C: out_value='C';
                        break;
                case 0x0D: out_value='D';
                        break;
                case 0x0E: out_value='E';
                        break;
                case 0x0F: out_value='F';
                        break;
        }
        return out_value;
}

int 
alibaba_file_sink_hex::general_work (int noutput_items,
			       gr_vector_int &ninput_items,
			       gr_vector_const_void_star &input_items,
			       gr_vector_void_star &output_items)
{
  const short *in = (const short *) input_items[0];
  int  nwritten = 0;

  do_update();				// update d_fp is reqd
  
  if (!d_fp)
  {
        consume_each(noutput_items);
        return noutput_items;		// drop output on the floor
  }

  for (int i=0;i<noutput_items;i++) 
  {
    if(in[i]==separation_value_miller_) 
    {
        tmp_buffer.push_back('\n');
        tmp_buffer.push_back('R');
        tmp_buffer.push_back(':');
        tmp_buffer.push_back(' ');
        continue;
    }
    if(in[i]==separation_value_manchester_) 
    {
        tmp_buffer.push_back('\n');
        tmp_buffer.push_back('T');
        tmp_buffer.push_back(':');
        tmp_buffer.push_back(' ');
        continue;
    }
    if(in[i]==-1) 
    {
        tmp_buffer.push_back('M');//modified miller error
        if (seperate_by_space_) tmp_buffer.push_back(' ');
        continue;
    }
    if(in[i]==-2) 
    {    
        tmp_buffer.push_back('P');//parity check error
        if (seperate_by_space_) tmp_buffer.push_back(' ');
        continue;
    }
    if(in[i]==-3) 
    {
        tmp_buffer.push_back('C');//CRC check error
        if (seperate_by_space_) tmp_buffer.push_back(' ');
        continue;
    }
    if(in[i]==-4) 
    {
        tmp_buffer.push_back('\n');
        tmp_buffer.push_back('U');//Unknown Encoding
        if (seperate_by_space_) tmp_buffer.push_back(' ');
        continue;
    }
    
    else if(in[i]>=0)
    {
        tmp_buffer.push_back('0');
        tmp_buffer.push_back('x');
        tmp_buffer.push_back(hex_converter(in[i], true));
        tmp_buffer.push_back(hex_converter(in[i], false));
        if (seperate_by_space_) tmp_buffer.push_back(' ');
    }
  }

  int tmp_size=tmp_buffer.size();
  unsigned char out_array[tmp_size];
  std::copy(tmp_buffer.begin(), tmp_buffer.end(), out_array);

  while (nwritten < tmp_size){
    int count = fwrite (out_array, d_itemsize, noutput_items - nwritten, d_fp);
    if (count == 0)	// FIXME add error handling
      break;
    nwritten += count;
    in += count * d_itemsize;
  }
  tmp_buffer.erase(tmp_buffer.begin(), tmp_buffer.begin()+nwritten);
  consume_each (noutput_items);
  return nwritten;
}
