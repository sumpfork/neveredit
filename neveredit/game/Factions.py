from neveredit.game.NeverData import NeverData
from neveredit.util import neverglobals
from neveredit.file.GFFFile import GFFStruct

import logging
logger = logging.getLogger("neveredit")

class Factions(NeverData):
    factionPropList = {
        }

    def __init__(self,erfFile):
        NeverData.__init__(self)
        repute_fac = erfFile.getEntryByNameAndExtension('repute','FAC')
        if not repute_fac:
            raise RuntimeError("couldn't find 'repute.fac'")
        self.addPropList('factions',self.factionPropList,erfFile.\
            getEntryContents(repute_fac).getRoot())
        self.factionList = None
        self.RepList = None

    def readContents(self):
        if self.factionList == None:
            facList = self.gffstructDict['factions'].getInterpretedEntry('FactionList')
            self.factionList = [FactionStruct(fac) for fac in facList]
            repList = self.gffstructDict['factions'].getInterpretedEntry('RepList')
            self.RepList = [ReputStruct(r) for r in repList]

    def discardContents(self):
        self.factionList = None
        self.RepList = None

    def getReputationValue(self,fac1,fac2):
        for rep in self.RepList:
            if rep.gffstructDict['repStruct'].getInterpretedEntry('FactionID1') == fac1 and\
                rep.gffstructDict['repStruct'].getInterpretedEntry('FactionID2') == fac2:
                    return rep.gffstructDict['repStruct'].getInterpretedEntry('FactionRep')
                    
    def addFaction(self,name):
        f = GFFStruct()
        f.add('FactionGlobal',True,'BYTE')
        f.add('FactionName',name,'CExoString')
        f.add('FactionParentID',1,'INT')
        self.factionList.append(FactionStruct(f))
        index = len(self.factionList)-1
        # now I must also create the reputation structs...
        for x in range(1,index): # 0=PC,
                                 # index = the new faction itself
            r = GFFStruct()
            r.add('FactionID1',index,'INT')
            r.add('FactionID2',x,'INT')
            r.add('FactionRep',50,'INT')
            self.RepList.append(ReputStruct(r))

        for y in range(0,index): 
            r = GFFStruct()
            r.add('FactionID1',y,'INT')
            r.add('FactionID2',index,'INT')
            r.add('FactionRep',50,'INT')
            self.RepList.append(ReputStruct(r))

       # and towards self
        r = GFFStruct()
        r.add('FactionID1',index,'INT')
        r.add('FactionID2',index,'INT')
        r.add('FactionRep',100,'INT')
        self.RepList.append(ReputStruct(r))

    def removeFaction(self,index):
        for r in self.RepList:
            if r.gffstructDict['repStruct'].getInterpretedEntry('FactionID1') == index or\
                r.gffstructDict['repStruct'].getInterpretedEntry('FactionID2') == index:
                self.RepList.remove(r)
        del self.factionList[index]

    def hasChanged(self):
        self.discardContents()
        self.readContents()

class FactionStruct(NeverData):
    facStructPropList = {
        'FactionGlobal': 'Boolean',
        'FactionName': 'CExoString,FactionName',
        'FactionParentID': 'Integer'
        }

    def __init__(self,gffEntry):
        NeverData.__init__(self)
        self.addPropList('factStruct',self.facStructPropList,gffEntry)

    def getName(self):
        return self.gffstructDict['factStruct'].getInterpretedEntry('FactionName')

    def getParent(self):
        return self.gffstructDict['factStruct'].getInterpretedEntry('FactionParentID')

class ReputStruct(NeverData):
    repStructPropList = {
        'FactionID1': 'Integer',
        'FactionID2': 'Integer',
        'FactionRep': 'Integer,0-100'
        }

    def __init__(self,gffEntry):
        NeverData.__init__(self)
        self.addPropList('repStruct',self.repStructPropList,gffEntry)
