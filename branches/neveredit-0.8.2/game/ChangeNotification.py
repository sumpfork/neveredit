"""Classes to deal with change notification."""

from sets import Set

class VisualChangeListener:
    def visualChanged(self,visual):
        raise NotImplementedError("visualChanged in VisualChangeListener")

class VisualChangeNotifier:
    def __init__(self):
        self.visualChangeListeners = Set()

    def addVisualChangeListener(self,l):
        self.visualChangeListeners.add(l)

    def removeVisualChangeListener(self,l):
        self.visualChangeListeners.discard(l)
        
    def visualChanged(self,v):
        '''Call this to notify visual change listeners of a change in
        visual v.
        @param v: the changed visual, usually implementing
                  L{neveredit.game.NeverData.LocatedNeverData}.
        '''
        for l in self.visualChangeListeners:
            l.visualChanged(v)
    

class ResourceListChangeListener:
    def resourceListChanged(self):
        raise NotImplementedError("resourceListChanged in "
                                  "ResourceListChangeListener")

class ResourceListChangeNotifier:
    def __init__(self):
        self.resourceListChangeListeners = Set()

    def addResourceListChangeListener(self,l):
        self.resourceListChangeListeners.add(l)

    def removeResourceListChangeListener(self,l):
        self.resourceListChangeListeners.discard(l)

    def moduleResourceListChanged(self):
        if not self.module:
            logger.warning("can't register resource list change without"
                           " registered module")
            return
        self.addModule(self.module)
        for l in self.resourceListChangeListeners:
            l.resourceListChanged()

class PropertyChangeListener:
    def propertyChanged(self):
        raise NotImplementedError("propertyChanged in "
                                  "PropertyChangeListener")

class PropertyChangeNotifier:
    def __init__(self):
        self.propertyChangeListeners = Set()

    def addPropertyChangeListener(self,l):
        self.propertyChangeListeners.add(l)

    def removePropertyChangeListener(self,l):
        self.propertyChangeListeners.discard(l)
        
    def propertyChanged(self,propControl,prop):
        '''Call this to notify property change listeners of a change in
        property p.
        @param propControl: the changed control, implementing
                  L{neveredit.ui.PropWindow.PropControl}.
        @param prop: the corresponding prop
        '''
        for l in self.propertyChangeListeners:
            l.propertyChanged(propControl,prop)
