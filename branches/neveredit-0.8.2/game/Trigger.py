
from neveredit.game.NeverData import *
from neveredit.util import neverglobals
from neveredit.file.GFFFile import GFFStruct

import logging
logger = logging.getLogger("neveredit")

import math

class Trigger(LocatedNeverData):
    triggerPropList = {
        'AutoRemoveKey': 'Hidden',     # Boolean but unused, so maybe 'Hidden'?
        'Cursor': '2daIndex,cursors.2da,,strref,Label',
        #'HighlightHeight': 'Float',
        'DisarmDC': 'Integer,1-250',
        'Faction': 'Integer',
        'KeyName': 'Hidden',            # CExoString, but unused
        'LinkedTo': 'CExoString',
        'LinkedToFlags': 'Integer,0-2', # not sure this shouldn't be AreaTrans only
        'LocalizedName': 'CExoLocString',
        'LoadScreenID': '2daIndex,loadscreens.2da,StrRef,strref,Label',
        'OnClick': 'ResRef',
        'OnDisarm': 'ResRef,NSS',
        'OnTrapTriggered': 'ResRef,NSS',
        'PortraitId': 'Portrait',
        'ScriptHeartbeat': 'ResRef,NSS',
        'ScriptOnEnter': 'ResRef,NSS',
        'ScriptOnExit': 'ResRef,NSS',
        'ScriptUserDefine': 'ResRef,NSS',
        'Tag': 'CExoString',
        'TrapDetectable': 'Boolean',
        'TrapDetectDC': 'Integer,0-250',
        'TrapDisarmable': 'Boolean',
        'TrapFlag': 'Boolean',          # strange, as it indicates IF this is a trap or not
        'TrapOneShot': 'Boolean',
        'TrapType': '2daIndex,traps.2da,,strref,Label',
        'Type': 'Integer,0-2,Traptype'
        }

    def __init__(self,gffEntry):
        LocatedNeverData.__init__(self)
        self.addPropList('main',self.triggerPropList,gffEntry)

    def getPortrait(self,size):
        if self['Portrait']:
            name = self['Portrait'].lower() + size + '.tga'
            return neverglobals.getResourceManager().getResourceByName(name)
        twoda = neverglobals.getResourceManager()\
                .getResourceByName('portraits.2da')
        baseResRef = twoda.getEntry(self['PortraitId'],'BaseResRef')
        if not baseResRef or baseResRef == '****':
            return None
        return neverglobals.getResourceManager()\
               .getResourceByName('po_' + baseResRef.lower()
                                  + size + '.tga')

    def getName(self):
        return self.gffstructDict['main'].getInterpretedEntry('LocalizedName').getString()

    def clone(self):
        gff = self.getGFFStruct('main').clone()
        return self.__class__(gff)

    def getModel(self):
        return None

class TriggerBP(Trigger):
    triggerBPPropList = {
        'Comment': 'CExoString',
        'PaletteID': 'Integer,0-255',
        'TemplateResRef': 'ResRef,UTT'
        }

    def __init__ (self, gffEntry):
        Trigger.__init__(self,gffEntry)
        self.addPropList('blueprint',self.triggerBPPropList,gffEntry)

    def toInstance(self):
        gff = self.gffstructDict['blueprint'].clone()

        del gff['Comment']
        del gff['PaletteID']
        
        gff.add('XPosition',0.0,'FLOAT')
        gff.add('YPosition',0.0,'FLOAT')
        gff.add('ZPosition',0.0,'FLOAT')
        gff.add('XOrientation',0.0,'FLOAT')
        gff.add('YOrientation',0.0,'FLOAT')

        gff.setType(TriggerInstance.GFF_STRUCT_ID)
        
        return TriggerInstance(gff)

class TriggerInstance(Trigger,NeverInstance):
    GFF_STRUCT_ID = 1
    triggerInstancePropList = {
        'Geometry': 'Hidden',
        'TemplateResRef': 'ResRef,UTT',
        'XOrientation': 'Hidden',
        'YOrientation': 'Hidden',
        'XPosition': 'Hidden',
        'YPosition': 'Hidden',
        'ZPosition': 'Hidden',
        }

    def __init__(self,gffEntry):
        if gffEntry.getType() != TriggerInstance.GFF_STRUCT_ID:
            logger.warning("created with gff struct type "
                           + `gffEntry.getType()`
                           + " should be " + `TriggerInstance.GFF_STRUCT_ID`)
        Trigger.__init__(self,gffEntry)
        self.addPropList('instance',self.triggerInstancePropList,gffEntry)


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

    def getPoint(self,n):
        try:
            pointStruct = self['Geometry'][n]
        except ValueError:
            return None
        return triggerPoint(pointStruct)

    def addPoint(self,X,Y,Z):
        s = GFFStruct()
        s.add('PointX',X,"FLOAT")
        s.add('PointY',Y,"FLOAT")
        s.add('PointZ',Z,"FLOAT")
        self['Geometry'].append(s)

    def removePoint(self, index):
        del self['Geometry'][index]

class triggerPoint(NeverData):
    pointPropList = {
        'PointX': 'Hidden', #float
        'PointY': 'Hidden',
        'PointZ': 'Hidden'
        }

    def __init__(self,gffEntry):
        NeverData.__init__(self)
        self.addPropList('point',self.pointPropList,gffEntry)

    def getX(self):
        return self['PointX']

    def getY(self):
        return self['PointY']

    def getZ(self):
        return self['PointZ']

    def getCoordinates(self):
        return self.getX(),self.getY(),self.getZ()

    def setCoordinates(self,X,Y,Z):
        self['pointX'] = X
        self['pointY'] = Y
        self['pointZ'] = Z
