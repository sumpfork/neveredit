import logging
logger = logging.getLogger("neveredit.file")

import sys,os
import pprint
import time

from neveredit.util import neverglobals
import neveredit.game.ResourceManager
from neveredit.file.NeverFile import NeverFile

class ERFKey:
    def __init__(self,n='',i=0,t=0,o=0,s=0):
        self.name = n
        self.id = i
        self.type = t
        self.offset = o
        self.size = s
        self.contents = None

    def getPrintableName(self):
        return self.name.strip('\0')
    
    def __str__(self):
        stringtype = neveredit.game.ResourceManager.ResourceManager\
                     .extensionFromResType(self.type)
        s = 'name: ' + self.name + ' id: ' + `self.id` + ' type: '\
            + stringtype + ' offset: ' + `self.offset` + ' size: '\
            + `self.size`
        return s

    def __repr__(self):
        return 'ERFKey(' + `self.name` + ',' + `self.id` + ',' + `self.type`\
               + ',' + `self.offset` + ',' + `self.size` + ')'

class ERFFile(NeverFile):
    """A class encapsulating a Bioware ERF file.
    This class contains two sets of data structures. One set is a flat
    structure that closely corresponds to the actual ERF file data as it
    is stored on disk. The other is a tree that corresponds to the conceptual
    structure of an ERF file. Given a file, this class first reads most
    of the flat structures from the file, and then constructs the tree in
    memory (while still reading some of the flat structure). It will delay
    reading the actual contents of the ERF file files until they are requested.
    Once build, clients can work with and modify the tree structure. When asked
    to save back to a file, this class will flatten the tree structures into
    its flat structures, then saves these to the file."""

    class RawContentWrapper:
        '''a class to give raw contents a "toFile" method for writing'''
        def __init__(self,rawContent):
            self.content = rawContent
            
        def toFile(self,f,offset):
            f.seek(offset)
            f.write(self.content)

    HEADERSIZE = 160
    
    def __init__(self,typ='ERF'):
        '''Create an empty erf file.
        @param typ: one of "ERF" (the default), "MOD", "SAV", "HAK" depending on the type
                    of erf to be created.
        '''
        NeverFile.__init__(self)
        self.filename = ""
        self.readFileHandle = None
        self.writeFileHandle = None
    
        self.languageCount = 0
        self.localizedStringSize = 0
        self.entryCount = 0
        self.offsetToLocalizedString = ERFFile.HEADERSIZE
        self.offsetToKeyList = ERFFile.HEADERSIZE
        self.offsetToResourceList = ERFFile.HEADERSIZE
        self.buildYear = time.localtime().tm_year - 1900
        self.buildDay = time.localtime().tm_yday
        self.descriptionRef = ""

        self.localizedStrings = {}
        
        self.entriesByType = {}
        self.entriesByNameAndType = {}

        self.version = 'V1.0'
        typ = typ.upper()
        if typ not in ["ERF","MOD","SAV","HAK"]:
            raise ValueError,'invalid erf type ' + typ
        self.type = typ + ' '
            
    def headerFromFile(self,f):
        NeverFile.headerFromFile(self,f)
        self.languageCount = self.dataHandler.readIntFile(f)
        self.localizedStringSize = self.dataHandler.readIntFile(f)
        self.entryCount = self.dataHandler.readIntFile(f)
        self.offsetToLocalizedString = self.dataHandler.readIntFile(f)
        self.offsetToKeyList = self.dataHandler.readIntFile(f)
        self.offsetToResourceList = self.dataHandler.readIntFile(f)
        self.buildYear = self.dataHandler.readIntFile(f)
        self.buildDay = self.dataHandler.readIntFile(f)
        self.descriptionRef = f.read(4)
        f.seek(116,1) #skip header padding

    def recalculateParams(self):
        """recalculate the offsets and sizes to be written to a file"""
        self.localizedStringSize = self.calcLocalizedStringsSize()
        self.languageCount = len(self.localizedStrings.keys())
        self.entryCount = len(self.entriesByNameAndType)
        offset = ERFFile.HEADERSIZE
        offset += self.localizedStringSize
        self.offsetToKeyList = offset
        offset += self.calcKeyListSize()
        self.offsetToResourceList = offset

    def headerToFile(self):
        """output the header info of the ERF file"""
        self.writeFileHandle.write(self.type)
        self.writeFileHandle.write(self.version)
        self.dataHandler.writeIntFile(self.languageCount,self.writeFileHandle)
        self.dataHandler.writeIntFile(self.localizedStringSize,self.writeFileHandle)
        self.dataHandler.writeIntFile(self.entryCount,self.writeFileHandle)
        self.dataHandler.writeIntFile(self.offsetToLocalizedString,self.writeFileHandle)
        self.dataHandler.writeIntFile(self.offsetToKeyList,self.writeFileHandle)
        self.dataHandler.writeIntFile(self.offsetToResourceList,self.writeFileHandle)
        self.dataHandler.writeIntFile(self.buildYear,self.writeFileHandle)
        self.dataHandler.writeIntFile(self.buildDay,self.writeFileHandle)
        self.writeFileHandle.write(self.descriptionRef)
        self.writeFileHandle.write(116*'\0')
            
    def readLocalizedStrings(self):
        """read the ERF localized string file section"""
        self.readFileHandle.seek(self.offsetToLocalizedString)
        for i in range(self.languageCount):
            (langID,s) = self.dataHandler.readLocalizedString(self.readFileHandle)
            self.localizedStrings[langID] = s

    def writeLocalizedStrings(self):
        """write the ERF localized string file section"""
        self.writeFileHandle.seek(self.offsetToLocalizedString)
        for s in self.localizedStrings:
            self.dataHandler.writeLocalizedStringFile(s,self.localizedStrings[s],self.writeFileHandle)
        
    def calcLocalizedStringsSize(self):
        """calculate the size the ERF localized string section will take"""
        s = 0
        for lID in self.localizedStrings:
            s += 8 #langID and size
            s += len(self.localizedStrings[lID])
        return s
    
    def readKeysAndResourceList(self):
        """read the key and resources ERF sections"""
        self.readFileHandle.seek(self.offsetToKeyList)
        keys = []
        for i in range(self.entryCount):
            k = ERFKey()
            k.name = self.dataHandler.readResRef(self.readFileHandle)#.strip('\0')
            k.id = self.dataHandler.readIntFile(self.readFileHandle)
            k.type = self.dataHandler.readWordFile(self.readFileHandle)
            self.readFileHandle.seek(2,1) #unused
            keys.append(k)
        self.readFileHandle.seek(self.offsetToResourceList)
        for k in keys:
            k.offset = self.dataHandler.readIntFile(self.readFileHandle)
            k.size = self.dataHandler.readIntFile(self.readFileHandle)
            #print 'found entry of type',self.typeToText(k.type)
            if k.type in self.entriesByType.keys():
                self.entriesByType[k.type].append(k)
            else:
                self.entriesByType[k.type] = [k]
            if (k.name,k.type) in self.entriesByType.keys():
                print 'error, ',(k.name,k.type),'already present as key'
            self.entriesByNameAndType[(k.name,k.type)] = k

    def writeKeys(self):
        """write the key section of an ERF file"""
        self.writeFileHandle.seek(self.offsetToKeyList)
        entryList = [(int(x.id),x) for x in self.entriesByNameAndType.values()]
        entryList.sort()
        for e in entryList:
            k = e[1]
            self.dataHandler.writeResRef(k.name,self.writeFileHandle)
            self.dataHandler.writeIntFile(k.id,self.writeFileHandle)
            self.dataHandler.writeWordFile(k.type,self.writeFileHandle)
            self.writeFileHandle.write(2*'\0')

    def writeResourceList(self):
        """write the resource list section of an ERF file.
        Note that this should only be done AFTER the resources have been written,
        because we do not know their sizes and locations beforehand."""        
        self.writeFileHandle.seek(self.offsetToResourceList)
        entryList = [(int(x.id),x) for x in self.entriesByNameAndType.values()]
        entryList.sort()
        for e in entryList:
            k = e[1]
            self.dataHandler.writeIntFile(k.offset,self.writeFileHandle)
            self.dataHandler.writeIntFile(k.size,self.writeFileHandle)
    
    def calcKeyListSize(self):
        """calculate the size the key list will take up"""
        #the toolset writes lots of extra 0 bytes after the keys for some
        #reason, 8 for each entry. The game will happily load modules that
        #don't have this padding, but the toolset complains, so I'm now
        #padding, too, to make it shut up.
        return len(self.entriesByNameAndType) * 32 #24 is enough

    def calcResourceListSize(self):
        """calculate the size the resource list will take up"""
        return len(self.entriesByNameAndType) * 8
        
    def fromFile(self,fname):
        """initialize an ERF file from a file (does not initialize the files contained
        in this ERF file)."""
        logger.debug('fromFile("' + fname + '")')
        self.filename = fname
        self.readFileHandle = NeverFile.fromFile(self,fname)
        self.readLocalizedStrings()
        self.readKeysAndResourceList()

    def extractEntry(self,name):
        """
        extract an entry with the given name into a file with the same name in the current
        directory.
        @param name: the entry/file name to extract
        """
        key = neveredit.game.ResourceManager\
              .ResourceManager.keyFromName(name)
        entry = self.entriesByNameAndType[key]
        f = open(name.lower(),'wb')
        f.write(self.getRawEntryContents(entry))
        f.close()
        
    def extractAllEntries(self,verbose=False):
        '''extract all entries to be files in the current working directory.
        The files will have names of the form resref.ext.'''
        self.recalculateParams()
        for key,entry in self.entriesByNameAndType.iteritems():
            fname = neveredit.game.ResourceManager\
                    .ResourceManager.nameFromKey(key)
            f = open(fname.lower(),'wb')
            f.write(self.getRawEntryContents(entry))
            f.close()
            if verbose:
                print fname.lower()

    def writeEntries(self):
        """write the actual file entries of this ERF file. This method
        will ask the contents to write themselves by calling 'toFile' on
        them, because they may have changed without our knowledge. However,
        if the contents have never been read, this method will read them
        from the read file and write them out to the file being written,
        meaning that we can never write directly to the file we're reading
        (which is a good thing)."""
        offset = self.offsetToResourceList + self.calcResourceListSize()
        self.writeFileHandle.seek(offset)
        entryList = [(int(x.id),x) for x in self.entriesByNameAndType.values()]
        entryList.sort()
        for e in entryList:
            entry = e[1]
            if entry.contents:
                contents = self.getEntryContents(entry)
                contents.toFile(self.writeFileHandle,offset)
            else:
                contents = self.getRawEntryContents(entry)
                self.writeFileHandle.write(contents)
            entry.offset = offset
            entry.size = self.writeFileHandle.tell() - entry.offset
            offset += entry.size

    def saveToReadFile(self):
        """this method simulates writing back out to the file that this ERF
        file was read from. It actually writes a temp file, then moves this
        file to overwrite the old read file."""
        #the next line generates a warning, but I don't know how to
        #do the following
        #rename with tmpfile
        tmp = os.tmpnam()
        self.toFile(tmp)
        self.close()
        print 'renaming',self.writeFileHandle.name,self.readFileHandle.name
        if os.name == 'nt' and os.path.exists(self.readFileHandle.name):
            os.remove(self.readFileHandle.name)
        try:
            os.rename(self.writeFileHandle.name,self.readFileHandle.name)
        except OSError: #may be on different file systems
            print 'failed rename (different filesystems?), trying copy instead'
            ftmp = open(tmp,'rb')
            f = open(self.readFileHandle.name,'wb')
            f.write(ftmp.read())
            ftmp.close()
            f.close()
            os.remove(tmp)
        self.reOpenRead()
        
    def toFile(self,fname=''):
        """write this ERF to a file"""
        if len(fname) > 0:
            if self.readFileHandle and fname == self.readFileHandle.name:
                print 'error, ERFFile cannot write to file it is reading from'
                return
            self.writeFileHandle = open(fname,'wb')
        self.recalculateParams()
        print self.infoStr()
        self.headerToFile()
        self.writeLocalizedStrings()
        self.writeKeys()
        self.writeEntries() #do this first, so sizes & offsets are correct
        self.writeResourceList()
        self.writeFileHandle.flush()
        self.writeFileHandle.close()
        if self.filename:
            self.readFileHandle = open(self.filename,'rb')

    def reassignReadFile(self,fname):
        self.filename = fname
        self.readFileHandle = open(self.filename,'rb')

    def addFile(self,fname):
        """add another ERF file's entries to this one -
        skips localized strings and does not replace entries
        already present (as determined by their key).
        Note that this will save the file."""
        other = ERFFile()
        other.fromFile(fname)
        
        #don't use the localized strings from the file being added

        #update the entry list by adding entries from the other
        #file if they don't yet exist
        for (name,type),entry in other.entriesByNameAndType.iteritems():
            if (name,type) not in self.entriesByNameAndType.keys():
                entry.contents = ERFFile.RawContentWrapper(other.getRawEntryContents(entry))
                entry.id = len(self.entriesByNameAndType)
                self.entriesByNameAndType[(name,type)] = entry
                if type in self.entriesByType.keys():
                    self.entriesByType[type].append(entry)
                else:
                    self.entriesByType[type] = [entry]

        #transfer contents to original file
        self.saveToReadFile()
        other.close()
        #force all entry contents to be re-interpreted
        for entry in self.entriesByNameAndType.values():
            entry.contents = None

    def addRawResourceByName(self,name,r):
        self.addResourceByName(name,ERFFile.RawContentWrapper(r))
        
    def addResourceByName(self,name,r):
        key = neveredit.game.ResourceManager.ResourceManager.keyFromName(name)
        self.addResource(key,r)
        
    def addResource(self,key,r):
        entry = ERFKey()
        if key in self.entriesByNameAndType:
            entry.id = self.entriesByNameAndType[key].id
        else:
            entry.id = len(self.entriesByNameAndType)            
        entry.name = key[0]
        entry.type = key[1]
        entry.contents = r
        self.entriesByNameAndType[key] = entry
        self.entriesByType[key[1]] = entry
        
    def close(self):
        """close all the read and write file this class might have opened."""
        if self.readFileHandle:
            self.readFileHandle.close()
        if self.writeFileHandle:
            self.writeFileHandle.close()

    def reOpenRead(self):
        """re-open the read file of this class in case it was closed."""
        if self.readFileHandle:
            self.readFileHandle = open(self.readFileHandle.name,'rb')
    
    def getReadFileName(self):
        """get the filename this class was read from."""
        return self.readFileHandle.name
    
    def getEntriesWithExtension(self,ext):
        """get all the entries that have a given extension.
        @param ext: the extension to look up
        @return: a list of ERFKey objects"""
        type = neveredit.game.ResourceManager\
               .ResourceManager.resTypeFromExtension(ext)
        try:
            temp = self.entriesByType[type]
            if not isinstance(temp,list):
                #then we have only one element, not in a list
                entry = [temp]
            else:
                entry = temp
        except KeyError:
            entry = []
        return entry

    def getEntryByNameAndExtension(self,name,ext):
        """get an entry with a specific name and extension (that's
        equivalent to looking up by key).
        @param name: the name to look up
        @param ext: the extension to look up
        @return: the ERFKey with this name and extension, None, if not in this file"""
        name += (16-len(name))*'\0'
        type = neveredit.game.ResourceManager\
               .ResourceManager.resTypeFromExtension(ext)
        return self.entriesByNameAndType.get((name,type), None)

    def getRawEntryContents(self,entry):
        """get the raw contents of a given entry as a byte string"""
        self.readFileHandle.seek(entry.offset)
        return self.readFileHandle.read(entry.size)
    
    def getEntryContents(self,entry):
        """get the contents of an entry as interpreted by the ResourceManager.
        This will not re-read them if they've already been read."""
        if not entry.contents:
            raw = self.getRawEntryContents(entry)
            c = neverglobals.getResourceManager()\
                .interpretResourceContents((entry.name,entry.type),raw)
            entry.contents = c
        return entry.contents

    def setEntryContents(self,entry,contents):
        """set the contents of an entry. Does a simple set."""
        entry.contents = contents
        
    def getKeyList(self):
        """Get a list of all keys stored in this ERF file."""
        return self.entriesByNameAndType.keys()

    def __iter__(self):
        """iterator through keys"""
        for key in self.entriesByNameAndType:            
            yield key
            
    def __getitem__(self,name):
        """return a resource in this ERF by name"""
        return self.getResourceByName(name)

    def getResourceByName(self,name):
        """return a resouce in this ERF by name"""
        key = neveredit.game.ResourceManager.ResourceManager.keyFromName(name)
        return self.getResource(key)

    def getResourceData(self,key):
        """get the raw data of an entry corresponding to the given key.
        Just like getRawEntryContents, but with a key interface."""
        extension = neveredit.game.ResourceManager.ResourceManager\
                    .extensionFromResType(key[1])
        return self.getRawEntryContents(self\
                                        .getEntryByNameAndExtension(key[0],
                                                                    extension))

    def getResource(self,key):
        """Get the contents of an entry specified by a key (Just like
        getEntryContents, but with a key)."""
        extension = neveredit.game.ResourceManager\
                    .ResourceManager.extensionFromResType(key[1])
        return self.getEntryContents(self.getEntryByNameAndExtension(key[0],
                                                                     extension))

    def getRawResource(self,key):
        """Get the raw bytes of an entry specified by a key"""
        extension = neveredit.game.ResourceManager\
                    .ResourceManager.extensionFromResType(key[1])
        return self.getRawEntryContents(self.getEntryByNameAndExtension(key[0],
                                                                     extension))
    def infoStr(self):
        s = 'erf type/version: ' + `self.type` + '/' + self.version + '\n'
        s += 'build year/day: ' + `self.buildYear + 1900` + '/' + `self.buildDay` + '\n'
        s += 'header size: ' + `self.offsetToLocalizedString` + '\n'
        s += 'erf description in ' + `self.languageCount` + ' languages, using '\
             + `self.localizedStringSize` + ' bytes' + '\n'
        s += 'erf has ' + `self.entryCount` + ' entries' + '\n'
        return s
    
    def __str__(self):
        s =  'ERFFile ' + self.filename + '\n'
        s += self.infoStr()
        s += self.descriptionRef + '\n'
        s += pprint.PrettyPrinter().pformat(self.localizedStrings)
        s += pprint.PrettyPrinter().pformat(self.entriesByNameAndType)
        return s
        
if __name__ == "__main__":
    if(len(sys.argv) >= 2):
        f = ERFFile()
        f.fromFile(sys.argv[1])
        print f
        if len(sys.argv) >= 3:
            f.toFile(sys.argv[2])
    else:
        print 'usage:',sys.argv[0],'<filename>'



            
            
        
