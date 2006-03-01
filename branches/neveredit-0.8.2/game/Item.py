'''Classes for handling item objects, instances and blueprints'''
import logging
logger = logging.getLogger("neveredit")

import math

from neveredit.game.NeverData import LocatedNeverData
from neveredit.game.NeverData import NeverInstance

class Item(LocatedNeverData):
    itemPropList = {
        'AddCost': 'Integer,0-100000',
        'Charges': 'Integer,0-255',
        'Cost': 'Integer,0-100000',
        'DescIdentified': 'CExoLocString,4',
        'Description': 'CExoLocString,4',
        'LocalizedName': 'CExoLocString',
        'Plot': 'Boolean',
        #'StackSize': 'Integer', should look up basetype to see if stackable
        'Stolen': 'Boolean',
        'Tag': 'CExoString'
        }

    def __init__(self,gffEntry):
        LocatedNeverData.__init__(self)
        self.addPropList('main',self.itemPropList,gffEntry)
        self.model = None
        
    def getName(self):
        return self.gffstructDict['main'].getInterpretedEntry('LocalizedName').getString()

    def getPortrait(self,size):
        return None #have no portraits, but could assemble icons - to be done
    
    def getModel(self,copy=False):
        raise NotImplementedError("no item models yet")

    def clone(self):
        gff = self.getGFFStruct('main').clone()
        return self.__class__(gff)
    
class ItemBP (Item):
    itemBPPropList = {
        'Comment': 'CExoString',
        'PaletteID': 'Integer,0-20',
        'TemplateResRef': 'ResRef,NSS',
        }
            
    def __init__(self,gffEntry):
        Item.__init__(self, gffEntry)
        self.addPropList('blueprint',self.itemBPPropList,gffEntry)

    def toInstance(self):
        gff = self.gffstructDict['blueprint'].clone()

        del gff['Comment']
        del gff['PaletteID']
        
        gff.add('XPosition',0.0,'FLOAT')
        gff.add('YPosition',0.0,'FLOAT')
        gff.add('ZPosition',0.0,'FLOAT')
        gff.add('XOrientation',0.0,'FLOAT')
        gff.add('YOrientation',0.0,'FLOAT')

        gff.setType(ItemInstance.GFF_STRUCT_ID)
        
        return ItemInstance(gff)
    
class ItemInstance(Item, NeverInstance):

    GFF_STRUCT_ID = 0
    
    itemInstProplist = {
        'XOrientation': 'Hidden',
        'YOrientation': 'Hidden',
        'XPosition': 'Hidden',
        'YPosition': 'Hidden',
        'ZPosition': 'Hidden'
    }
    
    def __init__(self,gffEntry):
        if gffEntry.getType() != ItemInstance.GFF_STRUCT_ID:
            logger.warning("created with gff struct type " 
                           + `gffEntry.getType()`
                           + " should be " + `ItemInstance.GFF_STRUCT_ID`)
        Item.__init__(self,gffEntry)
        self.addPropList('instance',self.itemInstProplist,gffEntry)
        
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

