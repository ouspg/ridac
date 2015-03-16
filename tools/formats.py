"""
This file contains own encoding functions
"""


toInts = lambda l: [int(i) for i in l]
takeOne = lambda l,n: [i[n] for i in l]

heads = lambda l: [l[i:] for i in range(len(l))]
tails = lambda l: [l[:i+1] for i in range(len(l))]

concat = lambda l: [j for i in l for j in i] 
toStr = lambda i: "".join(map(str,i))

neg = lambda b: {'0':'1',0:1,'1':'0',1:0}[b]

"""the IEEE 802.5"""
standardManchester = lambda b:[ [0,1],[1,0]][b] 

startSeq = [0,0,0,1,1,1]
manchester = lambda bits: startSeq + concat( [
    standardManchester(i) for i in bits
    ])

evenBit = lambda bits: sum(bits )%2

oddBit = lambda bits:  ( evenBit(bits) +1 )%2

wiegandParities = lambda bits: concat([
        [evenBit(bits[:len(bits)/2])],
        bits[:len(bits)/2],
        bits[len(bits)/2:],
        [oddBit(bits[len(bits)/2:])]
        ])

manchesterDecode = lambda k : [ v for i,v in enumerate(k[6:]) if i%2 == 0]


#def shufflebits(bits,order): [bits[i] for i in order]
    

dataFrame = lambda data, standardFrameStart :  standardFrameStart + wiegandParities(data)

def tobits(x,digits=16):
    r = []    
    for i in range(digits):
        r.insert(0,x % 2)
        x >>= 1
    return r

toInteger = lambda k: sum([v*2**(len(k)-1-i) for i,v in enumerate(k)])


frameStart = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
def makeKeyFromInteger(i, standardFrameStart = frameStart):
    return manchester(dataFrame(tobits(i,digits=24),standardFrameStart))

toBCD = lambda n: [ toStr(tobits(int(d),4)) for d in str(n) ]



def getFormatPipe():
    formatFncs = []
    def processFormats(aId):
        for format in formatFncs:
            aId = format(aId)
        return aId
    return processFormats, formatFncs



def addEncodingOptions(parser):
    parser.add_option(
        "-w",
        "--wiegand",
        default=True,
        action = 'store_false',
        help="wiegand parities off")

    parser.add_option(
        "-m",
        "--manchester",
        default=True,
        action = 'store_false',
        help="manchester  IEEE 802.5 -encoding off")

    parser.add_option(
        "-s",
        "--payload-start-sequence",
        default= "".join(map(str,frameStart)),
        help="start sequence (before wiegand. default is %s)"%"".join(map(str,frameStart)))
    
    parser.add_option(
        "-l",
        "--payload-length",
        default="24",
        help="set the amount of bits of the payload.default is 24")

    parser.add_option(
        "-o",
        "--order-of-bits",
        default = None,
        help="set the order of bits in the id payload field. default is MSB first order. The index of LSB is 0 and separate ints by ','.")


def parseOptions(options):
    options.payload_length = int(options.payload_length)
    options.payload_start_sequence = toInts(options.payload_start_sequence.strip('"\''))
    if set(options.payload_start_sequence) not in [set([0,1]), set([0]), set([1]), set([])]:
        raise ValueError('invalid start sequence')
    if options.order_of_bits != None:
        try:
            options.order_of_bits = map(int,options.order_of_bits.split(','))
            if len(list(set(options.order_of_bits))) != options.payload-length:
                raise ValueError('invalid order of bits')
        except:
            raise ValueError('invalid order of bits')
    


def setRfidFormatPipe(options, formatFncs):
    formatFncs.append(
        lambda aId: tobits(aId, options.payload_length)
        )

    if options.order_of_bits:            
        formatFncs.append(
            lambda aId: [aId[i] for i in options.order_of_bits]
            )

    if options.wiegand:
        formatFncs.append(
            lambda aId: wiegandParities(aId)
            )

    formatFncs.append(
        lambda aId: options.payload_start_sequence + aId
        )
    
        
    if options.manchester:
        formatFncs.append(
            lambda aId: manchester(aId)
            )

    formatFncs.append(
        lambda aId: toStr(aId)
        )
