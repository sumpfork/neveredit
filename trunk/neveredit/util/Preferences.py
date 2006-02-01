"""The neveredit preferences system."""
import logging
logger = logging.getLogger("neveredit")

import os,os.path,sys
import encodings, codecs

from neveredit.util import Utils
from neveredit.util import plistlib

globalPrefs = None

def getPreferences():
    """Get the gloal prefs object. Load it if non-existent.
    @return: the global preferences object.
    """
    global globalPrefs
    if not globalPrefs:
        globalPrefs = Preferences()
        globalPrefs.load()
    return globalPrefs

class Preferences:
    """A class to load and store user level cross-platform
    preferences for neveredit."""
    def __init__(self):
        if 'HOME' in os.environ:
            self.prefPath = os.environ['HOME']
        else:
            self.prefPath = os.path.dirname(sys.argv[0])
            
        if Utils.iAmOnMac():
            self.prefPath = os.path.join(self.prefPath,
                                         'Library','Preferences',
                                         'org.openknights.neveredit.plist')
        elif sys.platform.find('linux') >= 0:
            self.prefPath = os.path.join(self.prefPath,'.neveredit')
        else:
            self.prefPath = os.path.join(self.prefPath,'neveredit.prefs')

        # Updated to include preferences for control of the model
        # window.
        self.values = {'NWNAppDir':None,
                       'ScriptAntiAlias':False,
                       'ScriptAutoCompile':True,
                       "DefaultLocStringLang":0,        # english=0
                       'FileHistory':[],
                       'GLW_UP':'w',
                       'GLW_DOWN': 's',
                       'GLW_RIGHT': 'e',
                       'GLW_LEFT': 'q'}


    def __getitem__(self,key):
        return self.values[key]

    def __setitem__(self,key,value):
        self.values[key] = value
        
    def load(self):
        '''Load preferences from their standard location.'''
        #defaults
        if not self.values['NWNAppDir']:
            if sys.platform == 'darwin':
                self['NWNAppDir'] = '/Applications/Neverwinter Nights/'
            elif sys.platform.find('linux') >= 0:
                self['NWNAppDir'] = '/usr/local/games/nwn/'
            else:
                self['NWNAppDir'] = '/Program Files/NWN/'                

        codecs.register(encodings.search_function)
        if os.path.exists(self.prefPath):
            try:
                pl = plistlib.Plist.fromFile(self.prefPath)
                for key in self.values:
                    if key in pl:
                        self.values[key] = getattr(pl,key)
            except:
                #could be out of date or malformed
                logger.exception("while reading preferences file")
                
                
    def save(self):
        '''Save the current preferences settings.'''        
        codecs.register(encodings.search_function)
        pl = plistlib.Plist()
        pl.update(self.values)
        pl.write(self.prefPath)

    def update(self,valueDict):
        self.values.update(valueDict)
        

