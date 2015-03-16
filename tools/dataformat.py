import array
import csv
import math
import os  

concat = lambda l: [j for i in l for j in i]


def popBitsFromArray(aArray, digits):
    while aArray:
        c = aArray.pop(0)
        bits = [ (c>>i)%2 for i in range(digits)]
        bits.reverse()
        for b in bits:
            yield b


class Sequence:
    goodbases =    {2:1,8:3,16:4,256:8}
    def __init__(self, s, base=2):
        if base not in self.goodbases:
            raise ValueError("%d not in supported bases"%base+str(self.goodbases))
        self.base = base
        if base != 256:
            self.data = array.array('B',[int(i, base=base) for i in s])
        else:
            self.data = array.array('B',[ord(i) for i in s])
            
    def setBase(self, nBase):
        if nBase not in self.goodbases:
            raise ValueError("%d not in supported bases"%nBase+str(self.goodbases))
        
        nBits = self.goodbases[nBase]
        oldBits = self.goodbases[self.base]
        nArray = array.array('B')
        
        bitCntr = 0
        c = 0
        for b in popBitsFromArray(self.data, oldBits):
            c<<=1
            c+=b
            bitCntr += 1
            if bitCntr == nBits:
                nArray.append(c)
                bitCntr = 0
                c = 0
        if c != 0:
            c<<= nBits - bitCntr
            nArray.append(c)
        

        self.base = nBase
        self.data = nArray
                
    def __repr__(self):
        prints = {
            2:str,
            8:lambda d: "%o"%d,
            16:lambda d: "%x"%d,
            256:chr
            }
        f = prints[self.base]
        return "".join(map(f,self.data))+"_%d"%self.base




def getBase(s):
    try:
        return int(s.split('_')[-1])
    except IndexError:
        return 256
    except ValueError:
        return 256
            
def getHeader(s):
    return s.split('_')[0]


class MyCsvData:
    def __init__(self, aFileName):
        """list of unsigned int data """
        self.aFileName = aFileName
        
        self.headerBases = None
        
        try:
            f = open(aFileName,'rb')
            reader = csv.DictReader(f)
            reader.next()

            self.headerBases = dict(
                [(getHeader(i), getBase(i)) for i in reader.fieldnames]
                )
            f.close()
        except IOError:
            pass
        except StopIteration:
            f.close()
            pass
        
    
    def getFields(self,headersWithBases ):
        try:
            f = open(self.aFileName,'rb')
            reader = csv.DictReader(f)
            for row in reader:
                r = []
                for h in headersWithBases:
                    v = row.get(h,None)
                    if v != None:
                        v = Sequence(v,self.headerBases[h])
                        v.setBase(headersWithBases[h])
                        r.append(v)
                yield r
            f.close()
        except IOError:
            raise StopIteration




    def writeFields(self, fieldYielder, fieldNames= None):
        tmpName = os.tempnam()
        tmpFile = os.open(tmpName,'wb')
        writer = csv.DictWriter(tmpFile, fieldNames)
        for row in fieldYielder:
            writer.writerow(row)
        tmpFile.close()
        os.rename(tmpName, self.aFileName)

def test():    
    import sys
    sys.excepthook = None
    a = MyCsvData("testi1.csv")
    for i in a.getFields({'text':2}):
        print i
                        
    
    

