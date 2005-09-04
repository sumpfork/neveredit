import string

from neveredit.util import Loggers
import logging
logger = logging.getLogger("neveredit.file")

from neveredit.util import neverglobals

class CExoLocString:

    def __init__(self,gffentry=None,value=None,langID=0,gender=0):
        if gffentry:
            self.strref = gffentry[0]
            self.locStrings = dict(gffentry[1])
        else:
            self.strref = -1
            self.locStrings = {}
        if value != None:
            self.setString(value,langID,gender)

    def getStringAndIndex(self,langID,gender):
        index = langID * 2 + gender
        if index in self.locStrings:
            return (self.locStrings[index],index)
        elif self.strref != -1:
            if not neverglobals.getResourceManager():
                logger.error('no resource manager in CExoLocString')
                return ('',-1)
            else:
                s = neverglobals.getResourceManager().getDialogString(self.strref)
                if s != None:
                    return (s,-1)
                else:
                    logger.error('error, Invalid Strref in CExoLocString')
                    return ('',-1)
        else:
            #print string.join (['error, no string for language',
            #                    `index`,
            #                     'in CExoLocString for embedded strings',
            #                     `self.locStrings`
            #                     ])
            return ('',-1)

    def getString(self,langID=0,gender=0):
        (text,res) = self.getStringAndIndex(langID,gender)
        return text

    def setString(self,str,langID=0,gender=0):
        index = langID * 2 + gender
        s = None
        if self.strref != -1:
            if not neverglobals.getResourceManager():
                logger.error('no resource manager in CExoLocString')
                return
            else:
                s = neverglobals.getResourceManager().getDialogString(self.strref)
        if s != str:
            self.locStrings[index] = str
        
    def toGFFEntry(self):
        return (self.strref,
                zip(self.locStrings.keys(),
                    self.locStrings.values()))

    def __str__(self):
        return self.getString()

    def __repr__(self):
        return self.__str__()
