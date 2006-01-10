import logging
logger = logging.getLogger("neveredit")

from neveredit.game.SituatedObject import SituatedObject
from neveredit.game.SituatedObject import SituatedObjectInstance
from neveredit.game.SituatedObject import SituatedObjectBP
from neveredit.game.Item import ItemInstance
from neveredit.util import neverglobals

class Placeable(SituatedObject):
    propList = {
        'HasInventory':'Boolean',
        'OnInvDisturbed':'ResRef,NSS',
        'OnUsed':'ResRef,NSS',
        'Static':'Boolean',
        'Useable':'Boolean',
        'Appearance':'2daIndex,placeables.2da,StrRef,strref,Label',
        'BodyBag':'2daIndex,bodybag.2da,Name,strref,Label'
        }
        
    def __init__ (self, gffEntry):
        SituatedObject.__init__ (self, gffEntry)
        self.addPropList ('placeable', self.propList, gffEntry)
        

    def getInventory(self):
        if not self['HasInventory']:
            return []
        inventoryStructs = self.gffstructDict['placeable'].getInterpretedEntry('ItemList')
        if not inventoryStructs:
            return []
        return [ItemInstance(s) for s in inventoryStructs]

    def getModel(self,copy=False):
        if not copy and self.model:
            return self.model
        twoda = neverglobals.getResourceManager()\
                .getResourceByName('placeables.2da')
        index = self['Appearance']
        self.modelName = twoda.getEntry(index,'ModelName').lower() + '.mdl'
        model = neverglobals.getResourceManager()\
                .getResourceByName(self.modelName,copy)
        if not copy:
            self.model = model
        return model

class PlaceableBP(Placeable,SituatedObjectBP):
    def __init__(self,gffEntry):
        SituatedObjectBP.__init__(self,gffEntry)
        Placeable.__init__(self,gffEntry)        

    def toInstance(self):
        gff = self.makeInstanceGFF()
        gff.setType(PlaceableInstance.GFF_STRUCT_ID)
        return PlaceableInstance(gff)

class PlaceableInstance(Placeable,SituatedObjectInstance):

    GFF_STRUCT_ID = 9
    
    def __init__ (self, gffEntry):
        if gffEntry.getType() != PlaceableInstance.GFF_STRUCT_ID:
            logger.warning("created with gff struct type "
                           + `gffEntry.getType()`
                           + " should be " + `PlaceableInstance.GFF_STRUCT_ID`)
        SituatedObjectInstance.__init__ (self, gffEntry)
        Placeable.__init__ (self, gffEntry)

