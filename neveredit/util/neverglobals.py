'''shared global instances that need to be accessed via same module path.'''

import logging

resourceManager = None

def setResourceManager(rm):
    global resourceManager
    resourceManager = rm

def getResourceManager():
    global resourceManager
    if not resourceManager:
        import neveredit.util.Preferences
        p = neveredit.util.Preferences.getPreferences()
        if p['NWNAppDir']:
            from neveredit.game import ResourceManager
            try:
                resourceManager = ResourceManager.ResourceManager()
                resourceManager.scanGameDir(p['NWNAppDir'])
            except:
                resourceManager = None
            return resourceManager
        else:
            logging.getLogger().critical("No NWN App Dir specifid in prefs.")
            raise RuntimeError,"No App Dir"
    else:
        return resourceManager


