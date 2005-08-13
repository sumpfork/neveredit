import logging
logger = logging.getLogger("neveredit")

import string

from neveredit.game.NeverData import NeverData
from neveredit.util import neverglobals

compilerAvailable = False
try:
    from nwntools import nsscompiler
    compilerAvailable = True
except ImportError:
    logger.exception('could not import nsscompiler - install from nwntools package\n'
                     '      ignore this exception if you do not want to compile scripts')

class CompiledScript:
    def __init__(self,data):
        self.data = data

    def toFile(self,f,o):
        f.seek(o)
        f.write(self.data)
        
class Script(NeverData):
    lang_keywords = """bool break case char const continue
    default do double else enum extern false float for
    goto if int long not not_eq or or_eq return short signed sizeof static struct
    switch true union unsigned void while string object location effect event
    talent itemproperty action OBJECT_SELF TRUE FALSE
    """

    nwscript_keywords = {}

    def init_nwscript_keywords(cls):
        nwscript = str(neverglobals.getResourceManager()\
                       .getResourceByName('nwscript.nss'))
        comment = []
        for line in nwscript.split('\r\n'):
            if not line.strip():
                comment = []
            elif line.strip()[:2] == '//':
                comment.append(line.strip()[2:])
            else:
                parens = line.find('(')                
                if  parens != -1:
                    comment.append(line)
                    keyword = line[:parens].split()[-1].strip()
                    cls.nwscript_keywords[keyword] = string.join(comment,'\n')
                    comment = []
                else:
                    eq = line.find('=')
                    if eq != -1:
                        keyword = line[:eq].split()[-1].strip()
                        cls.nwscript_keywords[keyword] = line
                        comment = []
    init_nwscript_keywords = classmethod(init_nwscript_keywords)
    
    def __init__(self,n,data):
        NeverData.__init__(self)
        self.name = n
        self.scriptData = data.decode('latin1')
        self.nwndir = None
        self.module = None
        self.compiled = None

    def getName(self):
        '''return the name (resref) of this script'''
        return self.name

    def getData(self):
        '''return the data (script text) of this script'''
        return self.scriptData

    def getUnixData(self):
        '''return the data of this script, making sure there
        are no window/mac line endings'''
        return self.scriptData.replace('\r','')

    def setUnixData(self,d):
        self.scriptData = d.replace('\n','\r\n')

    def getCompiledScript(self):
        return self.compiled
    
    def getProperty(self,label):
        if label != self.name:
            logger.error('script contains "' + self.name + '" not "' + label + '"')
        else:
            return [self.name,self,'Script']

    def setProperty(self,label,value):
        if label != self.name:
            logger.error('script contains "' + self.name + '" not "' + label + '"')
        else:
            self.scriptData = value
            self.compile()
            
    def iterateProperties(self):
        yield [self.name,self.scriptData,'Script']

    def toFile(self,f,o):
        f.seek(o)
        f.write(self.scriptData.encode('latin1'))

    def setNWNDir(self,nwndir):
        self.nwndir = nwndir

    def setModule(self,mod):
        self.module = mod
        
    def compile(self):
        if not compilerAvailable:
            raise RuntimeError("nwnnsscompiler not available")
        if not self.nwndir:
            print 'cannot compile script without location of NWN dir'
        nsscompiler.init(self.nwndir)
        if self.module:
            nsscompiler.set_module(self.module)
        self.compiled,err = nsscompiler.compile(self.scriptData,self.name,True)
        if self.compiled:
            self.compiled = CompiledScript(self.compiled)
        nsscompiler.free()
        return (self.compiled,err)

    def __str__(self):
        return self.scriptData

    def __repr__(self):
        return self.__str__()

if __name__ == '__main__':
    import sys
    Script.init_nwscript_keywords()
    print string.join(Script.nwscript_keywords.keys())
    s = Script('test',open(sys.argv[1]).read())
    print s
    print
    print 'trying to compile',sys.argv[1]
    s.setNWNDir('/Applications/Neverwinter Nights')    
    print `s.compile()`
    
