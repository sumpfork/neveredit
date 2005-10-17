import string

from neveredit.util import neverglobals
from neveredit.game.NeverData import NeverData
from neveredit.game.Door import DoorBP
from neveredit.game.Placeable import PlaceableBP
from neveredit.game.Creature import CreatureBP
from neveredit.game.Item import ItemBP
from neveredit.game.WayPoint import WayPointBP

class TreeNode:
    def __init__(self,nodeStruct,bptype):
        self.bptype = bptype
        self.blueprint = None
        
        if nodeStruct.hasEntry('STRREF') and nodeStruct['STRREF'] != 0xffffffff:
            self.name = neverglobals.getResourceManager()\
                        .getDialogString(nodeStruct['STRREF'])
        elif nodeStruct.hasEntry('NAME'):
            self.name = nodeStruct['NAME']
        elif nodeStruct.hasEntry('DELETE_ME'):
            self.name = nodeStruct['DELETE_ME']
            
        if nodeStruct.hasEntry('TYPE'):            
            self.type = nodeStruct['TYPE']
        else:
            self.type = 0
            
        if nodeStruct.hasEntry('ID'):
            self.nodeID = nodeStruct['ID']
        else:
            self.nodeID = -1

        if nodeStruct.hasEntry('RESREF'):
            self.resref = nodeStruct['RESREF']
        else:
            self.resref = None

        if nodeStruct.hasEntry('CR'):
            self.challengeRating = nodeStruct['CR']
            self.faction = nodeStruct['FACTION']
        else:
            self.challengeRating = -1.0
            self.faction = ''

        if nodeStruct.hasEntry('LIST'):
            self.children = [TreeNode(s,self.bptype) for s in nodeStruct['LIST']]
        else:
            self.children = []
            
    def getName(self):
        return self.name

    def getChildren(self):
        return self.children

    def getImage(self):
        bp = self.getBlueprint()
        if bp:
            return bp.getPortrait('t')
        else:
            return None
    
    def getBPType(self):
        return self.bptype
   
    def getBlueprint(self):
        if not self.resref:
            return None
        if self.blueprint:
            return self.blueprint
        if self.bptype != 'Store':
            resname = string.join([self.resref.strip('\0'),'.UT',self.bptype[0]],'')
        else:
            resname = string.join([self.resref.strip('\0'),'.UTM'],'')
        gffroot = neverglobals.getResourceManager()\
                  .getResourceByName(resname).getRoot()
        if self.bptype == 'Creature':
            self.blueprint = CreatureBP(gffroot)
        elif self.bptype == 'Door':
            self.blueprint = DoorBP(gffroot)
        elif self.bptype == 'Item':
            self.blueprint = ItemBP(gffroot)
        elif self.bptype == 'Trigger':
            raise NotImplementedError("no trigger blueprints yet")
            #self.blueprint = TriggerBP(gffroot)
        elif self.bptype == 'Sound':
            raise NotImplementedError("no sound blueprints yet")
            #self.blueprint = SoundBP(gffroot)
        elif self.bptype == 'Encounter':
            raise NotImplementedError("no encounter blueprints yet")
            #self.blueprint = EncounterBP(gffroot)
        elif self.bptype == 'Placeable':
            self.blueprint = PlaceableBP(gffroot)
        elif self.bptype == 'Store':
            raise NotImplementedError("no store blueprints yet")
            #self.blueprint = StoreBP(gffroot)
        elif self.bptype == 'Waypoint':
            #raise NotImplementedError("no waypoint blueprints yet")
            self.blueprint = WayPointBP(gffroot)
        return self.blueprint

    def getTypeAsString(self):
        extension = neverglobals.getResourceManager()\
                    .extensionFromResType(self.type)
        return extension
    
    def printTree(self,indent):
        print indent + `self`
        for c in self.children:
            c.printTree(indent + '  ')
            
    def __str__(self):
        return string.join([self.name,`self.resref`,self.bptype])

    def __repr__(self):
        return self.__str__()

class Palette(NeverData):
    palettePropList = {}
    PALETTE_TYPES = ['Creature','Door','Encounter','Item','Placeable',
                     'Sound','Store','Trigger','Waypoint']
    def __init__(self,gffEntry,bptype):
        NeverData.__init__(self)
        self.addPropList('main',self.palettePropList,gffEntry)
        self.type = self['RESTYPE']
        self.roots = [TreeNode(nodeStruct,bptype) for nodeStruct in self['MAIN']]
        #for r in self.roots:
        #    r.printTree('')

    def getRoots(self):
        return self.roots

    def getStandardPalette(typ):
        r = neverglobals.getResourceManager()
        return Palette(r.getResourceByName(typ.lower() + 'palstd.itp').getRoot(),typ)
    getStandardPalette = staticmethod(getStandardPalette)
