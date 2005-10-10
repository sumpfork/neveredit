import sys
from neveredit.file.NeverFile import NeverFile

class SoundSetFile(NeverFile):
    def __init__(self):
        NeverFile.__init__(self)
        self.SSFFile = None
        self.dataCache = {}

    def headerFromFile(self,f):
        f.seek(0)
        NeverFile.headerFromFile(self,f)
        self.EntryCount = self.dataHandler.readUIntFile(f)
        self.TableOffset = self.dataHandler.readUIntFile(f)

    def fromFile(self,f):
        self.headerFromFile(f)
        self.SSFFile = f

    def getEntryData(self,index):
        # returns the data as a [ResRef, StringRef] couple at position index
        # note that index starts from 1

        if index in self.dataCache.keys():
            return self.dataCache[index]
        else:
            # search for data ofset by looking in the Entry Table
            self.SSFFile.seek(self.TableOffset + (index -1) * 4)
            dataOffset = self.dataHandler.readUIntFile(self.SSFFile)
            self.SSFFile.seek(dataOffset)
            resref = self.dataHandler.readResRef(self.SSFFile)
            stringref = self.dataHandler.readUIntFile(self.SSFFile)
            self.dataCache[index]=[resref,stringref]
            return [resref,stringref]
