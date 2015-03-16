/* -*- c++ -*- */
/*
 * Copyright 2004 Free Software Foundation, Inc.
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

#ifndef INCLUDED_ALIBABA_FILE_RING_SOURCE_H
#define INCLUDED_ALIBABA_FILE_RING_SOURCE_H

#include <gr_sync_block.h>

#include <vector>
#include <string>
#include <iostream>



class alibaba_file_ring_source;
typedef boost::shared_ptr<alibaba_file_ring_source> alibaba_file_ring_source_sptr;

alibaba_file_ring_source_sptr
alibaba_make_file_ring_source (size_t itemsize);

/*!
 * \brief Read stream from file
 * \ingroup source
 */

class alibaba_file_ring_source : public gr_sync_block
{
  

 private:
  size_t	d_itemsize;
  void	       *d_fp;
  int d_open_file_index;
  bool next_file;
  std:: vector <std::string> d_str_filename_vector;
  
  friend alibaba_file_ring_source_sptr alibaba_make_file_ring_source (size_t itemsize);
  alibaba_file_ring_source (size_t itemsize);
  

  int proceed_to_file();

 public:      
  ~alibaba_file_ring_source ();

  int work (int noutput_items,
	    gr_vector_const_void_star &input_items,
	    gr_vector_void_star &output_items);

    

  void append_filename(std::string s);

  int get_open_file_index() {return this->d_open_file_index;}
  void set_open_file_index(int n);

};

#endif /* INCLUDED_ALIBABA_FILE_RING_SOURCE_H */
