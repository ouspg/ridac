def read_complex_file(fname, fs):
    a = array.array("f")
    bf = open(fname, "rb")
    bf.seek(0,2)
    length = bf.tell()
    bf.seek(0)
    a.fromfile(bf,length/4)
    bf.close()
    b = array.array("f")
    real = [ a[i] for i in xrange(0, len(a), 2) ]
    imag = [ a[i] for i in xrange(1, len(a), 2) ]
    t = [ float(x)/fs for x in xrange(0, length/8) ]
    return real, imag, t
