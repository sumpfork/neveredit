# -*- coding: latin-1 -*-

import logging
logger = logging.getLogger("neveredit.file")

import sys
import copy

from neveredit.file.NeverFile import NeverFile
from neveredit.file import CExoLocString

FIELDTYPES = {
    0 : 'BYTE',
    1 : 'CHAR',
    2 : 'WORD',
    3 : 'SHORT',
    4 : 'DWORD',
    5 : 'INT',
    6 : 'DWORD64',
    7 : 'INT64',
    8 : 'FLOAT',
    9 : 'DOUBLE',
    10 : 'CExoString',
    11 : 'ResRef',
    12 : 'CExoLocString',
    13 : 'VOID',
    14 : 'Struct',
    15 : 'List' }

FIELDTYPENAMES = {
    'BYTE'    : 0,
    'CHAR'    : 1,
    'WORD'    : 2,
    'SHORT'   : 3,
    'DWORD'   : 4,
    'INT'     : 5,
    'DWORD64' : 6,
    'INT64'   : 7,
    'FLOAT'   : 8,
    'DOUBLE'  : 9,
    'CExoString'    : 10,
    'ResRef'        : 11,
    'CExoLocString' : 12,
    'VOID'          : 13,
    'Struct'        : 14,
    'List'          : 15 }

class GFFStruct:
    ''' A class that represents a GFF structure as used by GFFFile
   * GFFStruct.entries is a dictionnary {label: [value,type],...}, possible types are given
   in the tables above (FIELDTYPES and FIELDTYPENAMES). The List and Struct types will allow
   to nest GFFStructs.
   * The function getTargetStruct allows to refer to members of a struct e.g.
       'AreaProperties.AmbientSndDayVol' refers to AmbientSndDayVol substructure of AreaProperties
       calling getTargetStruct() on it will thus return <AGFFStruct>,AmbientSndDayVol'''

    def __init__(self,t=0):
        self.type = t
        self.entries = {}

    def setType(self, t):
        self.type = t

    def getType(self):
        return self.type
    
    def addEntry(self, label, entry):
        if label in self.entries.keys():
            logger.warning('adding "' + label
                           + '" - it already exists in struct')
        else:
            self.entries[label] = entry

    def add(self,label,value,typename):
        """
        Add an entry to this GFF structure.
        @param label: the label for the entry
        @param value: the entry's value
        @param typename: the entry's type, chosen from L{FIELDTYPENAMES}
        """
        self.addEntry(label,(value,FIELDTYPENAMES[typename]))

    def __getitem__(self,key):
        return self.getEntry(key)[0]

    def __delitem__(self,key):
        self.removeEntry(key)

    def __setitem__(self,key,value):
        self.setInterpretedEntry(key,value)

    def __contains__(self,key):
        return self.hasEntry(key)
    
    def getEntry(self, label):
        return self.getEntryHelper(label)[0]

    def getLabeledEntry(self,spec):
        return self.getEntryHelper(spec)

    def getEntryHelper(self,spec):
        (s,l) = self.getTargetStruct(spec)
        return (s.entries[l],l)
    
    def getTargetStruct(self,spec):
        '''traverse a GFFFile according to a specification with
        periods separating structure names and return the target
        structure of the specification as well as the target
        entry label.'''        
        structNames = spec.split('.')
        targetStruct = self
        for s in structNames[:-1]:
            targetStruct = targetStruct[s]
        return (targetStruct,structNames[-1])

    def getEntryNames(self):
        return self.entries.keys()
    
    def hasEntry(self, label):
        try:
            s = self.getTargetStruct(label)[0]
            return label in s.entries
        except KeyError:
            return False
    
    def getInterpretedEntry(self, label):
        try:
            entry = self.getEntry(label)
        except KeyError:
            #print >>sys.stderr,'no entry with label',label,'in getInterpretedEntry'
            return None
        t = FIELDTYPES[entry[1]]
        if t == 'CExoLocString':
            return CExoLocString.CExoLocString(entry[0])
        else:
            return entry[0]

    def setInterpretedEntry(self,label,value):
        try:
            s,n = self.getTargetStruct(label)
            entry = s.getEntry(n)
        except KeyError:
            if label != 'Mod_HakList': #upgrade mod file
                print >>sys.stderr,'error in setInterpretedEntry: only existing entries accepted',label
                print >>sys.stderr,'possible entries are:',s.getEntryNames()
                return
            else:
                s.entries[n] = (value,FIELDTYPENAMES['List'])
                return
        if entry[1] == FIELDTYPENAMES['CExoLocString']\
           and value.__class__ != CExoLocString.CExoLocString:
            logger.info("making new CExoLocString")
            value = CExoLocString.CExoLocString(value)
        if value.__class__ == CExoLocString.CExoLocString:                
            s.entries[n] = (value.toGFFEntry(),entry[1])
        else:
            s.entries[n] = (value,entry[1])
            
    def removeEntry(self,label):
        s,t = self.getTargetStruct(label)
        if label in s.entries:
            del s.entries[label]
        
    def __str__(self):        
        s = 'type: ' + `self.type` + ' entries: ' + `self.getEntryNames()`
        return s

    def __repr__(self):
        return self.__str__()

    def clone(self):
        return copy.deepcopy(self)
    
