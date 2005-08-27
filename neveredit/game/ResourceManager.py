"""Classes to find resources in modules, hak packs and the game directory
and delegate their interpretation. Also contains change notification
mechanisms and various resource name/key conversion functions."""

#standard lib
import os,os.path,sys
import cStringIO
from sets import Set
import logging
logger = logging.getLogger("neveredit.game")

#external lib
import Image
import TgaImagePlugin
import JpegImagePlugin
import BmpImagePlugin

#neveredit
from neveredit.util.Progressor import Progressor
import neveredit.file.MDLFile
import neveredit.file.KeyFile
import neveredit.file.ERFFile
import neveredit.file.GFFFile
import neveredit.file.TalkTableFile
import neveredit.file.TwoDAFile
import neveredit.file.TileSetFile
from neveredit.game.ChangeNotification import VisualChangeNotifier
from neveredit.game.ChangeNotification import ResourceListChangeNotifier
import neveredit.game.Module
import neveredit.game.Script

class ResourceManager(Progressor,VisualChangeNotifier,ResourceListChangeNotifier):
    '''The resource manager is a global object that takes care of loading
    an interpreting resources from the nwn install dir. You can get
    the instance of this class from neverglobals.getResourceManager().'''
    RESOURCETYPES = {
        'INVALID' : 0xFFFF,
        'BMP'     : 1,
        'TGA'     : 3,
        'WAV'     : 4,
        'PLT'     : 6,
        'INI'     : 7,
        'TXT'     : 10,
        'MDL'     : 2002,
        'NSS'     : 2009,
        'NCS'     : 2010,
        'ARE'     : 2012,
        'SET'     : 2013,
        'IFO'     : 2014,
        'BIC'     : 2015,
        'WOK'     : 2016,
        '2DA'     : 2017,
        'TXI'     : 2022,
        'GIT'     : 2023,
        'UTI'     : 2025,
        'UTC'     : 2027,
        'DLG'     : 2029,
        'ITP'     : 2030,
        'UTT'     : 2032,
        'DDS'     : 2033,
        'UTS'     : 2035,
        'LTR'     : 2036,
        'GFF'     : 2037,
        'FAC'     : 2038,
        'UTE'     : 2040,
        'UTD'     : 2042,
        'UTP'     : 2044,
        'DFT'     : 2045,
        'GIC'     : 2046,
        'GUI'     : 2047,
        'UTM'     : 2051,
        'DWK'     : 2052,
        'PWK'     : 2053,
        'JRL'     : 2056,
        'UTW'     : 2058,
        'SSF'     : 2060,
        'NDB'     : 2064,
        'PTM'     : 2065,
        'PTT'     : 2066}

    RESOURCEEXTENSIONS = dict(zip(RESOURCETYPES.values(),RESOURCETYPES.keys()))

    GFFFILETYPES = ['ARE','IFO','BIC','GIT','UTI','UTC','DLG','ITP','UTT',
                    'UTS','GFF','FAC','UTE','UTD','UTP','GIC','GUI','UTM',
                    'JRL','UTW','PTM','PTT']

    KEYFILES = ['chitin.key','patch.key','xp1.key','xp1patch.key',
                'xp2.key','xp2patch.key']
    
    appDir = ''

    def __init__(self):
        """
        Create a new resource manager object. This will not load the
        info from a game dir. You need to call L{scanGameDir} for that.
        Instead of manually making a resource manager, it is recommended
        you call L{neveredit.util.neverglobals.getResourceManager} which
        will use the user's preference settings to find the game dir and
        initialize the manager.
        """
        Progressor.__init__(self)
        VisualChangeNotifier.__init__(self)
        ResourceListChangeNotifier.__init__(self)
        self.cache = {}
        self.clear()
        self.module = None
        
    def clear(self):
        '''Discard all info this resource manager has loaded.'''
        self.keyResourceKeys = {}
        self.dirResourceKeys = {}
        self.hakResourceKeys = {}
        self.resourcesByType = {}
        self.hakFileNames = []
        self.mainDialogFile = None
        self.modMap = {}
        self.module = None

    def resTypeFromExtension(cls,ext):
        '''Class method that converts a resource type into a string extension'''
        return cls.RESOURCETYPES[ext.upper()]
    resTypeFromExtension = classmethod(resTypeFromExtension)
    
    def extensionFromResType(cls,type):
        '''Class method that converts a three letter string extension
        into a numerical resource type.'''
        try:
            return cls.RESOURCEEXTENSIONS[type]
        except KeyError:
            logger.error('type ' + `type` + 'unknown resource type')
            return 'UNK'
    extensionFromResType = classmethod(extensionFromResType)
    
    def nameFromKey(cls,key):
        '''Class method that converts a key into a filename.
        @param key: the key to convert
                    (16 byte resref,numerical resource type tuple)
        @return: the corresponding filename with extension
        '''
        return key[0].strip('\0') + '.' + cls.extensionFromResType(key[1])
    nameFromKey = classmethod(nameFromKey)
    
    def keyFromName(cls,name):
        '''Class method that converts a filename into a key.
        @param name: the filename (including extension) to convert
        @return: (16 byte resref,numerical resource type).'''
        parts = name.split('.')
        k1 = parts[0] + (16-len(parts[0]))*'\0'    
        try:
            k2 = cls.resTypeFromExtension(parts[1])
        except KeyError:
            #logger.error('unknown extension "' + parts[1].upper() + '"')
            raise ValueError,'unknown nwn extension .' + parts[1]
        return (k1,k2)
    keyFromName = classmethod(keyFromName)

    def getResourceFromCache(self,key):
        """Return a cached resource based on its key.
        @return: the resource, 'None' if no such resource cached."""
        return self.cache.get(key,None)
    
    def addResourceToCache(self,key,r):
        """Add a resource to this manager's cache. Will not replace
        if resource with this key already in cache.
        @param key: the key to add the resource under
        @param r: the resource to add
        """
        self.cache.setdefault(key,r)

    def clearCache(self):
        """Clear this manager's cache"""
        self.cache = {}

    def clearResourceCacheByExtension(self,ext):
        t = ResourceManager.resTypeFromExtension(ext)
        for key in self.cache:
            if t == key[1]:
                del self.cache[key]

    def interpretResourceContents(self,key,data):
        '''Take the raw binary data associated with a key and interpret it.
        This method will return a neveredit object instance such as
        a L{neveredit.file.GFFFile.GFFFile},
        L{neveredit.file.TwoDAFile.TwoDAFile},
        L{neveredit.file.MDLFile.Model} or similar.'''
        #could alternatively go by 'type' header field for many types...
        extension = ResourceManager.extensionFromResType(key[1])
        logger.debug('interpreting resource "' +
                     ResourceManager.nameFromKey(key) + '"')
        resource = None
        if extension in ResourceManager.GFFFILETYPES:
            resource = neveredit.file.GFFFile.GFFFile()
            resource.fromFile(cStringIO.StringIO(data),0)
        elif extension == 'NSS':
            resource = neveredit.game.Script\
                       .Script(ResourceManager.nameFromKey(key),data)
        elif extension == '2DA':
            resource = neveredit.file.TwoDAFile.TwoDAFile()
            resource.fromFile(cStringIO.StringIO(data))
        elif extension == 'TGA':
            resource = Image.open(cStringIO.StringIO(data))
        elif extension == 'MDL':
            f = neveredit.file.MDLFile.MDLFile()
            f.fromFile(cStringIO.StringIO(data))
            resource = f.getModel()
        elif extension == 'SET':
            resource = neveredit.file.TileSetFile.TileSetFile()
            resource.fromFile(cStringIO.StringIO(data))
        else:
            return data
        self.addResourceToCache(key,resource)
        return resource
    
    def scanGameDir(self,dirname):
        '''Scan an NWN install dir and store all the resource keys and
        hak files in it.
        @param dirname: the name of the directory to be scanned '''
        print >>sys.stderr,'initializing resource manager from "',dirname,'"',
        sys.stderr.flush()
        self.clear()
        self.setAppDir(dirname)
        if not os.path.exists(self.getAppDir()):
            logger.warning('dir given to resource manager does not exist')
            raise IOError("invalid path to NWN dir")
        c = 0.0
        for f in ResourceManager.KEYFILES:
            if os.path.exists(os.path.join(self.getAppDir(),f)):
                print >>sys.stderr,'.',
                sys.stderr.flush()
                self.addKeyFile(os.path.join(self.getAppDir(),f))
                c += 1
                self.setProgress((c/len(ResourceManager.KEYFILES))*100.0)
        files = os.listdir(self.getAppDir())
        for f in files:
            if f == 'dialog.tlk':
                self.mainDialogFile = neveredit.file\
                                      .TalkTableFile.TalkTableFile()
                self.mainDialogFile.fromFile(os.path.join(self.getAppDir(),f))
            if f == 'override':
                for over in os.listdir(os.path.join(self.getAppDir(),f)):
                    pass #should add override files here
            if f == 'hak':
                for hak in os.listdir(os.path.join(self.getAppDir(),f)):
                    if hak[-4:] == '.hak':
                        self.hakFileNames.append(hak)
            if f == 'modules':
                for mod in os.listdir(os.path.join(self.getAppDir(),f)):
                    if mod[-4:] == '.mod':
                        #self.addMODFile(os.path.join(self.getAppDir(),f,mod))
                        self.modMap[os.path.basename(f)] = os.path.join(self.getAppDir(),f)
        self.setProgress(0)
        print >>sys.stderr
        if not self.mainDialogFile:
            logger.warning('"' + self.getAppDir() +
                           '"' + " does not look like a valid NWN dir")

    def getDialogString(self,strref):
        '''look up a strref in dialog.tlk and return as a python string'''
        if not self.mainDialogFile:
            print >>sys.stderr,'not initialized, cannot return dialog string'
            return None
        else:
            return self.mainDialogFile.getString(strref)
        
    def getHAKFileNames(self):
        '''return a list of all hak file names found in the game install'''
        return self.hakFileNames

    def loadHAKsForModule(self,mod):
        '''Given a module, add all the resources in its hak files to the
        resource manager lookup tables. This will ignore the capitalization
        of both the hak file names stored in the module and of the hak files
        in the nwn installation directory.'''
        logger.debug('loading haks for "' + mod.getName() + '"')
        haks = [h.lower() for h in mod.getHAKNames()]
        haks.reverse() #reverse as later haks have lower priority
        lowerHakNames = [f.lower() for f in self.hakFileNames]
        for hak in haks:
            if not hak:
                continue
            if hak not in lowerHakNames:
                logger.warning('Could not find hak ' + hak
                               + ' amongst installed haks')
            else:
                hakName = self.hakFileNames[lowerHakNames.index(hak)]
                self.addHAKFile(os.path.join(self.getAppDir(),'hak',hakName))
                
    def addKeyFile(self,keyf):
        keyFile = neveredit.file.KeyFile.KeyFile(self.getAppDir())
        keyFile.fromFile(keyf)
        keyList = keyFile.getKeyList()
        for key in keyList:
            self.keyResourceKeys[key] = keyFile
        self.buildResourceTable()

    def addHAKFile(self,hak):
        logger.debug('adding hak "' + hak + '"')
        hakFile = neveredit.file.ERFFile.ERFFile()
        hakFile.fromFile(hak)
        keyList = hakFile.getKeyList()
        for key in keyList:
            self.hakResourceKeys[key] = hakFile

    def getMODPath(self,m):
        return self.modMap.get(m,m)
    
    def addMODFile(self,erf):
        mod = neveredit.game.Module.Module(erf)
        self.addModule(mod)

    def addModule(self,mod):
        self.cleanMODandHAKKeys()
        self.module = mod
        keyList = mod.getKeyList()
        for key in keyList:
            self.dirResourceKeys[key] = mod.getERFFile()
        self.loadHAKsForModule(mod)
        self.buildResourceTable()
        
    def buildResourceTable(self):
        for key in self.hakResourceKeys.keys() +\
            self.dirResourceKeys.keys() +\
            self.keyResourceKeys.keys():
            self.resourcesByType.setdefault(key[1],Set()).add(key)
            
    def cleanMODandHAKKeys(self):
        self.dirResources = {}
        self.hakResources = {}
        self.buildResourceTable()
        self.clearCache()
        
    def getRawResource(self,key):
        if key in self.hakResourceKeys:
            return self.hakResourceKeys[key].getRawResource(key)
        elif key in self.dirResourceKeys:
            return self.dirResourceKeys[key].getRawResource(key)
        elif key in self.keyResourceKeys:
            return self.keyResourceKeys[key].getRawResource(key)
        else:
            logger.error('cannot find resource for ' + `key` +
                         'in any added lists')
            return None

    def getRawResourceByName(self,name):        
        key = ResourceManager.keyFromName(name)
        return self.getRawResource(key)

    def getResource(self,key,copy=False):
        r = self.getResourceFromCache(key)
        if not copy and r:
            return r
        deleteCache = copy and not r
        resource = None
        if key in self.hakResourceKeys:
            resource = self.hakResourceKeys[key].getResource(key)
        elif key in self.dirResourceKeys:
            resource = self.dirResourceKeys[key].getResource(key)
        elif key in self.keyResourceKeys:
            resource = self.keyResourceKeys[key].getResource(key)
        else:
            logger.error('cannot find resource for ' + `key` +
                         'in any added lists')
        if resource and deleteCache:
            del self.cache[key]
        return resource

    def getResourceByName(self,name,copy=False):
        '''This method take a filename and returns an interpreted resource
        if such a resource exists.'''
        key = ResourceManager.keyFromName(name)
        return self.getResource(key,copy)

    def getKeysWithName(self,name):
        keys = []
        for keySet in self.resourcesByType.values():
            keys.extend([key for key in keySet
                         if key[0].strip('\0').lower() == name.lower()])
        return keys
    
    def getKeysWithType(self,type):
        return self.resourcesByType[type]
    
    def getKeysWithExtensions(self,ext):
        return self.resourcesByType[ResourceManager.resTypeFromExtension(ext)]

    def getDirKeysWithExtensions(self,ext):
        keys = self.getKeysWithExtensions(ext)
        return [k for k in keys if k in self.dirResourceKeys]
    
    def getTextScriptKeys(self):
        return self.getKeysWithExtensions('nss')

    def getAppDir(cls):
        return cls.appDir
    getAppDir = classmethod(getAppDir)

    def setAppDir(cls,dir):
        cls.appDir = dir
    setAppDir = classmethod(setAppDir)

    def getPortraitByIndex(self,index,size):
        twoda = self.getResourceByName('portraits.2da')
        entry = twoda.getEntry(index,'BaseResRef').lower()
        if not entry or entry == '****':
            logger.warning('empty portrait entry for ' + `index` + ' ' +
                           `size`)
            return None
        name = 'po_' + entry + size + '.tga'
        return self.getResourceByName(name)

    def getPortraitNameList(self):
        portraits = Set()
        for key in self.getKeysWithExtensions('TGA'):
            if key[0][:3] == 'po_':
                portraits.add(key[0].strip('\0')[:-1])
        return list(portraits)
    
