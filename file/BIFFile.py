"""Class to read Bioware BIF format files."""
from neveredit.file.NeverFile import NeverFile
import pprint
import sys

global appDir

class BIFFile(NeverFile):
    __doc__=globals()['__doc__']
    def __init__(self):
        NeverFile.__init__(self)
        self.variableResourceCount = 0
        self.fixedResourceCount = 0
        self.variableTableOffset = 0

        self.variableResources = []
        self.fixedResources = []
        
    def headerFromFile(self,f):
        f.seek(0)
        NeverFile.headerFromFile(self,f)
        self.variableResourceCount = self.dataHandler.readUIntFile(f)
        self.fixedResourceCount = self.dataHandler.readUIntFile(f)
        if self.fixedResourceCount != 0:
            print 'error, fixed resources in BIF files not implemented'
            return
        self.variableTableOffset = self.dataHandler.readUIntFile(f)

    def variableResourcesFromFile(self,f):
        self.variableResources = self.variableResourceCount * [None]
        f.seek(self.variableTableOffset)
        b = f.read(self.variableResourceCount * 16)
        nums = self.dataHandler.readUIntsBuf(b,self.variableResourceCount*4)
        for i in range(self.variableResourceCount):
            index = i*4
            resID,offset,size,type = nums[index:index+4]
            #resID = self.dataHandler.readUIntFile(f)
            fileIndex = resID>>20
            #resourceIndex = resID & 0xFFFFF
            #index = (f.tell() - self.variableTableOffset - 4)/16
            #if resourceIndex != len(self.variableResources):
            #    #this error seems to occur - is this ok?
            #    print 'BIFFile: we are',len(self.variableResources),'into the resources'
            #    pass
            #offset = self.dataHandler.readUIntFile(f)
            #size = self.dataHandler.readUIntFile(f)
            #type = self.dataHandler.readUIntFile(f)
            self.variableResources[i] = (offset,size,type,fileIndex)
            
    def fixedResourcesFromFile(self,f):
        pass #BW claims these aren't used
    
    def fromFile(self,fname):
        self.file = NeverFile.fromFile(self,fname)
        self.variableResourcesFromFile(self.file)
        self.fixedResourcesFromFile(self.file)

    def getResourceData(self,index):
        entry = self.variableResources[index]
        self.file.seek(entry[0])
        return self.file.read(entry[1])
    
    def __str__(self):
        return pprint.PrettyPrinter().pformat(self.variableResources)

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        f = BIFFile()
        print 'reading bif file',sys.argv[1]
        f.fromFile(sys.argv[1])
        print 'read file'
        print f

