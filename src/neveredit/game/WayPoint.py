from neveredit.game.NeverData import LocatedNeverData,NeverInstance
from neveredit.util import neverglobals

import logging
logger = logging.getLogger("neveredit")

import math

class WayPoint(LocatedNeverData):
    waypointPropList = {
        'Appearance': 'Integer',
        'Description': 'CExoLocString,2',
        'HasMapNote': 'Boolean',
        'LinkedTo': 'Hidden',
        'LocalizedName': 'CExoLocString,2',
        'MapNote': 'CExoLocString,2',
        'MapNoteEnabled': 'Boolean',
        'Tag': 'CExoString'
        }

    def __init__(self,gffEntry):
        LocatedNeverData.__init__(self)
        self.addPropList('main',self.waypointPropList,gffEntry)

    def getPortrait(self,size):
        # waypoints have no portrait
        return None

    def getModel(self,copy=False):
        # index to 'waypoint.2da', RESREF column
        if not copy and self.model:
            return self.model
        twoda = neverglobals.getResourceManager()\
                .getResourceByName('waypoint.2da')
        index = self['Appearance']
        #print(index)
        if not index:
            index = 1   # only influes on apearence in the toolset, not in game
        self.modelName = twoda.getEntry(index,'RESREF').lower() + '.mdl'
        #print('MODELNAME : '+self.modelName)
        model = neverglobals.getResourceManager()\
                .getResourceByName(self.modelName,copy)
        if not copy:
            self.model = model
        return model

    def getName(self):
        return self.gffstructDict['main'].getInterpretedEntry('LocalizedName').getString()

    def clone(self):
        gff = self.getGFFStruct('main').clone()
        return self.__class__(gff)

class WayPointBP(WayPoint):
    waypointBPPropList = {
        'Comment': 'CExoString',
        'PaletteID': 'Integer',
        'TemplateResRef': 'ResRef,UTW',
        }

    def __init__ (self, gffEntry):
        WayPoint.__init__(self,gffEntry)
        self.addPropList('blueprint',self.waypointBPPropList,gffEntry)

    def toInstance(self):
        gff = self.gffstructDict['blueprint'].clone()

        del gff['Comment']
        del gff['PaletteID']
        
        gff.add('XPosition',0.0,'FLOAT')
        gff.add('YPosition',0.0,'FLOAT')
        gff.add('ZPosition',0.0,'FLOAT')
        gff.add('XOrientation',0.0,'FLOAT')
        gff.add('YOrientation',0.0,'FLOAT')

        gff.setType(WayPointInstance.GFF_STRUCT_ID)
        
        return WayPointInstance(gff)

class WayPointInstance(WayPoint, NeverInstance):

    GFF_STRUCT_ID = 5
    
    # it seems we hide this data so that we don't create the controls for them.
    # right?
    waypointInstProplist = {
        'XOrientation': 'Hidden',
        'YOrientation': 'Hidden',
        'XPosition': 'Hidden',
        'YPosition': 'Hidden',
        'ZPosition': 'Hidden'
    }

    def __init__(self,gffEntry):
        if gffEntry.getType() != WayPointInstance.GFF_STRUCT_ID:
            logger.warning("created with gff struct type "
                           + `gffEntry.getType()`
                           + " should be " + `WayPointInstance.GFF_STRUCT_ID`)
        WayPoint.__init__(self,gffEntry)
        self.addPropList('instance',self.waypointInstProplist,gffEntry)


    def getX(self):
        return self['XPosition']

    def getY(self):
        return self['YPosition']

    def getZ(self):
        return self['ZPosition']

    def setX(self,x):
        self['XPosition'] = x

    def setY(self,y):
        self['YPosition'] = y

    def setZ(self,z):
        self['ZPosition'] = z

    def getXOrientation(self):
        return self['XOrientation']

    def getYOrientation(self):
        return self['YOrientation']

    def getBearing(self):        
        return math.atan2(self.getYOrientation(),self.getXOrientation())*180.0/math.pi

    def setBearing(self,b):        
        self['XOrientation'] = math.cos(b)*math.pi/180.0
        self['YOrientation'] = math.sin(b)*math.pi/180.0

    def getObjectId(self):
        return self['ObjectId']
