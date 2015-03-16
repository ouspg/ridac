import array
import random
from optparse import OptionParser



typecodes = 'cbBuhHiIlLfd'
repeats = 5

range_min = 0
range_max = 100

data_entries = 100

def get_number():
    return random.uniform(range_min, range_max)

def get_buffer(typecode):
    if typecode in 'cu':
        nmbr = get_number()
        nmbr = str(nmbr)
        if typecode == 'u':
            nmbr = unicode(nmbr)
        nmbr = nmbr [:repeats]
    else:
        nmbr = [get_number() for _ in range(repeats)]
    return array.array(typecode, nmbr).tostring()

def get_data_entry():
    return "".join([get_buffer(i) for i in typecodes])
        


def main():
    parser = OptionParser()
    parser.add_option(
        "-f", 
        "--output-file", 
        dest="file",
        help="""the output file. default is %default""", 
        default = "generated.raw"
        )
    (options, args) = parser.parse_args()

    e = get_data_entry()
    print 'an example data entry (with string escape):'
    print e.encode('string escape')
    print 'length of one data entry in bytes is', len(e)

    print 'typecode ; length of field in bytes ; an example entry using string escaping'
    for i in typecodes:
        print i, ';', len(get_buffer(i)), ';', get_buffer(i).encode('string escape')
    
    
    print 'number of written data entries is', data_entries
    print 'data entries are now written to the file', options.file

    f = open(options.file,'wb')
    for i in range(data_entries):
        f.write(get_data_entry())
    f.close()

main()
