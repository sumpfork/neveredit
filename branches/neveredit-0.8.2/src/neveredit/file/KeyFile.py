"""Class to read Bioware format KEY files and retrieve their resources."""
import pprint
import sys
import os.path

import neveredit.game.ResourceManager
from neveredit.file.NeverFile import NeverFile
from neveredit.file.BIFFile import BIFFile
from neveredit.util import neverglobals

__all__ = ['KeyFile']

bifFiles = {}

class KeyFile(NeverFile):
    __doc__ = globals()['__doc__']
    def __init__(self,dir):
        NeverFile.__init__(self)
        self.bifCount = 0
        self.keyCount = 0
        self.offsetToFileTable = 0
        self.offsetToKeyTable = 0
        self.buildYear = 0
        self.buildDay = 0

        self.files = []
        self.keys  = {}
        self.appDir = dir

    def headerFromFile(self,f):        
        f.seek(0)
        NeverFile.headerFromFile(self,f)
        self.bifCount = self.dataHandler.readUIntFile(f)
        self.keyCount = self.dataHandler.readUIntFile(f)
        self.offsetToFileTable = self.dataHandler.readUIntFile(f)
        self.offsetToKeyTable = self.dataHandler.readUIntFile(f)
        self.buildYear = self.dataHandler.readUIntFile(f)
        self.buildDay = self.dataHandler.readUIntFile(f)
        f.seek(32,1) #skip empty space

    def fileTableFromFile(self,f):
        f.seek(self.offsetToFileTable)
        self.files = []
        for i in range(self.bifCount):
            size = self.dataHandler.readUIntFile(f)
            nameOffset = self.dataHandler.readUIntFile(f)
            nameSize = self.dataHandler.readUWordFile(f)
            drives = self.dataHandler.readUWordFile(f)
            self.files.append([size,drives,nameSize,nameOffset])
        for file in self.files:
            f.seek(file.pop())
            #the names seem null-terminated,
            #BW claims they're not
            name = f.read(file.pop()).strip('\0') 
            file.append(name)                

    def keyTableFromFile(self,f):
        f.seek(self.offsetToKeyTable)
        b = f.read(self.keyCount * 22)
        self.keys = {}
        for i in xrange(self.keyCount):
            index = i*22
            resref,type,resID = self.dataHandler.readFromBuf('<16sHI',
                                                             b[index:index+22])
            resref = resref.lower()
            fileIndex = resID >> 20
            resourceIndex = resID & 0xFFFFF #assume variable
            #I'm not sure about the decoding of fixed resources
            #maybe they mean y <<12 in the BW docs?
            #anyway, they're supposed to not be used
            self.keys[(resref,type)] = (self.files[fileIndex],resourceIndex)

    def fromFile(self,fname):
        f = NeverFile.fromFile(self,fname)
        self.fileTableFromFile(f)
        self.keyTableFromFile(f)
        
    def getKeyList(self):
        return self.keys.keys()

    def getBifFile(self,spec):
        f = None
        fname = spec[0][2].replace('\\','/')
        if not fname in bifFiles:
            f = BIFFile()
            f.fromFile(os.path.join(self.appDir,fname))
            bifFiles[fname] = f
        else:
            f = bifFiles[fname]
        return f
    
    def getResource(self,key):
        bifFileSpec = self.keys[key]
        f = self.getBifFile(bifFileSpec)
        c = neverglobals.getResourceManager()\
            .interpretResourceContents(key,
                                       f.getResourceData(bifFileSpec[1]))
        return c

    def getRawResource(self,key):
        bifFileSpec = self.keys[key]
        f = self.getBifFile(bifFileSpec)
        return f.getResourceData(bifFileSpec[1])
        
    def __str__(self):
        s = ''
        for k in self.keys:
            s += k[0].strip('\0') + '.' +\
                 neveredit.game.ResourceManager\
                 .ResourceManager.extensionFromResType(k[1])\
                 + ':' + self.keys[k][0][2] + ',' + `self.keys[k][1]` + '\n'
        return s

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    if(len(sys.argv) == 3):
        f = KeyFile(sys.argv[2])
        print 'reading key file',sys.argv[1]
        f.fromFile(sys.argv[1])
        print 'read',len(f.getKeyList()),'keys'
        print f
    else:
        print 'usage:',sys.argv[0],'<file> <appdir>'
        
        
