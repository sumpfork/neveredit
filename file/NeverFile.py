from neveredit.file import BinaryDataHandler
import sys
from neveredit.util.Progressor import Progressor

class NeverFile(Progressor):
    def __init__(self):
        Progressor.__init__(self)
        self.dataHandler = BinaryDataHandler.BinaryDataHandler()
        self.type = ''
        self.version = ''
        self.progressDisplay = None
        
    def headerFromFile(self,f):
        """Read a file header"""
        self.type = f.read(4)
        self.version = f.read(4)

    def fromFile(self,fname):
        """initialize this class from the given filename"""
        f = open(fname,'rb')
        self.headerFromFile(f)
        return f

if __name__ == "__main__":
    if(len(sys.argv) == 2):
        f = NeverFile()
        print 'reading file',sys.argv[1]
        f.fromFile(sys.argv[1])
        print 'file type is' + `f.type` + ' version ' + `f.version`

