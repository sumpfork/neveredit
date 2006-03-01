from neveredit.game.NeverData import LocatedNeverData,NeverInstance
from neveredit.util import neverglobals

class SituatedObject(LocatedNeverData):
    sitObjPropList = {
        'AnimationState': 'Integer,0-16',
#        'Appearance': 'DWORD',
        'AutoRemoveKey': 'Boolean',
        'CloseLockDC': 'Integer,0-30',
        'Conversation': 'ResRef,DLG',
        'CurrentHP': 'Integer,0-1000',
        'Description': 'CExoLocString,4',
        'DisarmDC': 'Integer,0-30',
        'Faction': 'Integer,0-30',
        'Fort': 'Integer,0-50',
        'Hardness': 'Integer,0-100',
        'HP': 'Integer,0-1000',
        'Interruptable': 'Boolean',
        'Lockable': 'Boolean',
        'Locked': 'Boolean',
        'LocName': 'CExoLocString',
        'OnClosed': 'ResRef,NSS',
        'OnDamaged': 'ResRef,NSS',
        'OnDeath': 'ResRef,NSS',
        'OnDisarm': 'ResRef,NSS',
        'OnHeartbeat': 'ResRef,NSS',
        'OnLock': 'ResRef,NSS',
        'OnMeleeAttacked': 'ResRef,NSS',
        'OnOpen': 'ResRef,NSS',
        'OnSpellCastAt': 'ResRef,NSS',
        'OnTrapTriggered': 'ResRef,NSS',
        'OnUnlock': 'ResRef,NSS',
        'OnUserDefined': 'ResRef,NSS',
        'OpenLockDC': 'Integer,0-30',
        'Plot': 'Boolean',
        'PortraitId': 'Portrait',
        'Ref': 'Integer,0-30',
        'Tag': 'CExoString',
        'TrapDetectable': 'Boolean',
        'TrapDetectDC': 'Integer,0-30',
        'TrapDisarmable': 'Boolean',
        'TrapFlag': 'Boolean',
        'TrapOneShot': 'Boolean',
        'Will': 'Integer,0-30'
        }
            
    def __init__(self,gffEntry):
        LocatedNeverData.__init__(self)
        if not self.getGFFStruct('main'):
            self.addPropList('main',self.sitObjPropList,gffEntry)
        self.model = None
        
    def getName(self):
        return self['LocName'].getString ()

    def getObjectId(self):
        return self['ObjectId']

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

    def clone(self):
        gff = self.getGFFStruct('main').clone()
        return self.__class__(gff)
        
        
class SituatedObjectBP (SituatedObject):
    sitObjBPPropList = {
        'Comment': 'CExoString',
        'PaletteID': 'Integer,0-128',
        'TemplateResRef': 'ResRef,NSS',
        }

    def __init__ (self, gffEntry):
        SituatedObject.__init__ (self, gffEntry)
        self.addPropList ('blueprint', self.sitObjBPPropList, gffEntry)

    def makeInstanceGFF(self):
        gff = self.gffstructDict['blueprint'].clone()

        del gff['Comment']
        del gff['PaletteID']
        
        gff.add('Bearing',0.0,'FLOAT')
        gff.add('X',0.0,'FLOAT')
        gff.add('Y',0.0,'FLOAT')
        gff.add('Z',0.0,'FLOAT')

        return gff
    
class SituatedObjectInstance (SituatedObject,NeverInstance):
    sitObjInstPropList = {
        'Bearing': 'Hidden',
        'TemplateResRef': 'ResRef,NSS',
        'X': 'Hidden',
        'Y': 'Hidden',
        'Z': 'Hidden'
        }

    def __init__ (self, gffEntry):
        SituatedObject.__init__ (self, gffEntry)
        self.addPropList ('instance', self.sitObjInstPropList, gffEntry)

    def getX(self):
        return self['X']

    def getY(self):
        return self['Y']

    def getZ(self):
        return self['Z']

    def setX(self,x):
        self['X'] = x

    def setY(self,y):
        self['Y'] = y

    def setZ(self,z):
        self['Z'] = z

    def getBearing(self):
        return self['Bearing']

    def setBearing(self,b):
        self['Bearing'] = b
        