class GFFFile(NeverFile):    
    ''' A class that represents a GFF file (one of the basic file formats in NWN)

   The data is stored as in a tree, with nested structures. Each structure (except for
   anonymous data in a List for example) has a label, a data type, and data.
   * A GFFFile has a field named rootStructure that is the parent of all GFF Structs
   in the file.
   * many fields refer to physical data of the GFF file, i.e. offsets for specific places
   in the file (see clearHeaderData)
   * GFFFile.structs is a list of physical (file) GFF struct data (!= GFFStruct class as it's a
   binary file representation). GFFFile.fields and GFFFile.labels are the same thing for GFF
   fields (data) and labels.'''

    def __init__(self):
        NeverFile.__init__(self)
        self.clearHeaderData()
        self.clearFlats()
        
        self.rootStructure = None
    
        self.offset = 0

        self.fieldData = ''

    def clearHeaderData(self):
        self.type = ''
        self.version = ''
        self.structOffset = 0
        self.structCount = 0
        self.fieldOffset = 0
        self.fieldCount = 0
        self.labelOffset = 0
        self.labelCount = 0
        self.fieldDataOffset = 0
        self.fieldDataCount = 0
        self.fieldIndicesOffset = 0
        self.fieldIndicesCount = 0
        self.listIndicesOffset = 0
        self.listIndicesCount = 0

    def clearFlats(self) :
        self.structs = []
        self.fields = []
        self.labels = []
        self.fieldIndices = []
        self.lists = {}
        self.currentListIndexCount = 0

    def headerFromFile(self,f,offset=-1):
        if offset >= 0:
            f.seek(offset)
        NeverFile.headerFromFile(self,f)
        self.structOffset = self.dataHandler.readUIntFile(f)
        self.structCount = self.dataHandler.readUIntFile(f)
        self.fieldOffset = self.dataHandler.readUIntFile(f)
        self.fieldCount = self.dataHandler.readUIntFile(f)        
        self.labelOffset = self.dataHandler.readUIntFile(f)
        self.labelCount = self.dataHandler.readUIntFile(f)
        self.fieldDataOffset = self.dataHandler.readUIntFile(f)
        self.fieldDataCount = self.dataHandler.readUIntFile(f)
        self.fieldIndicesOffset = self.dataHandler.readUIntFile(f)
        self.fieldIndicesCount = self.dataHandler.readUIntFile(f)/4
        self.listIndicesOffset = self.dataHandler.readUIntFile(f)
        self.listIndicesCount = self.dataHandler.readUIntFile(f)/4

    def headerToFile(self,f,offset=-1):
        if offset >= 0:
            f.seek(offset)
        f.write(self.type)
        f.write(self.version)
        self.dataHandler.writeUIntFile(self.structOffset,f)
        self.dataHandler.writeUIntFile(self.structCount,f)
        self.dataHandler.writeUIntFile(self.fieldOffset,f)
        self.dataHandler.writeUIntFile(self.fieldCount,f)        
        self.dataHandler.writeUIntFile(self.labelOffset,f)
        self.dataHandler.writeUIntFile(self.labelCount,f)
        self.dataHandler.writeUIntFile(self.fieldDataOffset,f)
        self.dataHandler.writeUIntFile(self.fieldDataCount,f)
        self.dataHandler.writeUIntFile(self.fieldIndicesOffset,f)
        self.dataHandler.writeUIntFile(self.fieldIndicesCount*4,f)
        self.dataHandler.writeUIntFile(self.listIndicesOffset,f)
        self.dataHandler.writeUIntFile(self.listIndicesCount*4,f)

    def recalculateParams(self):
        self.structOffset = 56
        offset = self.structOffset
        self.structCount = len(self.structs)
        offset += self.structCount * 12
        self.fieldOffset = offset
        self.fieldCount = len(self.fields)
        offset += self.fieldCount * 12
        self.labelOffset = offset
        self.labelCount = len(self.labels)
        offset += self.labelCount * 16
        self.fieldDataOffset = offset
        offset += len(self.fieldData)
        self.fieldDataCount = len(self.fieldData)
        self.fieldIndicesOffset = offset
        self.fieldIndicesCount = len(self.fieldIndices)
        offset += len(self.fieldIndices) * 4
        self.listIndicesOffset = offset        
        self.listIndicesCount = 0
        for l in self.lists:
            self.listIndicesCount += 1 + len(self.lists[l])
        
    def structsFromFile(self,f):
        f.seek(self.offset + self.structOffset)
        for i in range(self.structCount):
            type = self.dataHandler.readUIntFile(f)
            dataOrOffset = self.dataHandler.readUIntFile(f)
            fieldCount = self.dataHandler.readUIntFile(f)
            self.structs.append([type,dataOrOffset,fieldCount])

    def structsToFile(self,f):
        f.seek(self.offset + self.structOffset)
        for s in self.structs:
            self.dataHandler.writeUIntFile(s[0],f)
            self.dataHandler.writeUIntFile(s[1],f)
            self.dataHandler.writeUIntFile(s[2],f)
    
    def fieldsFromFile(self,f):
        f.seek(self.offset + self.fieldOffset)
        for i in range(self.fieldCount):
            type = self.dataHandler.readUIntFile(f)
            labelIndex = self.dataHandler.readUIntFile(f)
            dataOrOffset = f.read(4) #leave uninterpreted for now
            self.fields.append([type,labelIndex,dataOrOffset])

    def fieldsToFile(self,f):
        f.seek(self.offset + self.fieldOffset)
        for field in self.fields:
            #print 'fieldToFile: ',FIELDTYPES[field[0]],field[1],field[2]
            self.dataHandler.writeUIntFile(field[0],f)
            self.dataHandler.writeUIntFile(field[1],f)
            f.write(field[2]) # must be uninterpreted, 4 bytes long
    
    def labelsFromFile(self,f):
        f.seek(self.offset + self.labelOffset)
        for i in range(self.labelCount):
            self.labels.append(f.read(16).strip('\0'))

    def labelsToFile(self,f):
        f.seek(self.offset + self.labelOffset)
        for l in self.labels:
            self.dataHandler.writeSizedStringFile(l,16,f)

    def fieldDataToFile(self,f):
        f.seek(self.offset + self.fieldDataOffset)
        f.write(self.fieldData)
        
    def fieldIndicesFromFile(self,f):
        f.seek(self.offset + self.fieldIndicesOffset)
        for i in range(self.fieldIndicesCount):
            self.fieldIndices.append(self.dataHandler.readUIntFile(f))

    def fieldIndicesToFile(self,f):
        f.seek(self.offset + self.fieldIndicesOffset)
        for i in self.fieldIndices:
            self.dataHandler.writeUIntFile(i,f)
    
    def listIndicesFromFile(self,f):
        f.seek(self.offset + self.listIndicesOffset)
        readDWORDS = 0
        while readDWORDS < self.listIndicesCount:
            beginIndex = readDWORDS
            size = self.dataHandler.readUIntFile(f)
            readDWORDS += 1
            list = []
            for j in range(size):
                list.append(self.dataHandler.readUIntFile(f))
                readDWORDS += 1
            self.lists[beginIndex] = list

    def listIndicesToFile(self,f):
        f.seek(self.offset + self.listIndicesOffset)
        beginIndices = self.lists.keys()
        beginIndices.sort() #make sure we get them in the right order
        c = 0
        for l in beginIndices:
            if l*4+self.offset+self.listIndicesOffset != f.tell():
                print >>sys.stderr,'hmmm, list index is',l*4+self.offset+self.listIndicesOffset,\
                                                                        'but file is at',f.tell()
                print >>sys.stderr,'error on list',c,l
            c += 1
            self.dataHandler.writeUIntFile(len(self.lists[l]),f)
            for i in self.lists[l]:
                self.dataHandler.writeUIntFile(i,f)
    
    def uninterpretField(self,label,content,t):
        type = FIELDTYPES[t]
        try:
            labelIndex = self.labels.index(label)
        except:
            labelIndex = len(self.labels)
            self.labels.append(label)
        if type == 'BYTE':
            return (t,labelIndex,self.dataHandler.writeByteBuf(content) + '\0\0\0')
        elif type == 'CHAR':
            return (t,labelIndex,self.dataHandler.writeCharBuf(content) + '\0\0\0')
        elif type == 'WORD':
            return (t,labelIndex,self.dataHandler.writeUWordBuf(content) + '\0\0')
        elif type == 'SHORT':
            return (t,labelIndex,self.dataHandler.writeWordBuf(content) + '\0\0')
        elif type == 'DWORD':
            return (t,labelIndex,self.dataHandler.writeUIntBuf(content))
        elif type == 'INT':
            return (t,labelIndex,self.dataHandler.writeIntBuf(content))
        elif type == 'FLOAT':
            return (t,labelIndex,self.dataHandler.writeFloatBuf(content))
        elif type == 'Struct':
            return (t,labelIndex,self.flattenStructure(content))
        elif type == 'List':
            return (t,labelIndex,self.flattenList(content))
        else:
            #complex type other than struct and list
            o = len(self.fieldData)
            if type == 'DWORD64':
                self.fieldData += self.dataHandler.writeUInt64Buf(content)
            elif type == 'INT64':
                self.fieldData += self.dataHandler.writeInt64Buf(content)
            elif type == 'DOUBLE':
                self.fieldData += self.dataHandler.writeDoubleBuf(content)
            elif type == 'VOID':
                self.fieldData += self.dataHandler.writeUIntBuf(len(content))
                self.fieldData += content
            elif type == 'ResRef':
                self.fieldData += self.dataHandler.writeSizedResRefBuf(content)
            elif type == 'CExoString':
                self.fieldData += self.dataHandler.writeCExoStringBuf(content)
            elif type == 'CExoLocString':
                self.fieldData += self.dataHandler.writeCExoLocStringsBuf(content[0],content[1])
            else:
                print >>sys.stderr,'Error: unhandled type',type,label
                return (-1,-1,0)
            return (t,labelIndex,self.dataHandler.writeUIntBuf(o))
        
    def interpretField(self,f,i):
        entry = self.fields[i]
        type = FIELDTYPES[entry[0]]
        label = self.labels[entry[1]]
        #print 'interpreting',entry,type,label
        if type == 'BYTE':
            return (label,self.dataHandler.readUByteBuf(entry[2][0]),entry[0])
        elif type == 'CHAR':
            return (label,self.dataHandler.readCharBuf(entry[2][0]),entry[0])
        elif type == 'WORD':
            return (label,self.dataHandler.readUWordBuf(entry[2][0:2]),entry[0])
        elif type == 'SHORT':
            return (label,self.dataHandler.readWordBuf(entry[2][0:2]),entry[0])
        elif type == 'DWORD':
            return (label,self.dataHandler.readUIntBuf(entry[2]),entry[0])
        elif type == 'INT':
            return (label,self.dataHandler.readIntBuf(entry[2]),entry[0])
        elif type == 'FLOAT':
            return (label,self.dataHandler.readFloatBuf(entry[2]),entry[0])
        elif type == 'Struct':
            return (label,self.makeStructure(f,self.dataHandler.readUIntBuf(entry[2])),entry[0])
        elif type == 'List':
            return (label,self.makeList(f,self.dataHandler.readUIntBuf(entry[2])/4),entry[0])
        else:
            #complex type other than struct and list
            o = self.dataHandler.readUIntBuf(entry[2])
            f.seek(self.offset + self.fieldDataOffset + o)
            if type == 'DWORD64':
                return (label,self.dataHandler.readUInt64File(f),entry[0])
            elif type == 'INT64':
                return (label,self.dataHandler.readInt64File(f),entry[0])
            elif type == 'DOUBLE':
                return (label,self.dataHandler.readDoubleFile(f),entry[0])
            elif type == 'VOID':
                size = self.dataHandler.readUIntFile(f)
                return (label,f.read(size),entry[0])
            elif type == 'ResRef':
                return (label,self.dataHandler.readSizedResRef(f),entry[0])
            elif type == 'CExoString':
                return (label,self.dataHandler.readCExoString(f),entry[0])
            elif type == 'CExoLocString':
                return (label,self.dataHandler.readCExoLocStrings(f),entry[0])
            else:
                print >>sys.stderr,'Error: unhandled type',type,entry[0]
        return ('INVALID',None,None)
    
    def makeList(self,f,i):
        list = []
        for entry in self.lists[i]:
            list.append(self.makeStructure(f,entry))
        return list
    
    def makeStructure(self,f,si):
        struct = GFFStruct()
        entry = self.structs[si]
        struct.type = entry[0]
        if entry[2] == 1: # only one field
            try:
                field = self.interpretField(f,entry[1])
            except:
                logger.exception('exception on making struct field "' +\
                                            self.labels[self.fields[entry[1]]] + '": ' + `f`)
                raise
            struct.addEntry(field[0],(field[1],field[2]))
        else:
            index = entry[1]/4 #offset in bytes
            for i in range(entry[2]):
                try:
                    field = self.interpretField(f,self.fieldIndices[index + i])
                except:
                    logger.exception('exception on making struct field "' +\
                            self.labels[self.fields[self.fieldIndices[index+1]]] + '" ' + `f`)
                    raise
                struct.addEntry(field[0],(field[1],field[2]))
        return struct

    currentListIndexCount = 0

    def flattenList(self,list):
        index = self.currentListIndexCount
        flatList = []
        self.lists[index] = flatList
        self.currentListIndexCount += 1 + len(list)
        for e in list:
            flatList.append(len(self.structs))
            assert isinstance(e,GFFStruct)
            self.flattenStructure(e)
        return self.dataHandler.writeUIntBuf(index * 4)

    def flattenStructure(self,struct):
        numEntries = len(struct.entries)
        structIndex = 0
        if numEntries == 1:
            #first get a struct index, because the root must be at index 0
            structIndex = len(self.structs)
            self.structs.append([struct.type,0,numEntries])
            label = struct.entries.keys()[0]
            entry = struct.entries.values()[0]
            t = type(self.fieldData)
            try:
                flattened = self.uninterpretField(label,entry[0],entry[1])
            except:
                logger.exception('exception on flattening "'
                                 + label + '": ' + `entry[0]` + ' ' + `type(self.fieldData)`)
                raise
            if t != type(self.fieldData):
                logger.warning('warning, type of fielddata changed from ' + `t` + ' to ' +\
                                                `type(self.fieldData)` + ' after ' + `entry`)
            index = len(self.fields)
            self.fields.append(flattened)
            self.structs[structIndex][1] = index
        else:
            #first get a struct index, because the root must be at index 0
            structIndex = len(self.structs)
            self.structs.append([struct.type,0,numEntries])
            #now climb the tree and flatten our childen, collect their entries
            flatEntries = []
            for e in struct.entries:
                entry = struct.entries[e]
                t = type(self.fieldData)
                try:
                    flatEntries.append(self.uninterpretField(e,entry[0],entry[1]))
                except:
                    logger.exception('exception on flattening "' + e
                                     + '": ' + `entry[0]`  + ' ' + `type(self.fieldData)`)
                    raise
                if t != type(self.fieldData):
                    logger.warning('warning, type of fielddata changed from ' + `t` + ' to '\
                                                 + `type(self.fieldData)` + ' after ' + `entry`)
            #the children probably wrote their own struct fields, so adjust our index
            self.structs[structIndex][1] = len(self.fieldIndices) * 4
            #and finally write out our entries in a contiguous chunk
            for e in flatEntries:
                self.fieldIndices.append(len(self.fields))
                self.fields.append(e)
        return self.dataHandler.writeUIntBuf(structIndex)
    
    def flattenRootStructure(self):
        self.clearFlats()
        self.flattenStructure(self.rootStructure)
        
    def fromFile(self,f,o=0):
        self.offset = o
        f.seek(self.offset)
        self.clearFlats()
        self.headerFromFile(f)
        self.structsFromFile(f)
        self.fieldsFromFile(f)
        self.labelsFromFile(f)
        self.fieldIndicesFromFile(f)
        self.listIndicesFromFile(f)
        self.rootStructure = self.makeStructure(f,0)
        self.clearFlats()
        
    def toFile(self,f,o=0):
        self.offset = o
        f.seek(self.offset)
        self.flattenRootStructure()
        self.recalculateParams()
        self.headerToFile(f)
        #logger.debug('writing GFF : Fields and Structs for:')
        #logger.debug(self.type+' file')
        #for i in self.fields:
        #    logger.debug(str(self.fields.index(i))+' '+FIELDTYPES[i[0]]+' '+self.labels[i[1]])
        self.structsToFile(f)
        self.fieldsToFile(f)
        self.labelsToFile(f)
        self.fieldDataToFile(f)
        self.fieldIndicesToFile(f)
        self.listIndicesToFile(f)
        self.fieldData = ''
        self.clearFlats()
        
    def getRoot(self):
        '''retrieve the top level structure from this GFF file as a GFFStruct'''
        return self.rootStructure

    def getEntry(self,name):
        return self.rootStructure.getEntry(name)

    def add(self, label, value, typename):
        """
        Delegate to add an entry to the root GFF structure.
        @param label: the label for the entry
        @param value: the entry's value
        @param typename: the entry's type, chosen from L{FIELDTYPENAMES}
        """
        self.rootStructure.add(label, value,typename)
        
    def __getitem__(self,key):
        return self.getRoot()[key]

    def __setitem__(self,key,value):
        self.getRoot()[key] = value
        
    def __contains__(self,key):
        return key in self.getRoot()
    
    def clone(self):
        gff = GFFFile()
        gff.version = self.version
        gff.type = self.type
        gff.rootStructure = self.getRoot().clone()
        return gff
    
    def __str__(self):
        s = `self.type` + ' ' + `self.version` + '\n'
        s += 'offset: ' + `self.offset` + '\n'
        s += 'structOffset: ' + `self.structOffset` + '\n'
        s += 'structCount: ' + `self.structCount` + '\n'
        s += 'fieldOffset: ' + `self.fieldOffset` + '\n'
        s += 'fieldCount: ' + `self.fieldCount` + '\n'
        s += 'labelOffset: ' + `self.labelOffset` + '\n'
        s += 'labelCount: ' + `self.labelCount` + '\n'
        s += 'fieldDataOffset: ' + `self.fieldDataOffset` + '\n'
        s += 'fieldDataCount: ' + `self.fieldDataCount` + '\n'
        s += 'fieldIndicesOffset: ' + `self.fieldIndicesOffset` + '\n'
        s += 'fieldIndicesCount: ' + `self.fieldIndicesCount` + '\n'
        s += 'listIndicesOffset: ' + `self.listIndicesOffset` + '\n'
        s += 'listIndicesCount: ' + `self.listIndicesCount` + '\n'

        s += 'structs: ' + `self.structs`[:150] + '\n'
        s += 'fields: ' + `self.fields`[:150] + '\n'
        s += 'labels: ' + `self.labels`[:150] + '\n'
        s += 'fieldIndices: ' + `self.fieldIndices`[:150] + '\n'
        s += 'lists: ' + `self.lists`[:150] + '\n'
        s += '------ root structure starts here ------\n'
        s += self.getRoot().__str__()
        import pprint
        s += pprint.pformat(self.getRoot().entries)
        return s
    

        
if __name__ == "__main__":
    if(len(sys.argv) >= 2):
        f = GFFFile()
        print >>sys.stderr,'reading',sys.argv[1]
        f.fromFile(open(sys.argv[1],'rb'),0)
        if len(sys.argv) >= 3:
            print >>sys.stderr,'writing',sys.argv[2]
            f.toFile(open(sys.argv[2],'wb'))            
            print >>open('out.txt','w'),f
            f = f.clone()
            #f.flattenRootStructure()
            f.toFile(open(sys.argv[2] + '2','wb'))
            print >>open('out2.txt','w'),f
        else:
            print f
        #pprint.PrettyPrinter().pprint(f.localizedStrings)
        #pprint.PrettyPrinter().pprint(f.entriesByNameAndType)
        #f.toFile(open(sys.argv[1] + '.copy','w'),0)        
        #f.fromFile(open(sys.argv[1] + '.copy'),0)
        #print f
        #print f.getRoot()
        #pprint.PrettyPrinter().pprint(f.localizedStrings)
        #pprint.PrettyPrinter().pprint(f.entriesByNameAndType)
    else:
        print 'usage:',sys.argv[0],'<filename>'
