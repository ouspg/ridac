#
# Copyright 2004,2005,2006,2008 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

include $(top_srcdir)/Makefile.common

# Install this stuff so that it ends up as the gnuradio.howto module
# This usually ends up at:
#   ${prefix}/lib/python${python_version}/site-packages/gnuradio

ourpythondir = $(grpythondir)
ourlibdir    = $(grpyexecdir)

AM_CPPFLAGS = $(STD_DEFINES_AND_INCLUDES) $(PYTHON_CPPFLAGS) $(WITH_INCLUDES)

SWIGPYTHONARGS = $(SWIGPYTHONFLAGS) $(SWIGGRFLAGS) $(WITH_SWIG_INCLUDES) \
	$(WITH_INCLUDES)

ALL_IFILES = 				\
	$(LOCAL_IFILES)			\
	$(NON_LOCAL_IFILES)		

NON_LOCAL_IFILES =			\
	$(GNURADIO_CORE_INCLUDEDIR)/swig/gnuradio.i


LOCAL_IFILES = 				\
	$(top_srcdir)/src/lib/alibaba.i				

# These files are built by SWIG.  The first is the C++ glue.
# The second is the python wrapper that loads the _alibaba shared library
# and knows how to call our extensions.

BUILT_SOURCES = 			\
	alibaba.cc			\
	alibaba.py				

# This gets alibaba.py installed in the right place
ourpython_PYTHON =			\
	alibaba.py

ourlib_LTLIBRARIES = _alibaba.la

# These are the source files that go into the shared library
_alibaba_la_SOURCES = 			\
	alibaba.cc			\
	alibaba_controlled_signalsource_bc.cc	\
	alibaba_checkid_bb.cc		\
	alibaba_fsk_demodulator_fb.cc	\
	alibaba_combine_symbols_bb.cc	\
	alibaba_char_converter_bch.cc	\
	alibaba_blocksplitter_ff.cc	\
	alibaba_square_ff.cc		\
	alibaba_normalizer_ff.cc	\
	alibaba_file_sink_hex.cc	\
	alibaba_mimadecoder_fb.cc	\
	alibaba_readersource_bf.cc	\
	alibaba_tagsource_bf.cc         \
	alibaba_sequence_repeater_bb.cc	\
	alibaba_file_ring_source.cc


# magic flags
_alibaba_la_LDFLAGS = $(NO_UNDEFINED) -module -avoid-version

# link the library against some comon swig runtime code and the 
# c++ standard library
_alibaba_la_LIBADD = 			\
	$(PYTHON_LDFLAGS)		\
	-lstdc++			

alibaba.cc alibaba.py: $(LOCAL_IFILES) $(ALL_IFILES)
	$(SWIG) $(SWIGPYTHONARGS) -module alibaba -o alibaba.cc $(LOCAL_IFILES)

# These headers get installed in ${prefix}/include/gnuradio
grinclude_HEADERS =			\
	alibaba_controlled_signalsource_bc.h	\
	alibaba_checkid_bb.h		\
	alibaba_fsk_demodulator_fb.h	\
	alibaba_combine_symbols_bb.h	\
	alibaba_char_converter_bch.h	\
	alibaba_blocksplitter_ff.h	\
	alibaba_square_ff.h		\
	alibaba_normalizer_ff.h		\
	alibaba_file_sink_hex.h		\
	alibaba_mimadecoder_fb.h	\
	alibaba_readersource_bf.h	\
	alibaba_tagsource_bf.h		\
	alibaba_sequence_repeater_bb.h	\
	alibaba_file_ring_source.h

# These swig headers get installed in ${prefix}/include/gnuradio/swig
swiginclude_HEADERS = 			\
	$(LOCAL_IFILES)


MOSTLYCLEANFILES = $(BUILT_SOURCES) *.pyc

# Don't distribute output of swig
dist-hook:
	@for file in $(BUILT_SOURCES); do echo $(RM) $(distdir)/$$file; done
	@for file in $(BUILT_SOURCES); do $(RM) $(distdir)/$$file; done
