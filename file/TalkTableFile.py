from neveredit.file.NeverFile import NeverFile
import sys

__all__ = ['TalkTableFile']

class TalkTableFile(NeverFile):    
    def __init__(self):
        NeverFile.__init__(self)
        self.languageID = 0
        self.stringCount = 0
        self.stringDataOffset = 0
        self.stringSpecOffset = 20
        self.stringSpecs = []
        self.tlkFile = None
        self.version = ''
        self.stringSpecSize = 40
        
    def headerFromFile(self,f):        
        f.seek(0)
        NeverFile.headerFromFile(self,f)
        if self.version != 'V3.0':
            self.stringSpecSize = 36
        else:
            self.stringSpecSize = 40 #sound length got added
        self.languageID = self.dataHandler.readUIntFile(f)
        self.stringCount = self.dataHandler.readUIntFile(f)
        self.stringDataOffset = self.dataHandler.readUIntFile(f)
        self.stringSpecs = self.stringCount * [None]
        
    def retrieveStringSpec(self,index):
        f = self.tlkFile
        if self.stringSpecs[index]:
            return self.stringSpecs[index]
        f.seek(self.stringSpecOffset + index * self.stringSpecSize)
        class StringSpec:
            def __init__(self):
                pass
        sp = StringSpec()
        flags = self.dataHandler.readUIntFile(f)
        sp.textPresent = flags & 0x0001
        sp.soundPresent = flags & 0x0002
        sp.soundLengthPresent = flags & 0x0004
        sp.soundResRef = self.dataHandler.readResRef(f)
        sp.volumeVariance = self.dataHandler.readUIntFile(f)
        sp.pitchVariance = self.dataHandler.readUIntFile(f)
        sp.stringOffset = self.dataHandler.readUIntFile(f)
        sp.stringSize = self.dataHandler.readUIntFile(f)
        if self.version == 'V3.0':
            sp.soundLength = self.dataHandler.readFloatFile(f)
        else:
            sp.soundLength = 0.0
        f.seek(self.stringDataOffset + sp.stringOffset)
        sp.string = f.read(sp.stringSize).decode('latin1')
        self.stringSpecs[index] = sp
        return sp
    
    def fromFile(self,fname):
        f = NeverFile.fromFile(self,fname)
        self.tlkFile = f
        
    def getLanguageID(self):
        return self.languageID

    def getStringSpec(self,strref):
        if strref == 0xFFFFFFFF:
            return None
        special = (strref & 0xFF000000) >> 24
        alternate = special & 0x01
        if alternate:
            print 'not handling alternate dialog.tlk files yet'
            return None
        strref &= 0x00FFFFFF
        if strref >= len(self.stringSpecs):
            print 'invalid index into talk table:',strref
            return None
        else:
            return self.retrieveStringSpec(strref)

    def getString(self,strref):
        sp = self.getStringSpec(strref)
        if sp:
            return sp.string
        else:
            return None
        
    def __str__(self):
        s = ''
        s += 'file has' + `self.stringCount` + 'strings\n'
        s += 'here are a few:\n'
        for i in range(min(self.stringCount,50)):
            s += self.getString(i) + '\n'
        return s
    
    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        f = TalkTableFile()
        print 'reading tlk file',sys.argv[1]
        f.fromFile(sys.argv[1])
        print f.getString(int(sys.argv[2]))
        
        
