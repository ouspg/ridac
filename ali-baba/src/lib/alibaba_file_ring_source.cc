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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <alibaba_file_ring_source.h>
#include <gr_io_signature.h>
#include <cstdio>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdexcept>

#include <stdio.h> //for remove, fseek

// win32 (mingw/msvc) specific
#ifdef HAVE_IO_H
#include <io.h>
#endif
#ifdef O_BINARY
#define	OUR_O_BINARY O_BINARY
#else
#define	OUR_O_BINARY 0
#endif
// should be handled via configure
#ifdef O_LARGEFILE
#define	OUR_O_LARGEFILE	O_LARGEFILE
#else
#define	OUR_O_LARGEFILE 0
#endif

alibaba_file_ring_source::alibaba_file_ring_source (size_t itemsize)
  : gr_sync_block ("file_ring_source",
		   gr_make_io_signature (0, 0, 0),
		   gr_make_io_signature (1, 1, itemsize)),
    d_itemsize (itemsize), d_fp (NULL), d_open_file_index (0), next_file (true)
{

}

void 
alibaba_file_ring_source::set_open_file_index(int n)
{
  int nfiles = this->d_str_filename_vector.size();
  if(nfiles != 0)
    this->d_open_file_index = n % nfiles;
  else
    this->d_open_file_index = n; 
}

void 
alibaba_file_ring_source::append_filename(std::string s)
{
  this->d_str_filename_vector.push_back(s);
  this->d_open_file_index %= this->d_str_filename_vector.size();
}



int
alibaba_file_ring_source::proceed_to_file()
{
  void * old_fp = d_fp;

  // we use "open" to use to the O_LARGEFILE flag
  const char * filename 
    = this->d_str_filename_vector[this->d_open_file_index].c_str();

  int fd;
  if ((fd = open (filename, O_RDONLY | OUR_O_LARGEFILE | OUR_O_BINARY)) < 0)
  {
    perror (filename);
    if(d_fp != NULL)
      if (fseek ((FILE *) d_fp, 0, SEEK_SET) == -1) {
	fprintf(stderr, "[%s] fseek failed\n", __FILE__);
	
	fclose ((FILE *) d_fp);
	this->d_fp = NULL;
	
	exit(-1);
      }


    return 1;
  }

  if ((d_fp = fdopen (fd, "rb")) == NULL){
    d_fp = old_fp;
    perror (filename);
    if(d_fp != NULL)
      if (fseek ((FILE *) d_fp, 0, SEEK_SET) == -1) {
	fprintf(stderr, "[%s] fseek failed\n", __FILE__);
	
	fclose ((FILE *) d_fp);
	this->d_fp = NULL;
	
	exit(-1);
    }
    return 1;
  }
  
  if( remove(filename) != 0 ){
    perror( "Error deleting file" );
    throw std::runtime_error ("can't delete file");
  }

  if(old_fp != NULL){
    fclose ((FILE *) old_fp);
    old_fp = NULL;
  }

  this->d_open_file_index ++;
  this->d_open_file_index %=  this->d_str_filename_vector.size();
  return 0;
}

// public constructor that returns a shared_ptr

alibaba_file_ring_source_sptr
alibaba_make_file_ring_source (size_t itemsize)
{
  return alibaba_file_ring_source_sptr (new alibaba_file_ring_source (itemsize));
}

alibaba_file_ring_source::~alibaba_file_ring_source ()
{
  if(d_fp != NULL)
    fclose ((FILE *) d_fp);
}

int 
alibaba_file_ring_source::work (int noutput_items,
			   gr_vector_const_void_star &input_items,
			   gr_vector_void_star &output_items)
{
  char *o = (char *) output_items[0];
  int i;
  int size = noutput_items;

  if(this->next_file)
    this->proceed_to_file();      

  while (size) {
    i = 0;
    if(this->d_fp != NULL){
      i = fread(o, d_itemsize, size, (FILE *) d_fp);
      size -= i;
      o += i * d_itemsize;
    }

    if (size == 0)		// done
      break;

    if (i > 0)			// short read, try again
      continue;

    // We got a zero from fread.  This is either EOF or error.  In
    // any event,try to proceed to next file 
    next_file = true;

    break;  
  }

  if (size > 0){			// EOF or error
    //if (size == noutput_items)	// we didn't read anything; say we're done
    //  return -1;
    return noutput_items - size;	// else return partial result
  }

  return noutput_items;
}


