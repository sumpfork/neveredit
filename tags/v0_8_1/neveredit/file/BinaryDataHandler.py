import struct,string

class BinaryDataHandler:
    def readFromBuf(self,format,b):
        return struct.unpack(format,b)

    def readFromFile(self,format,f):
        b = f.read(struct.calcsize(format))
        return self.readFromBuf(format,b)
    
    def readIntBuf(self,d):
        return struct.unpack('<i',d)[0]

    def readIntFile(self,f):
        b = f.read(4)
        return self.readIntBuf(b)

    def readUIntBuf(self,d):
        return struct.unpack('<I',d)[0]

    def readUIntFile(self,f):
        b = f.read(4)
        return self.readUIntBuf(b)
    
    def readUIntsFile(self,f,count):
        b = f.read(4*count)
        return self.readUIntsBuf(b,count)

    def readUIntsBuf(self,b,count):
        format = string.join(['<',`int(count)`,'I'],'')
        return struct.unpack(format,b)
        
    def readInt64Buf(self,d):
        return struct.unpack('<q',d)[0]

    def readInt64File(self,f):
        return struct.unpack('<q',f.read(8))[0]

    def readUInt64Buf(self,d):
        return struct.unpack('<Q',d)[0]
    
    def readUInt64File(self,f):
        return struct.unpack('<Q',f.read(8))[0]

    def readFloatFile(self,f):
        return struct.unpack('<f',f.read(4))[0]

    def readFloatsFile(self,f,count):
        b = f.read(4*count)
        return self.readFloatsBuf(b,count)
    
    def readFloatsBuf(self,b,count):
        format = '<' + `int(count)` + 'f'
        return struct.unpack(format,b)

    def readDoubleBuf(self,b):
        return struct.unpack('<d',b)
    
    def readDoubleFile(self,f):
        return struct.unpack('<d',f.read(8))[0]
    
    def readFloatBuf(self,b):
        return struct.unpack('<f',b)[0]

    def readWordBuf(self,b):
        return struct.unpack('<h',b)[0]

    def readWordFile(self,f):
        return struct.unpack('<h',f.read(2))[0]

    def readUWordBuf(self,b):
        return struct.unpack('<H',b)[0]

    def readUWordFile(self,f):
        return struct.unpack('<H',f.read(2))[0]

    def readUWordsFile(self,f,count):
        format = '<' + `int(count)` + 'H'
        result = struct.unpack(format,f.read(2*count))
        return result

    def readByteBuf(self,b):
        return struct.unpack('b',b)[0]
    
    def readByteFile(self,f):
        return struct.unpack('b',f.read(1))[0]

    def readUByteBuf(self,b):
        return struct.unpack('B',b)[0]
    
    def readUByteFile(self,f):
        return struct.unpack('B',f.read(1))[0]

    def readCharBuf(self,b):
        return struct.unpack('c',b)[0]

    def readCharFile(self,f):
        return struct.unpack('c',f.read(1))[0]

    def readLocalizedString(self,f):
        langID = self.readIntFile(f)
        size = self.readIntFile(f)
        s = f.read(size).decode('latin1')
        return (langID,s)

    def readResRef(self,f):
        return f.read(16).lower()

    def readSizedResRef(self,f):
        size = self.readUByteFile(f)
        return f.read(size).lower()

    def readCExoString(self,f):
        size = self.readUIntFile(f)
        return f.read(size).decode('latin1')

    def readCExoLocStrings(self,f):
        totSize = self.readUIntFile(f)
        resref = self.readIntFile(f)
        count = self.readUIntFile(f)
        strings = []
        for i in range(count):
            strings.append(self.readLocalizedString(f))
        return (resref,strings)


    def writeIntBuf(self,n):
        return struct.pack('<i',n)

    def writeIntFile(self,n,f):
        f.write(self.writeIntBuf(n))

    def writeUIntBuf(self,n):
        return struct.pack('<I',n)

    def writeUIntFile(self,n,f):
        f.write(self.writeUIntBuf(n))

    def writeInt64Buf(self,n):
        return struct.pack('<q',n)

    def writeInt64File(self,n,f):
        f.write(self.writeInt64Buf(n))

    def writeUInt64Buf(self,n):
        return struct.pack('<Q',n)

    def writeUInt64File(self,n,f):
        f.write(self.writeUInt64Buf(n))

    def writeWordBuf(self,n):
        return struct.pack('<h',n)

    def writeWordFile(self,n,f):
        f.write(self.writeWordBuf(n))

    def writeUWordBuf(self,n):
        return struct.pack('<H',n)

    def writeUWordFile(self,n,f):
        f.write(self.writeUWordBuf(n))

    def writeByteBuf(self,n):
        return struct.pack('<b',n)

    def writeByteFile(self,n,f):
        f.write(self.writeByteBuf(n))

    def writeUByteBuf(self,n):
        return struct.pack('<B',n)

    def writeUByteFile(self,n,f):
        f.write(self.writeUByteBuf(n))

    def writeFloatBuf(self,n):
        return struct.pack('<f',n)

    def writeFloatFile(self,n,f):
        f.write(self.writeFloatBuf(n))

    def writeDoubleBuf(self,n):
        return struct.pack('<d',n)

    def writeDoubleFile(self,n,f):
        f.write(self.writeDoubleBuf(n))

    def writeCharBuf(self,n):
        return struct.pack('<c',n)

    def writeCharFile(self,n,f):
        f.write(self.writeCharBuf(n))

    def writeLocalizedStringBuf(self,langID,str):
        b = self.writeIntBuf(langID)
        strVal = str.encode('latin1')
        b += self.writeIntBuf(len(strVal))
        b += strVal
        return b

    def writeLocalizedStringFile(self,langID,str,f):
        f.write(self.writeLocalizedStringBuf(langID,str))

    def writeResRef(self,rr,f):
        rr = rr.encode('ascii')
        rr += '\0'*(16-len(rr))
        f.write(struct.pack('<16s',rr))

    def writeSizedResRefBuf(self,rr):
        b = self.writeUByteBuf(len(rr))
        b += rr.encode('ascii')
        return b

    def writeSizedResRefFile(self,rr,f):
        f.write(self.writeSizedResRefBuf(rr))

    def writeCExoStringBuf(self,str):
        strVal = str.encode('latin1')
        b = self.writeUIntBuf(len(strVal))
        b += strVal
        return b

    def writeCExoStringFile(self,str,f):
        f.write(self.writeCExoStringBuf(str))

    def writeSizedStringFile(self,str,size,f):
        str += (size-len(str))*'\0'
        f.write(str[:16])

    def writeCExoLocStringsBuf(self,resref,strings):
        totSize = 8
        for s in strings:
            totSize += 8 + len(s[1])
        b = self.writeUIntBuf(totSize)
        b += self.writeUIntBuf(resref)
        b += self.writeUIntBuf(len(strings))
        for s in strings:
            b += self.writeLocalizedStringBuf(s[0],s[1])
        return b
    
    def writeCExoLocStringsFile(self,strings,resref,f):
        f.write(self.writeCExoLocStringsBuf(resref,strings))
