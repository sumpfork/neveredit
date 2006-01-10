'''Classes for handling door objects, instances and blueprints'''

import logging
logger = logging.getLogger("neveredit")

import copy

from neveredit.game.SituatedObject import SituatedObject
from neveredit.game.SituatedObject import SituatedObjectInstance
from neveredit.game.SituatedObject import SituatedObjectBP
from neveredit.util import neverglobals

class Door(SituatedObject):
    doorPropList = {
        'AnimationState':'Integer,0-2',
        'LinkedTo':'CExoString',
        'LinkedToFlags':'Integer,0-2',
        'OnClick':'ResRef,NSS',
        'OnFailToOpen':'ResRef,NSS',
        'Appearance':'2daIndex,doortypes.2da,StringRefGame,strref,Label',
        'GenericType':'2daIndex,genericdoors.2da,Name,strref,Label',
        'LoadScreenID':'2daIndex,loadscreens.2da,StrRef,strref,Label'
        }

    def __init__ (self, gffEntry):        
        SituatedObject.__init__ (self, gffEntry)
        self.addPropList ('door', self.doorPropList, gffEntry)
        
    def getModel(self,copy=False):
        if not copy and self.model:
            return self.model
        index = self['Appearance']
        if index > 0:
            twoda = neverglobals.getResourceManager()\
                    .getResourceByName('doortypes.2da')
            self.modelName = twoda.getEntry(index,'Model').lower() + '.mdl'
            model = neverglobals.getResourceManager()\
                    .getResourceByName(self.modelName,copy)
        else:
            index = self['GenericType']
            twoda = neverglobals.getResourceManager()\
                    .getResourceByName('genericdoors.2da')
            self.modelName = twoda.getEntry(index,'ModelName').lower() + '.mdl'
            model = neverglobals.getResourceManager()\
                    .getResourceByName(self.modelName,copy)
        if not copy:
            self.model = model
        return model

class DoorBP(Door,SituatedObjectBP):
    def __init__(self,gffEntry):
        SituatedObjectBP.__init__(self,gffEntry)
        Door.__init__(self,gffEntry)        

    def toInstance(self):
        gff = self.makeInstanceGFF()
        gff.setType(DoorInstance.GFF_STRUCT_ID)
        return DoorInstance(gff)
    
class DoorInstance(Door,SituatedObjectInstance):

    GFF_STRUCT_ID = 8
    
    def __init__ (self, gffEntry):
        if gffEntry.getType() != DoorInstance.GFF_STRUCT_ID:
            logger.warning("created with gff struct type "
                           + `gffEntry.getType()`
                           + " should be " + `DoorInstance.GFF_STRUCT_ID`)     
        SituatedObjectInstance.__init__ (self, gffEntry)
        Door.__init__ (self, gffEntry)
