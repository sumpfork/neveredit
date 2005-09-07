'''Classes for handling nwn modules'''

import logging
logger = logging.getLogger('neveredit')

import neveredit.file.ERFFile
from neveredit.file.GFFFile import GFFStruct
from neveredit.game.Area import Area
from neveredit.game.NeverData import NeverData
from neveredit.util import neverglobals
from neveredit.util.Progressor import Progressor

class Module(Progressor,NeverData):    
    """A class the encapsulates an NWN module file and gives access
    to entities contained therein, such as doors and scripts."""
    ifoPropList = {
        "Mod_CustomTlk":"CExoString",
        "Mod_DawnHour":"Integer,0-23",
        "Mod_Description":"CExoLocString,4",
        "Mod_DuskHour":"Integer,0-23",
        "Mod_Entry_Area":"ResRef,ARE",
        "Mod_HakList":"CheckList,HAKs",
        "Mod_Hak":"CheckList,HAK",
        "Mod_Name":"CExoLocString",
        "Mod_MinPerHour": "Integer,1-255",
        "Mod_OnAcquirItem": "ResRef,NSS",
        "Mod_OnActvtItem": "ResRef,NSS",
        "Mod_OnClientEntr": "ResRef,NSS",
        "Mod_OnClientLeav": "ResRef,NSS",
        "Mod_OnCutsnAbort": "ResRef,NSS",
        "Mod_OnHeartbeat": "ResRef,NSS",
        "Mod_OnModLoad": "ResRef,NSS",
        "Mod_OnModStart": "ResRef,NSS",
        "Mod_OnPlrDeath": "ResRef,NSS",
        "Mod_OnPlrDying": "ResRef,NSS",
        "Mod_OnPlrEqItm": "ResRef,NSS",
        "Mod_OnPlrLvlUp": "ResRef,NSS",
        "Mod_OnPlrRest": "ResRef,NSS",
        "Mod_OnPlrUnEqItm": "ResRef,NSS",
        "Mod_OnSpawnBtnDn": "ResRef,NSS",
        "Mod_OnUnAqreItem": "ResRef,NSS",
        "Mod_OnUsrDefined": "ResRef,NSS",
        "Mod_StartDay": "Integer,1-31",
        "Mod_StartHour": "Integer,0-23",
        "Mod_StartMonth": "Integer,1-24",
        "Mod_StartYear": "Integer,0-2000",
        "Mod_Tag": "CExoString",
        "Mod_XPScale": "Integer,0-255",
        "Mod_Area_list": "Hidden"
        }
    
    def __init__(self,fname):
        NeverData.__init__(self)
        self.needSave = False
        logger.debug("reading erf file %s",fname)
        self.erfFile = neveredit.file.ERFFile.ERFFile()
        self.erfFile.fromFile(fname)
        ifoEntry = self.erfFile.getEntryByNameAndExtension("module","IFO")
        self.addPropList('ifo',self.ifoPropList,
                         self.erfFile.getEntryContents(ifoEntry).getRoot())
        logger.debug("checking for old style Mod_Hak")
        prop = self['Mod_Hak']
        if prop != None:
            logger.info('Old-Style Mod_Hak found,'
                        'changing to new style Mod_HakList')
            new_prop = self['Mod_HakList']
            if not new_prop:
                self.getGFFStruct('ifo').add('Mod_HakList',[],'List')
                new_prop = self['Mod_HakList']
            if prop:
                new_prop.append(prop)
            self.needSave = True
            
	prop = self['Mod_CustomTlk']
	if prop == None:
            logger.info("Old (pre-1.59) module with no Mod_CustomTlk,"
                        "adding an empty one")
            self.getGFFStruct('ifo').add('Mod_CustomTlk',"",'CExoString')
            self.needSave = True
                
        self.scripts = None
        self.conversations = None
        self.areas = {}
    
    def getFileName(self):
        return self.erfFile.filename
    
    def removeProperty(self,label):
        if label in self.ifoPropList:
            (s,t) = self.gffstructDict['ifo'].getTargetStruct(label)
            print 'removing',t
            s.removeEntry(t)

    def getHAKNames(self):
        if self['Mod_HakList'] != None:
            return [p['Mod_Hak'] + '.hak'
                    for p in self['Mod_HakList']]
        elif self['Mod_Hak'] != None:
            return [self['Mod_Hak']]
        else:
            return []
    
    def getName(self,lang=0):
        '''Looks up Mod_Name in the ifo file'''
        return self['Mod_Name'].getString(lang)
    
    def getAreaNames(self):
        '''Returns a list of area resref names
        @return: list of area resrefs
        '''
        return [a['Area_Name'] for a in self['Mod_Area_list']]

    def getArea(self,name):
        '''Get an area by its name
        @param name: name of the area object to return'''
        if name in self.areas:
            return self.areas[name]
        else:
            a = Area(self.erfFile,name)
            self.areas[name] = a
            return a

    def getEntryArea(self):
        return self.getArea(self['Mod_Entry_Area'])
    
    def getAreas(self):
        """Get the areas in this ERF.
        @return: a dict of Area names (keys) and objects (values)."""
        names = self.getAreaNames()
        areas = {}
        c = 1.0
        for n in names:
            self.setProgress((c/len(names))*100.0)
            areas[n] = self.getArea(n)
            c += 1
        self.setProgress(0)
        return areas

    def getTags(self):
        """Get a dictionary of all tags in this module.
        The dictionary will look like this::
        
        {
        'module': <module_Tag>,
        'areas':  {<area_tag>: <tag_dict_for_area>}
        }

        Where <tag_dict_for_area> is the dictionary produced by
        L{neveredit.game.Area.Area.getTags} for the area in question.

        Note that this function needs to read all areas and their
        contents, and thus will be slow unless they're already
        loaded.
        
        @return: the tag dictionary for this module
        """
        
        tags = {}
        tags['module'] = self['Mod_Tag']
        tags['areas'] = {}
        for a in self.getAreas().values():
            tags['areas'][a['Tag']] = a.getTags()
        return tags
    
    def getConversations(self):
        """Get the conversations in this ERF.
        @return: A dict of name:L{neveredit.game.Conversation.Conversation} objects."""
        if not self.conversations:
            entries = self.erfFile.getEntriesWithExtension('DLG')
            self.conversations = {}
            for s in entries:
                self.conversations[s.name.strip('\0')] = self.erfFile.getEntryContents(s)
        return self.conversations

    def getScripts(self):
        """Get the scripts in this ERF.
        @return: A dict of name:Script objects."""
        if not self.scripts:
            entries = self.erfFile.getEntriesWithExtension('NSS')
            self.scripts = {}
            for s in entries:
                self.scripts[s.name.strip('\0')] = self.erfFile.getEntryContents(s)
        return self.scripts

    def addScript(self,s):
        if not self.scripts:
            self.getScripts()
        self.scripts[s.getName()[:-4]] = s
        self.commit()
        neverglobals.getResourceManager().moduleResourceListChanged()
        
    def commit(self):
        if self.scripts:
            for s in self.scripts.values():
                self.erfFile.addResourceByName(s.getName(),s)
                if s.getCompiledScript():
                    self.erfFile.addResourceByName(s.getName()[:-4] + '.ncs',s.getCompiledScript())
                    
    def saveToReadFile(self):
        self.commit()
        self.erfFile.saveToReadFile()

    def toFile(self,fpath):
        self.commit()
        self.erfFile.toFile(fpath)

    def saveAs(self,fpath):
        self.commit()
        self.erfFile.toFile(fpath)
        self.erfFile.reassignReadFile(fpath)

    def addResourceFile(self,fname):
        self.erfFile.addRawResourceByName(fname,open(fname,'rb').read())
        
    def addERFFile(self,fname):
        self.erfFile.addFile(fname)

    def getKeyList(self):
        return self.erfFile.getKeyList()

    def getERFFile(self):
        return self.erfFile
    
    def setProgressDisplay(self,p):
        self.erfFile.setProgressDisplay(p)

    def getEntriesWithExtension(self,ext):
        return self.erfFile.getEntriesWithExtension(ext)

    def setProgress(self,p):
        self.erfFile.setProgress(p)
