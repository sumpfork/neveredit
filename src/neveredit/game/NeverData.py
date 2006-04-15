'''This module contains parent classes for many game element instances.'''

from neveredit.util import neverglobals

class NeverProperty:
    '''This class represents a property of a NeverData object, consisting
    of a name/value pair and a specification list indicating how this property
    is to be displayed, changed and used.
    '''
    def __init__(self,label,value,spec):
        self.label = label
        self.value = value
        self.spec = spec.split(',')

    def getName(self):
        return self.label

    def getValue(self):
        return self.value

    def setValue(self,v):
        self.value = v
        
    def getSpec(self):
        return self.spec
    
class NeverData:
    '''This class is the superclass to a hierarchy of game classes
    that all have properties stored in one or more gff files. Each
    subclass only has to add property list dictionaries and gff
    structs to their superclass, which handles access to the
    properties by name as well as iterating through them.

    NeverData.propListDict is a dict of PropLists indexed by strings. A PropList
    is a dict of {label: type,...}, made mainly to indicate to the UI how to display
    the data (which control to use).
    NeverData.gffstructDict is a dict of GFFStructs indexed by strings.
    To each of the strings, the NeverData associates one proplist and one gff struct. The
    GFF Struct is interpreted with *this* PropList.

    For a given label, a PropList/GFFStruct couple may (or may not) return a NeverProperty.
    When asked to search for one, the NeverData will iterate over its couples.
    One can also add a property (but must tell in which PropList/GFFStruct)

    NeverData.IterItem() allows to iterate over NeverData.propListDict, returning the next
    NeverProperty each time.
    '''

    globalID = 0
    
    def __init__(self):
        if not hasattr(self,'propListDict'): #this is so we can have multiple inheritance
            self.propListDict = {}
            self.gffstructDict = {}
            self.nevereditID = NeverData.globalID
            NeverData.globalID += 1

    def __getitem__ (self, key):
        """Returns the value of a property.
        @param key: the name of the property
        @return the property's value (plain value, I{not} an instance of NeverProperty)
        """
        try:
            sp = self.getProperty (key)
            return sp.getValue()
        except KeyError:
            return None
        
    def __setitem__ (self, key, value):
        return self.setProperty (key, value)

    def __iter__ (self):
        return self.iterateProperties()

#    def __delitem__
#    def __len__
#    def __contains__

    def getNevereditId(self):
        return self.nevereditID

    def getDescription(self):
        """Gives a more detailed description.
        @return: a string with a more detailed description including the 'Description' field and
        the object's 'Tag'"""
        return 'Name: ' + self.getName() + '\nDescription: "' + self['Description'].getString()\
               + '"\n' + 'Tag: ' + self['Tag']
    
    def addPropList(self,name,plist,gffstruct):
        '''Add a property list dictionary and a gff struct under
        the given name.'''
        if name in self.gffstructDict:
            print 'warning, gff struct dict with name',name,'already exists'
            print self,self.propListDict[name]
            return
        self.propListDict[name] = plist
        self.gffstructDict[name] = gffstruct

    def getMainGFFStruct(self):
        """Get the L{neveredit.file.GFFFile.GFFStruct} with name 'main'"""
        return self.getGFFStruct('main')
    
    def getGFFStruct(self,name):
        """Get the L{neveredit.file.GFFFile.GFFStruct} with the given name.
        @param name: the name of the gff struct to return.
        """
        return self.gffstructDict.get(name,None)

    def removePropList(self,name):
        '''Remove a property list dictionary by name'''
        if name in self.propListDict:
            del self.propListDict[name]
            del self.gffstructDict[name]
            
    def getProperty(self,label):
        """Get a property of this game object.
        @param label: the name of the property to return.
        @return: the property (an instance of L{NeverProperty}
        """
        for name,plist in self.propListDict.iteritems():
            if label in plist:
                return NeverProperty(label,
                                     self.gffstructDict[name].getInterpretedEntry(label),
                                     plist[label])
        else:
            #try the first one
            return NeverProperty(label,
                                 self.gffstructDict.values()[0].getInterpretedEntry(label),
                                 self.propListDict.values()[0].get(label,label))

    def setProperty(self,label,value):
        for name,plist in self.propListDict.iteritems():
            if label in plist:
                self.getGFFStruct(name).setInterpretedEntry(label,value)
                break
        else:
            #try the first one
            self.gffstructDict.values()[0].setInterpretedEntry(label,value)
            
    def iterateProperties(self):
        for name,plist in self.propListDict.iteritems():
            plkeys = plist.keys()
            plkeys.sort()
            for label in plkeys:
                yield NeverProperty(label,
                                    self.getGFFStruct(name).getInterpretedEntry(label),
                                    plist[label])

    def hasProperty(self,label):
        for plist in self.propListDict.values():
            if label in plist:
                return True
        return False
    
    def getPropertyValue(self,label):
        return self.getProperty(label).getValue()
    
    def getName(self):
        """Return the name of this game object as a string."""
        return 'NeverData'
    
    def __str__(self):
        if not len(self.gffstructDict):
            return '<empty neverdata object>'
        else:
            return '<' + self.__class__.__name__ + ': ' + self.getName() + '>'

    def __repr__(self):
        return self.__str__()

class LocatedNeverData(NeverData):
    '''This specialized subclass contains functionality unique to located game objects, i.e. object
    that are position within an area.'''
    def __init__(self):
        NeverData.__init__(self)
        self.model = None
        self.modelName = None
        
    def getPortrait(self,size):
        """Get this object's portrait (usually a PIL Image object).
        @param size: this size of the portrait to return, see BW documentation for possible
                     single character values."""
        portraitIndex = self.getPropertyValue('PortraitId')
        return neverglobals.getResourceManager()\
               .getPortraitByIndex(portraitIndex,size)

    def getModel(self,copy=False):
        """Get the L{neveredit.file.MDLFile.Model} for this object.
        @param copy: if True, return a copy of the model that is _not_ stored in the parent
                     class
        """
        raise NotImplementedError('should not call getModel on base class' + `self`)

    def forceModelReload(self):
        """
        Force this object to reload its L{neveredit.file.MDLFile.Model} when next
        accessed. Usually called when the model has changed in some way.
        """
        self.model = None

class NeverInstance(LocatedNeverData):
    """
    The parent class of instanced objects, which are objects that have actually been
    placed into an area and thus have an x,y,z location, orientation and id.
    """
    def getBearing(self):
        """Return the placed tile's orientation in degrees.
        @return: tile orientation in degrees clockwise from North"""
        raise NotImplementedError('should not call getBearing on base class: ' + `self`)

    
