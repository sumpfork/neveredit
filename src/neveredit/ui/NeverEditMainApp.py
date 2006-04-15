"""Main neveredit application class."""

from neveredit.util import Loggers
import logging
logger = logging.getLogger("neveredit")
from neveredit.util import check_versions

import sys
if sys.version_info[0] < 2 or (sys.version_info[0] == 2 and sys.version_info[1] < 3):
    print >>sys.stderr,"Sorry, neveredit needs python >= 2.3. Download from python.org"
    sys.exit()

import tempfile

try:
    import wx
    import wx.html
    import wx.stc
except:
    print >>sys.stderr,"Sorry,You don't seem to have a proper installation of wxPython."
    print >>sys.stderr,"Get one from wxpython.org."
    import traceback
    traceback.print_exc()
    sys.exit()

from neveredit.game import Module
from neveredit.game import Area
from neveredit.game import ResourceManager
from neveredit.game.ChangeNotification import PropertyChangeListener
from neveredit.game.Placeable import Placeable
from neveredit.game.Script import Script
from neveredit.game.Conversation import Conversation
from neveredit.game.Factions import Factions,FactionStruct
from neveredit.ui import MapWindow
from neveredit.ui import ConversationWindow
from neveredit.ui import ModelWindow
from neveredit.ui import ScriptEditor
from neveredit.ui import PropWindow
from neveredit.ui import HelpViewer
from neveredit.ui import ToolPalette
from neveredit.ui import PreferencesDialog
from neveredit.ui import Notebook
from neveredit.ui import SoundControl
from neveredit.ui.FactionGridWindow import FactionGridWindow,FactionGrid
from neveredit.util import Preferences
from neveredit.util import Utils
from neveredit.util import neverglobals

#images
from neveredit.resources.images import neveredit_logo_jpg
from neveredit.resources.images import neveredit_logo_init_jpg
import neveredit.resources

from pkg_resources import resource_filename,resource_listdir
logo_fname = resource_filename('neveredit.resources',
                               'neveredit.jpg')

import os
import threading
from sets import Set
import gettext

gettext.install('neveredit','translations')

description =     '''<html><body>

    <table width="100%%" border=0>
    <tr>
    <td valign="top">
    <h2>neveredit</h2>
    </td><td align="right" valign="top">
    <img src="%s"></td></tr></table>

    <p>Welcome to neveredit. Neveredit strives to be an editor for files
    from the Bioware game Neverwinter Nights. One day it may have all of
    the functionality of the Bioware windows tools, and maybe more. For
    now, I am striving to achieve basic editing functionality on
    non-Windows platforms. This means that this is alpha quality
    software, and will at the current stage likely do bad things
    to your files. I am happy to receive bug reports, but take no
    responsibility for any damages incurred through the use of this
    software.</p>

    <p>I write neveredit in my spare time, but I try to respond to
    all reports and questions I get about it. Before you write, please
    see if what you want to know is covered at the neveredit homepage,
    <i> http://neveredit.sourceforge.net </i>. The page is a wiki, so feel
    free to add documentation there as you see fit. The wiki also
    has instructions for developers as to how to check out the source
    and contribute.

    <ul>
    <li>Thanks to Torlack for his script compiler and file format documentation.</li>
    <li>Thanks to Damon Law (damonDesign.com) for the neveredit image.</li>
    <li>Thanks to Mickael Leduque for a number of significant feature implementations (factions, sounds...)</li>
    <li>Thanks to Alan Schmitt for the beginnings of a conversation editor.</li>
    <li>Thanks to Sylvan_Elf for the neveredit splash screen.</li>
    <li>Thanks to the NWN Lexicon folks for letting me include the lexicon.</li>
    </ul>
    <p>Have fun,<br><i>sumpfork</i></p>

    </body></html>''' % logo_fname

class MySplashScreen(wx.SplashScreen):
    def __init__(self,pic):
        wx.SplashScreen.__init__(self, pic,
                                 wx.SPLASH_CENTRE_ON_SCREEN|
                                 wx.SPLASH_NO_TIMEOUT,
                                 4000, None, -1,
                                 style = wx.SIMPLE_BORDER
                                 |wx.FRAME_NO_TASKBAR
                                 |wx.STAY_ON_TOP)

##\mainpage
class NeverEditMainWindow(wx.Frame,PropertyChangeListener):
    __doc__ = description
    def __init__(self,parent,id,title):
        '''Constructor. Sets up static controls and menus.'''
        wx.InitAllImageHandlers()
        self.splash = MySplashScreen(neveredit_logo_jpg.getBitmap())
        wx.EVT_CLOSE(self.splash,self.OnCloseSplash)
        
        self.splash.Show(True)

        wx.Frame.__init__(self,parent,-1,title,size=(800,600))

        self.doInit = False
        self.fname = None
        self.doRead = False
        self.fileChanged = False

        self.map = None
        self.model = None
        self.helpviewer = None
        
        self.idToTreeItemMap = {}
        self.detachedMap = {}

        self.threadAlive = False
    
        self.selectThisItem = None
        
        #status bar
        self.CreateStatusBar(2)
        self.SetStatusWidths([-1,150])
        self.SetStatusText(_("Welcome to neveredit..."))
        self.statusProgress = wx.Gauge(self.GetStatusBar(),-1,100)
        self.setProgress(0)
                
        splitter = wx.SplitterWindow(self,-1,style=wx.NO_3D|wx.SP_3D)
        
        tID = wx.NewId()
        self.tree = wx.TreeCtrl(splitter,tID,wx.DefaultPosition,\
                               wx.DefaultSize,\
                               wx.TR_HAS_BUTTONS)
        self.selectedTreeItem = None
        self.lastAreaItem = None
        
        wx.EVT_TREE_SEL_CHANGED(self,tID,self.treeSelChanged)
        wx.EVT_TREE_ITEM_EXPANDING(self,tID,self.treeItemExpanding)
        wx.EVT_TREE_ITEM_COLLAPSED(self,tID,self.treeItemCollapsed)

        self.notebook = Notebook.Notebook(splitter)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnNotebookPageChanged,
                  self.notebook)
        
        self.SetSizeHints(minW=600,minH=200)
        
        splitter.SplitVertically(self.tree,self.notebook,180)
        splitter.SetMinimumPaneSize(100)

        self.welcome = wx.html.HtmlWindow(self.notebook,-1,(400,400))
        self.notebook.AddPage(self.welcome,_("Welcome to neveredit"),'welcome')
        try:
            self.welcome.SetPage(self.__doc__)
        except:
            pass #html window likes to throw exceptions

        helps = [resource_filename('neveredit.resources.help',file)
                 for file in resource_listdir('neveredit.resources','help')
                 if (file[-4:] == '.zip')]
        self.helpviewer = HelpViewer.makeHelpViewer(helps,tempfile.gettempdir())

        self.toolPalette = None
        self.props = None
        
        self.setupMenus()
        
        self.scriptEditorFrame = wx.Frame(self,-1,"Script Editor",(100,100))
        self.scriptEditor = ScriptEditor.ScriptEditor(self.scriptEditorFrame,-1)
        self.scriptEditorFrame.SetSize((700,500))
        self.scriptEditor.setHelpViewer(self.helpviewer)
        ScriptEditor.EVT_SCRIPTADD(self.scriptEditor,self.OnScriptAdded)

        self.showScriptEditorFix = False

        wx.EVT_CLOSE(self.scriptEditorFrame,self.OnCloseWindow)

        self.readingERF = False
        self.RMThread = None

        self.prefs = None
        self.loadPrefs()

        self.ID_TIMER = 200
        self.timer = wx.Timer(self,self.ID_TIMER)
        wx.EVT_TIMER(self,self.ID_TIMER,self.kick)
        self.timer.Start(200)
        wx.EVT_IDLE(self,self.idle)
        wx.EVT_CLOSE(self,self.OnClose)
        wx.EVT_SIZE(self,self.OnSize)

        tmp = self.splash
        self.splash = MySplashScreen(neveredit_logo_init_jpg.getBitmap())
        self.splash.Show(True)
        if tmp:
            tmp.Show(False)
            tmp.Destroy()

    def initResourceManager(self):
        '''Initialize the resource manager object from the app dir path.
        Fails with a dialog warning if path does not exit. If it does
        exist, disables interface and starts the initialization thread.'''
        if not os.path.exists(self.prefs['NWNAppDir']):
            if self.splash:
                self.splash.Show(False)
                self.splash.Destroy()
            dlg = wx.MessageDialog(self,_('Directory does not exist: ')
                                  + self.prefs['NWNAppDir'] +
                                  '\n' + _('Please reset in Preferences'),
                                  _('Non-existent App Dir'),wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.Show(True)
        else:
            self.Enable(False)
            self.SetStatusText(_("Initializing from NWN Application Directory..."))
            self.RMThread = threading.Thread(target=self.doInitResourceManager)
            self.threadAlive = True
            self.RMThread.start()

    def doInitResourceManager(self):
        '''This is the thread body for initializing the resource manager.Do
        not call any function that
        changes the interface from this method. You need to set a flag and call
        it from the main app thread, as otherwise things will get screwed up on
        linux.'''
        self.resourceManager = ResourceManager.ResourceManager()
        neverglobals.setResourceManager(self.resourceManager)
        self.resourceManager.setProgressDisplay(self)
        self.resourceManager.scanGameDir(self.prefs['NWNAppDir'])
        Script.init_nwscript_keywords()
        
    def setProgress(self,prog):
        '''Implementing the progress display interface'''
        self.progress = prog
        if not self.threadAlive and self.progress:
            self.statusProgress.Show(True)
            self.statusProgress.SetValue(int(self.progress))
            wx.YieldIfNeeded()

    def setStatus(self,s):
        '''Implementing the progress display interface'''
        self.SetStatusText(s)
        wx.YieldIfNeeded()
        
    def showScriptEditor(self):
        self.scriptEditorFrame.Show(True)
        self.scriptEditorFrame.Raise()

    def showToolPalette(self):
        if not self.toolPalette:
            self.toolPalette = ToolPalette.ToolFrame()
            self.toolPalette.GetToolBar().Enable(False)
            self.Bind(wx.EVT_CLOSE,self.OnCloseToolPalette,self.toolPalette)
            if self.map:
                ToolPalette.EVT_TOOLSELECTION(self.toolPalette,
                                              self.map.toolSelected)
        self.toolPalette.Show(True)

    def setupMenus(self):
        '''set up the app menu bar'''
        self.ID_ABOUT = wx.NewId()
        self.ID_OPEN  = wx.NewId()
        self.ID_SAVE  = wx.NewId()
        self.ID_SAVEAS = wx.NewId()
        self.ID_EXIT  = wx.NewId()
        self.ID_HELP = wx.NewId()
        self.ID_PREFS = wx.NewId()
        self.ID_ADD_ERF = wx.NewId()
        self.ID_ADD_RESOURCE = wx.NewId()
        self.ID_DETACH = wx.NewId()
        self.ID_PALETTE_WINDOW_MITEM = wx.NewId()
        self.ID_SCRIPT_WINDOW_MITEM = wx.NewId()
        self.ID_MAIN_WINDOW_MITEM = wx.NewId()
        self.ID_CUT = wx.NewId()
        self.ID_COPY = wx.NewId()
        self.ID_PASTE = wx.NewId()
        self.ID_DEL = wx.NewId()

        if Utils.iAmOnMac():
            wx.App_SetMacExitMenuItemId(self.ID_EXIT)
            wx.App_SetMacPreferencesMenuItemId(self.ID_PREFS)
            wx.App_SetMacAboutMenuItemId(self.ID_ABOUT)

        #menus
        self.filemenu = wx.Menu()
        self.filemenu.Append(self.ID_OPEN, '&' + _('Open') + '\tCtrl+O',
                             _("Open a File"))
        self.filemenu.Append(self.ID_ADD_ERF, _('Add in ERF File...'),
                             _("Add all entries of another ERF file"))
        self.filemenu.Append(self.ID_ADD_RESOURCE, _('Add in resource file...'),
                             _("Add an NWN resource into module"))
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_SAVE, '&' + _('Save') + '\tCtrl+S',
                             _("Save File"))
        self.filemenu.Append(self.ID_SAVEAS, '&' + _('Save As...') +
                             '\tShift+Ctrl+S',
                             _("Save File under a new name"))
        if not Utils.iAmOnMac():
            self.filemenu.Append(self.ID_EXIT,_('E&xit') + '\tAlt-X',
                                 _("Quit neveredit"))
        self.filemenu.Enable(self.ID_SAVE,False)
        self.filemenu.Enable(self.ID_SAVEAS,False)
        self.filemenu.Enable(self.ID_ADD_ERF,False)
        self.filemenu.Enable(self.ID_ADD_RESOURCE,False)

        self.filehistory = wx.FileHistory()
        self.filehistory.UseMenu(self.filemenu)
        wx.EVT_MENU_RANGE(self,wx.ID_FILE1,wx.ID_FILE9,self.OnFileHistory)

        self.editmenu = wx.Menu()
        self.editmenu.Append(self.ID_CUT, '&'+_('Cut'), _('cut'))
        self.editmenu.Append(self.ID_COPY, '&'+_('Copy'), _('copy'))
        self.editmenu.Append(self.ID_PASTE, '&'+_('Paste'), _('paste'))
        self.sep1=self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_DEL, '&'+_('Delete'), _('del'))
        self.sep2=self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_PREFS,'&' + _('Preferences...'),
                             _('neveredit preferences dialog'))
        
        wx.EVT_MENU(self,self.ID_DEL,self.OnDelete)
        wx.EVT_MENU(self,self.ID_CUT,self.OnCut)
        wx.EVT_MENU(self,self.ID_COPY,self.OnCopy)
        wx.EVT_MENU(self,self.ID_PASTE,self.OnPaste)
        self.editmenu.Bind(wx.EVT_MENU_OPEN, self.OnEditMenu)

        if not Utils.iAmOnMac(): # mac bundle now seems to produce own window menu
            self.windowmenu = wx.Menu()
            self.windowmenu.Append(self.ID_MAIN_WINDOW_MITEM, _('Main Window'))
            self.windowmenu.Append(self.ID_PALETTE_WINDOW_MITEM, _('Palette Window'))
            self.windowmenu.Append(self.ID_SCRIPT_WINDOW_MITEM, _('Script Editor'))
        
        helpmenu = wx.Menu()
        helpmenu.Append(self.ID_ABOUT, '&' + _('About...'), _("About neveredit"))
        helpmenu.Append(self.ID_HELP,'&'+ _('neveredit Help'), _("neveredit Help"))
        
        menuBar = wx.MenuBar()
        menuBar.Append(self.filemenu,"&" + _("File"))
        menuBar.Append(self.editmenu, "&" + _("Edit"))
        if not Utils.iAmOnMac():
            menuBar.Append(self.windowmenu, "&" + _("Window"))
        menuBar.Append(helpmenu, "&" + _("Help"))
        self.SetMenuBar(menuBar)

        wx.EVT_MENU(self,self.ID_OPEN,self.openFile)
        wx.EVT_MENU(self,self.ID_ADD_ERF,self.addERFFile)
        wx.EVT_MENU(self,self.ID_ADD_RESOURCE,self.addResourceFile)
        wx.EVT_MENU(self,self.ID_SAVE,self.saveFile)
        wx.EVT_MENU(self,self.ID_SAVEAS,self.saveFileAs)
        wx.EVT_MENU(self,self.ID_ABOUT,self.about)
        wx.EVT_MENU(self,self.ID_PREFS,self.OnPreferences)
        wx.EVT_MENU(self,self.ID_EXIT,self.exit)
        wx.EVT_MENU(self,self.ID_HELP,self.help)
        if not Utils.iAmOnMac():
            wx.EVT_MENU(self,self.ID_MAIN_WINDOW_MITEM, self.windowMenu)
            wx.EVT_MENU(self,self.ID_SCRIPT_WINDOW_MITEM, self.windowMenu)
            wx.EVT_MENU(self,self.ID_PALETTE_WINDOW_MITEM, self.windowMenu)
        
        #wx.EVT_MENU(self,self.ID_DETACH,self.OnDetach)

    def OnPaste(self,event):
        '''Perform a paste operation'''
        inFocus = wx.Window.FindFocus()
        if not inFocus:            
            return
        if inFocus == self.scriptEditor.getCurrentEditor():
            self.scriptEditor.OnPaste(event)        
        if not wx.TheClipboard.Open():
            logger.error("Can't open system clipboard")
            return
        data = wx.TextDataObject()
        hasData = wx.TheClipboard.GetData(data)

        if hasData and data.GetText() and hasattr(inFocus,'Replace'):
            inFocus.Replace(inFocus.GetSelection()[0],inFocus.GetSelection()[1],data.GetText())
        wx.TheClipboard.Close()

    def OnCopy(self,event):
        '''Perform a copy operation'''
        selection,inFocus = self.getCurrentTextSelection()
        if inFocus == self.scriptEditor.getCurrentEditor():
            self.scriptEditor.OnCopy(event)
        if selection:
            if not wx.TheClipboard.Open():
                logger.error("Can't open system clipboard")
                return
            data = wx.TextDataObject(selection)
            wx.TheClipboard.AddData(data)
            wx.TheClipboard.Close()        

    def OnDelete(self,event):
        '''Perform a delete operation'''
        selection,inFocus = self.getCurrentTextSelection()
        if inFocus == self.scriptEditor.getCurrentEditor():
            self.scriptEditor.OnDelete(event)
        if selection and hasattr(inFocus,'Remove'):
            inFocus.Remove(inFocus.GetSelection()[0],inFocus.GetSelection()[1])

    def OnCut(self,event):
        '''Peform a cut operation'''
        selection,inFocus = self.getCurrentTextSelection()
        if inFocus == self.scriptEditor.getCurrentEditor():
            self.scriptEditor.OnCut(event)
        if selection:
            if not wx.TheClipboard.Open():
                logger.error("Can't open system clipboard")
                return
            data = wx.TextDataObject(selection)
            wx.TheClipboard.AddData(data)
            wx.TheClipboard.Close()
            if hasattr(inFocus,'Remove'):
                inFocus.Remove(inFocus.GetSelection()[0],inFocus.GetSelection()[1])
            
    def getCurrentTextSelection(self):
        inFocus = wx.Window.FindFocus()
        if not inFocus:
            return None,None
        selection = None
        if hasattr(inFocus,'GetStringSelection'):
            selection = inFocus.GetStringSelection()
        return selection,inFocus
    
    def OnEditMenu(self,event):
        self.editmenu.Enable(self.ID_CUT,False)
        self.editmenu.Enable(self.ID_COPY,False)
        self.editmenu.Enable(self.ID_PASTE,False)
        self.editmenu.Enable(self.ID_DEL,False)

        selection,inFocus = self.getCurrentTextSelection()
        if not inFocus:
            return
        if inFocus == self.scriptEditor.getCurrentEditor():
            self.scriptEditor.setEditMenu(self.editmenu)
            self.scriptEditor.OnEditMenu(event,self)
        
        # If we have highlighted text, enable the appropriate options
        if selection:
            self.editmenu.Enable(self.ID_COPY,True)
            if hasattr(inFocus,'WriteText'):
                self.editmenu.Enable(self.ID_CUT,True)
                self.editmenu.Enable(self.ID_DEL,True)

        if not wx.TheClipboard.Open():
            logger.error("Can't open system clipboard")
            return
        data = wx.TextDataObject()
        hasData = wx.TheClipboard.GetData(data)

        # if we can paste, enable the option
        if hasData and data.GetText() and hasattr(inFocus,'WriteText'):
            self.editmenu.Enable(self.ID_PASTE,True)

        wx.TheClipboard.Close()
        
    def makePropPage(self):
        '''Initialize the static controls for the properties notebook page.'''
        self.props = PropWindow.PropWindow(self.notebook)
        self.props.mainAppWindow = self
        self.notebook.AddPage(self.props, _("Properties"), 'props')

    def treeFromERF(self):
        '''Make a new tree control from the erf file currently
        associated with the app. Does so in a new thread.'''
        self.selectedTreeItem = None
        self.tree.DeleteAllItems()
        self.treeRoot = self.tree.AddRoot(self.module.getName())
        self.tree.SetPyData(self.treeRoot,self.module)
        wx.BeginBusyCursor()
        self.doTreeFromERF()
        self.treeFromERFDone()
        wx.EndBusyCursor()

    def doTreeFromERF(self):
        '''The thread body for loading an ERF file.
        Do not call any function that changes the interface
        from this method. You need to set a flag and call
        it from the main app thread, as otherwise things will get screwed up on
        linux.'''
        self.module.setProgressDisplay(self)
        self.areas = self.module.getAreas()

    def setFileChanged(self,fc=True):
        '''Call this when the loaded file has changed
        (someone used a control, usually).'''
        self.fileChanged = fc
        self.filemenu.Enable(self.ID_SAVE,fc)
        
    def treeFromERFDone(self):
        '''This gets called when we finish loading a new ERF file.
        It gets the interface into its final state and cleans up a bit.'''
        self.setStatus("Preparing user interface...")
        areaRoot = self.tree.AppendItem(self.treeRoot,'Areas')
        for area in self.areas.values():
            self.makeAreaItem(areaRoot,area)
        self.scriptRoot = self.tree.AppendItem(self.treeRoot,_('Scripts'))
        self.addScripts()
        self.conversationRoot = self.tree.AppendItem(self.treeRoot,_('Conversations'))
        self.addConversations()
        self.factionRoot = self.tree.AppendItem(self.treeRoot,_('Factions'))
        self.addFactions()
        self.notebook.Refresh()
        self.SetStatusText(_("Read ") + self.fname)
        self.filemenu.Enable(self.ID_SAVEAS,True)
        self.filemenu.Enable(self.ID_ADD_ERF,True)
        self.filemenu.Enable(self.ID_ADD_RESOURCE,True)
        self.fileChanged = False
        self.tree.Expand(self.treeRoot)
        self.tree.UnselectAll()
        self.tree.SelectItem(self.treeRoot)
        self.setStatus("Ready.")
        
    def OnFileHistory(self,event):
        '''Callback for someone selecting a file history menu item.'''
        fileNum = event.GetId() - wx.ID_FILE1
        self.readFile(self.filehistory.GetHistoryFile(fileNum))
        
    def OnSize(self,event):
        rect = self.GetStatusBar().GetFieldRect(1)
        self.statusProgress.SetPosition((rect.x+1,rect.y+1))
        self.statusProgress.SetSize((rect.width-2,rect.height-2))
        event.Skip()

    def addScripts(self):
        '''Add the scripts contained in our module to the interface.'''
        self.tree.DeleteChildren(self.scriptRoot)
        scripts = self.module.getScripts()
        scriptNames = scripts.keys()
        scriptNames.sort()
        for s in scriptNames:
            name = s.split('.')[0]
            scriptItem = self.tree.AppendItem(self.scriptRoot,name)
            scripts[s].setNWNDir(self.prefs['NWNAppDir'])
            scripts[s].setModule(self.fname)
            self.tree.SetPyData(scriptItem,scripts[s])

    def addConversations(self):
        '''Add the conversations contained in our module to the interface.'''

        self.tree.DeleteChildren(self.conversationRoot)
        conversations = self.module.getConversations()
        conversationNames = conversations.keys()
        conversationNames.sort()
        for c in conversationNames:
            name = c.split('.')[0]
            conversationItem = self.tree.AppendItem(self.conversationRoot,name)
            self.tree.SetPyData(conversationItem,Conversation(c,conversations[c]))

    def addFactions(self):
        '''Add the factions contained in our module to the interface'''
        self.tree.DeleteChildren(self.factionRoot)
        factions = self.module.getFactions()
        factionNames = factions.keys()
        factionNames.sort()
        for f in factionNames:
            factionItem = self.tree.AppendItem(self.factionRoot,f)
            self.tree.SetPyData(factionItem,factions[f])

    def init(self):
        '''Schedule the the app init routine.'''
        self.doInit = True

    def kick(self,event):
        '''kick the idle func even without events'''
        wx.WakeUpIdle()

    def idle(self,event):
        '''Called on idle events. This is where the interface updates for
        other threads happen (they cannot update the interface themselves).
        For example, this handles updates to the progress bar and
        finishing up ERF file loading.'''
        if self.doInit:
            self.doInit = False
            self.initResourceManager()
        if self.RMThread and not self.RMThread.isAlive() and self.doRead:
            try:
                self.readFile(self.fname)
            except:
                pass
            self.doRead = False
        if self.RMThread and not self.RMThread.isAlive():
            if self.splash:
                self.splash.Show(False)
                self.splash.Destroy()
            self.showToolPalette()
            self.Show(True)
            self.Enable(True)
            self.SetStatusText(_("Welcome to neveredit..."))
            self.RMThread = None
            self.threadAlive = False
        if self.progress > 0:
            self.setProgress(self.progress)
            self.statusProgress.Show(True)
            self.statusProgress.SetValue(int(self.progress))
        else:
            self.statusProgress.Show(False)
        if self.showScriptEditorFix:
            self.showScriptEditor();
            self.showScriptEditorFix = False
        if self.selectThisItem != None:
            self.selectTreeItemById(self.selectThisItem)
            self.selectThisItem = None

    def selectTreeItemById(self,oid):
        '''try to find an item in the current module by object id and
        select the corresponding tree item'''
        item = self.idToTreeItemMap.get(oid,None)
        if item:
            self.tree.EnsureVisible(item)
            self.tree.SelectItem(item)
        else:
            logger.warning('cannot find tree item with id %d' % id)
        
    def OnScriptAdded(self,event):
        """event handler for new script being added to module"""
        self.scriptEditor.addChangeListener(self.setFileChanged)
        data = self.getSelectedTreeItemData()
        reselect = False
        if data and data.__class__ == Script:
            self.unselectTreeItem()
            reselect = True
        self.addScripts()
        if reselect:
            self.tree.SelectItem(self.scriptRoot)

    def OnMapSelection(self,event):
        '''handle a map window selection event'''
        self.selectTreeItemById(event.getSelectedId())

    def OnMapMove(self,event):
        '''handle a map movement event'''
        self.setFileChanged(True)

    def OnMapThingAdded(self,event):
        '''handle the addition of a new item to the map'''
        self.unselectTreeItem()
        self.tree.DeleteChildren(self.lastAreaItem)
        self.subtreeFromArea(self.lastAreaItem,self.map.getArea())
        self.selectThisItem = event.getSelectedId()
        # removing this line prevents a crash - good as a *temporary*
        # fix, but the crash should be investigated
        # this also cause functionality loss (auto-selection of the thing added
        self.setFileChanged(True)

    def unselectTreeItem(self):
        """unselect the currently selected tree item."""
        self.maybeApplyPropControlValues()
        self.selectedTreeItem = None
        self.tree.Unselect()
        
    def makeAreaItem(self,item,area):
        '''Create the parent tree item for an area'''
        areaItem = self.tree.AppendItem(item,area.getName())
        self.tree.SetItemHasChildren(areaItem,True)
        self.tree.SetPyData(areaItem,area)
        
    def subtreeFromArea(self,areaItem,area):
        '''Create a new subtree for a module area.'''
        doors = area.getDoors()
        if len(doors) > 0:
            doorParentItem = self.tree.AppendItem(areaItem,_('Doors'))
            for door in doors:
                doorItem = self.tree.AppendItem(doorParentItem,
                                                door.getName())
                self.tree.SetPyData(doorItem,door)
                self.idToTreeItemMap[door.getNevereditId()] = doorItem
            
        placeables = area.getPlaceables()
        if len(placeables) > 0:
            placeableParentItem = self.tree.AppendItem(areaItem,
                                                       _('Placeables'))
            for placeable in placeables:
                placeableItem = self.tree.AppendItem(placeableParentItem,
                                                     placeable.getName())
                self.tree.SetPyData(placeableItem,placeable)
                self.idToTreeItemMap[placeable.getNevereditId()] = placeableItem

        creatures = area.getCreatures()
        if len(creatures) > 0:
            creatureParentItem = self.tree.AppendItem(areaItem,
                                                      _('Creatures'))
            for creature in creatures:
                creatureItem = self.tree.AppendItem(creatureParentItem,
                                                    creature.getName())
                self.tree.SetPyData(creatureItem,creature)
                self.idToTreeItemMap[creature.getNevereditId()] = creatureItem
        
        items = area.getItems()
        if len(items) > 0:
            itemParentItem = self.tree.AppendItem(areaItem,_('Items'))
            for item in items:
                itemItem = self.tree.AppendItem(itemParentItem,
                                                item.getName())
                self.tree.SetPyData(itemItem,item)
                self.idToTreeItemMap[item.getNevereditId()] = itemItem

        waypoints = area.getWayPoints()
        if len(waypoints)>0:
            waypointParentItem = self.tree.AppendItem(areaItem,_('WayPoints'))
            for waypoint in waypoints:
                waypointItem = self.tree.AppendItem(waypointParentItem,
                                                waypoint.getName())
                self.tree.SetPyData(waypointItem,waypoint)
                self.idToTreeItemMap[waypoint.getNevereditId()] = waypointItem

    def isAreaItem(self,item):
        data = self.tree.GetPyData(item)
        return data and data.__class__ == Area.Area
    
    def getAreaForTreeItem(self,item):
        '''Get the area associated with this tree item'''
        item = self.getParentAreaItem(item)
        if item:
            return self.tree.GetPyData(item)
        else:
            return None

    def getParentAreaItem(self,item):
        '''Get the parent item in the tree that contains the area'''
        while item:
            data = self.tree.GetPyData(item)
            if data and data.__class__ == Area.Area:
                return item
            else:
                item = self.tree.GetItemParent(item)
        return None
    
    def treeItemExpanding(self,event):
        """Dynamically create the children of the currently expanding item."""
        item = event.GetItem()
        if self.isAreaItem(item):
            area = self.getAreaForTreeItem(item)
            area.readContents()
            self.subtreeFromArea(item,area)

    def treeItemCollapsed(self,event):
        item = event.GetItem()
        if self.isAreaItem(item):
            self.getAreaForTreeItem(item).discardContents()
            self.tree.DeleteChildren(item)

    def getSelectedTreeItemData(self):
        '''
        get the data stored with the currently selected tree item
        @return: the stored data object of the current item
        '''
        return self.tree.GetPyData(self.tree.GetSelection())

    def OnNotebookPageChanged(self,event):
        '''Callback for notebook page changing event'''
        self.maybeApplyPropControlValues()
        self.syncDisplayedPage()
        
    def syncDisplayedPage(self):
        '''
        The main application notebook does a lazy update: only when
        the user actually switches to a page does the page content get
        created. This leads to longer switching times, but shorter
        time to select a new item in the module tree. This method
        is called when the notebook page changes and ensures that
        the content is loaded if it has not been loaded before.
        '''
        if not self.selectedTreeItem:
            return        
        data = self.tree.GetPyData(self.selectedTreeItem)
        area = self.getAreaForTreeItem(self.selectedTreeItem)
        tag = self.notebook.getSelectedTag()
        if not data and not area:
            return
        if not self.notebook.doesCurrentPageNeedSync():
            if tag == 'map' and self.toolPalette:
                self.toolPalette.GetToolBar().Enable(True)
            else:
                self.toolPalette.GetToolBar().Enable(False)
            return
        self.SetEvtHandlerEnabled(False)
        self.notebook.SetEvtHandlerEnabled(False)
        if self.toolPalette:
            self.toolPalette.GetToolBar().Enable(False)
        if tag == 'props':
            self.props.makePropsForItem(data,self)
        elif tag == 'map':
            self.map.setArea(area)
            MapWindow.EVT_MAPSINGLESELECTION(self.map,
                                             self.OnMapSelection)
            MapWindow.EVT_MAPMOVE(self.map,self.OnMapMove)
            MapWindow.EVT_MAPTHINGADDED(self.map,self.OnMapThingAdded)
            if self.toolPalette:
                ToolPalette.EVT_TOOLSELECTION(self.toolPalette,
                                              self.map.toolSelected)
                self.toolPalette.GetToolBar().Enable(True)
                if data:
                    self.map.selectThingById(data.getNevereditId())
        elif tag == 'model':
            self.model.setModel(data.getModel(True))
        self.notebook.setCurrentPageSync(False)
        self.SetEvtHandlerEnabled(True)
        self.notebook.SetEvtHandlerEnabled(True)

    def treeSelChanged(self,event):
        '''Callback to handle the user changing the selection
        in the main tree.'''
        logger.info("treeSelChanged " + `event`)
        self.maybeApplyPropControlValues()
        lastItem = self.selectedTreeItem
        self.selectedTreeItem = event.GetItem()
        if self.isAreaItem(event.GetItem()):
            self.tree.Expand(event.GetItem())
        if not self.selectedTreeItem:
            return
        data = self.tree.GetPyData(self.selectedTreeItem)
        notebookSelection = self.notebook.GetSelection()
        if hasattr(data,'iterateProperties') and\
               not self.notebook.getPageByTag('props'):
            self.makePropPage()
        elif not hasattr(data,'iterateProperties'):
            self.notebook.deletePageByTag('props')
        area = self.getAreaForTreeItem(self.selectedTreeItem)
        oldArea = self.getAreaForTreeItem(lastItem)
        if oldArea and area != oldArea:
            oldArea.discardTiles()
        if area:
            self.lastAreaItem = self.getParentAreaItem(self.selectedTreeItem)
        if area and not self.notebook.getPageByTag('map'):
            self.map = MapWindow.MapWindow(self.notebook)
            self.notebook.AddPage(self.map, _('Map'), 'map')
            self.map.setProgressDisplay(self)
        elif not area and self.notebook.getPageByTag('map'):
            self.map.setArea(None)
            self.notebook.deletePageByTag('map')
        if area and self.toolPalette:
            self.toolPalette.toggleToolOn(ToolPalette.SELECTION_TOOL)
        
        if self.notebook.getPageByTag('model') and not hasattr(data,'getModel'):
            self.notebook.deletePageByTag('model')
        if hasattr(data,'getModel'):
            if not self.model:
                self.model = ModelWindow.ModelWindow(self.notebook)
                self.notebook.AddPage(self.model, _('Model'), 'model')

        if data:
            if data.__class__ == Script:
                self.scriptEditor.addScript(data)
                self.scriptEditor.addChangeListener(self.setFileChanged)
                self.selectedTreeItem = lastItem #we didn't actually change the main display
                self.showScriptEditor()
                self.showScriptEditorFix = True
                return
            if data.__class__ == Conversation:
                self.notebook.deletePageByTag('factions')
                if not self.notebook.getPageByTag('conversation'):
                    conversationPage = ConversationWindow\
                                       .ConversationWindow(self.notebook,
                                                           data)
                    conversationPage.addChangeListener(self.setFileChanged)
                    self.notebook.AddPage(conversationPage, _("Conversation"), 'conversation')
                else:
                    self.notebook.getPageByTag('conversation').setConversation(data)
            elif data.__class__ == FactionStruct:
                self.notebook.deletePageByTag('conversation')
                if self.notebook.getPageByTag('factions'):
                    # I destroy and rebuild, to keep in sync with the 'factionName' property
                    self.notebook.deletePageByTag('factions')
                facGrid = FactionGridWindow(self.notebook,self.module.facObject,self)
                self.notebook.AddPage(facGrid,_('Factions reactions'),'factions')
            else:
                self.notebook.deletePageByTag('factions')
                self.notebook.deletePageByTag('conversation')
        else:
            self.notebook.deletePageByTag('conversation')
            self.notebook.deletePageByTag('factions')
                    
        if notebookSelection < self.notebook.GetPageCount() and\
               not notebookSelection == self.notebook.getPageInfoByTag('welcome')[0]:
            self.notebook.SetSelection(notebookSelection)
        else:
            self.notebook.selectPageByTag('props')

        self.notebook.setSyncAllPages(True)
        self.syncDisplayedPage()

    def maybeApplyPropControlValues(self):
        '''
        Check if the selected item in the main module tree has
        data associated with it, and, if so, apply its control
        values by calling applyPropControlValues().
        '''
        # kill any thread playing BMU sound
        SoundControl.Event_Die.set()
        if self.selectedTreeItem:
            data = self.tree.GetPyData(self.selectedTreeItem)
            if data:
                if data.__class__ == Conversation:
                    self.notebook.getPageByTag('conversation').maybeApplyPropControlValues()
                self.applyPropControlValues()

    def applyPropControlValues(self):
        '''This method reads back in the values of currently
        displayed property controls and updates the actual
        module file to reflect these values.'''
        if self.props:
            # a PropWindow is in the tab list
            if self.props.applyPropControlValues(self.tree\
                                                 .GetPyData(self.selectedTreeItem)):
                self.setFileChanged(True)
        factions_notebook = self.notebook.getPageByTag('factions')
        if factions_notebook:
            # we have a faction window in the tabs
            if factions_notebook.applyPropControlValues(self.module.facObject):
                self.setFileChanged(True)
            
    def OnFileChanged(self,event):
        self.setFileChanged(True)
        
    def about(self,event):
        '''About menu item callback.'''
        dlg = wx.MessageDialog(self,_('neveredit v') + neveredit.__version__ +
                              _(''' by Peter Gorniak and others
Copyright 2003-2006'''),
                               _('About neveredit'),
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def maybeSave(self):
        '''Ask whether we should save changes and do so if yes.
        @return: boolean indicating whether we can proceed
                 (data saved or discarded).
        '''
        self.maybeApplyPropControlValues()
        if self.fileChanged:
            dlg = wx.MessageDialog(self,_('Save Changes to ') + self.fname
                                  + '?',
                                  _("Changed File"),
                                   wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
            answer = dlg.ShowModal ()
            if answer == wx.ID_YES:
                self.saveFile(None)
                return True
            elif answer == wx.ID_CANCEL:
                return False
            else:
                return True
        else:
            return True

    def OnCloseToolPalette(self,event):
        self.toolPalette = None
        
    def OnCloseSplash(self,event):
        self.splash = None

    def OnCloseWindow(self,event):
        self.scriptEditorFrame.Show(False)
        
    def OnClose(self,doForce=False):
        '''Window closing callback method for the main app.'''
        self.savePrefs()
        if self.maybeSave():
            sys.exit()
        else:
            return False

    def reparent(self,window,newparent):
        for c in window.GetChildren():
            window.RemoveChild(c)
            window.AddChild(c)
            self.reparent(c,window)
            
    def OnDetach(self,event):
        page = self.notebook.GetPage(self.notebook.GetSelection())
        print page
        self.notebook.RemovePage(self.notebook.GetSelection())
        frame = wx.Frame(self,-1,self.notebook\
                         .GetPageText(self.notebook.GetSelection()))
        page.Reparent(frame)
        self.reparent(page,frame)
        frame.Show(True)

    def windowMenu(self,event):
        id = event.GetId()
        if id == self.ID_MAIN_WINDOW_MITEM:
            self.Show(True)
            self.Raise()
        elif id == self.ID_PALETTE_WINDOW_MITEM:
            self.showToolPalette()
            self.toolPalette.Raise()
        elif id == self.ID_SCRIPT_WINDOW_MITEM:
            self.showScriptEditor()
            
    def exit(self,event):
        '''Exit the Main app, asking about possible unsaved changes.'''
        if self.OnClose():
            sys.exit()

    def help(self,event):
        self.helpviewer.DisplayContents()

    def OnPreferences(self,event):
        '''Display a prefs dialog.'''
        oldAppDir = self.prefs['NWNAppDir']
        d = PreferencesDialog.PreferencesDialog(self)
        if d.ShowAndInterpret():
            self.scriptEditor.prefsChanged()
            # Update the keys that correspond to the up, down, left and right.
            if self.model :
                self.model.UpdateKeys();
            if oldAppDir != self.prefs['NWNAppDir']:
                self.initResourceManager()
        
    def savePrefs(self):
        '''Save the current preferences settings.'''
        n = self.filehistory.GetCount()
        files = []
        for i in range(n):
            files.append(self.filehistory.GetHistoryFile(i))
        self.prefs['FileHistory'] = files
        self.prefs.save()
        
    def loadPrefs(self):
        '''Load preferences from their standard location.'''
        self.prefs = Preferences.getPreferences()
        #print self.prefs.filehistory
        for f in self.prefs['FileHistory']:
            try:
                f.encode('ascii')
            except:
                print >>sys.stderr,"not adding filename to file history to " +\
                      "work around wxWindow encoding bug"
                continue
            #print 'trying to add',f.encode('utf8')
            self.filehistory.AddFileToHistory(f)
        
    def doReadFile(self,fname):
        '''Read in a file. Does not ask about unsaved changes.
        @param fname: name of file to read
        '''
        self.SetStatusText("Reading " + fname + "...")
        try:
            self.module = Module.Module(fname)
        except IOError,e:
            dlg = wx.MessageDialog(self,_("Error opening file (" + e.strerror
                                          + '): ' + fname),
                                   _("Error Opening File"),wx.OK|wx.ICON_ERROR)
            dlg.ShowModal()
            return
        neverglobals.getResourceManager().addModule(self.module)
        self.fname = fname
        self.treeFromERF()
        self.setFileChanged(False)
        if self.module.needSave:
            self.setFileChanged(True)
            self.SetStatusText(_("Converting old module to new style..."))
        self.filehistory.AddFileToHistory(fname)
        self.scriptEditor.setModule(self.module)
        self.SetTitle('neveredit: ' + os.path.basename(self.module.getFileName()))
        
    def readFile(self,fname):
        '''Read in a file. Asks about unsaved changes.
        @param fname: name of file to read
        '''
        if self.maybeSave():
            self.doReadFile(fname)
        
    def openFile(self,event):
        '''Display a dialog to find a file, and load it if user says yes.'''
        try:
            lastOpenDir = self.prefs['LastOpenDir']
        except:
            lastOpenDir = os.path.join(self.prefs['NWNAppDir'],'modules')
        dlg = wx.FileDialog(self,_("Choose an ERF (mod/hak/nwm) File"),
                            lastOpenDir, '',
                           'MOD|*.mod|ERF|*.erf|HAK|*.hak|SAV|*.sav|'
                            +_('All Files')
                           +'|*.*',
                           wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.readFile(dlg.GetPath())
        dlg.Destroy()

    def addERFFile(self,event):
        '''Display a dialog to find a file and add its entries to
        the current one.'''
        dlg = wx.MessageDialog(self,_(
'''Merging in a an ERF will overwrite the file you have currently
loaded and save any changes you have made so far. Proceed?'''),
                              _("Merge ERF File"),wx.YES_NO|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_NO:
            return
        try:
            lastERFDir = self.prefs['LastERFDir']
        except:
            lastERFDir = os.path.join(self.prefs['NWNAppDir'],'erf')

        dlg = wx.FileDialog(self,_("Choose an ERF (mod/hak/nwm) File to add"),
                           lastERFDir, '',
                           'ERF|*.erf|MOD|*.mod|HAK|*.hak|SAV|*.sav|'
                            +_('All Files')
                           +'|*.*',
                           wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.maybeApplyPropControlValues()
            self.notebook.SetSelection(0)
            self.tree.SelectItem(self.treeRoot)
            self.module.addERFFile(dlg.GetPath())
            self.treeFromERF()
        dlg.Destroy()

    def addResourceFile(self,event):
        '''Display a dialog to find a file and add it as a resource to
        the current module.'''
        dlg = wx.FileDialog(self,_("Choose a resource file (e.g. .dlg) to add"),
                           '', '',
                            _('All Files')
                           +'|*.*',
                           wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            try:
                self.module.addResourceFile(dlg.GetPath())
                self.maybeApplyPropControlValues()
                self.treeFromERF()
                self.setFileChanged(True)
                dlg.Destroy()
            except ValueError:
                dlg.Destroy()
                dlg2 = wx.MessageDialog(self,_('"'
                                               + dlg.GetPath()
                                               + '" is not a valid nwn resource name'),
                                        _("Resource Name Error"),wx.OK|wx.ICON_ERROR)
                dlg2.ShowModal()
                dlg2.Destroy()
                
                
        
    def saveFile(self,event):
        '''Save the file to the file name we loaded it from.'''
        self.maybeApplyPropControlValues()
        self.module.saveToReadFile()
        self.setFileChanged(False)
        self.setStatus("Saved " + self.module.getFileName() + '.')

        
    def saveFileAs(self,event):
        try:
            lastSaveDir = self.prefs['LastSaveDir']
        except:
            lastSaveDir = os.path.join(self.prefs['NWNAppDir'],'modules')

        '''Save the file to a filename the users specifies in a file dialog.'''
        dlg = wx.FileDialog(self,_("Choose a an ERF (mod/hak/nwm)"
                                   " File Name for Saving"),
                            lastSaveDir, '',
                            'MOD|*.mod|HAK|*.hak|'+_('All Files') + '|*.*',
                            wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.maybeApplyPropControlValues()
            self.module.saveAs(dlg.GetPath())
            self.fname = dlg.GetPath()
        dlg.Destroy()
        self.setFileChanged(False)
        self.SetTitle('neveredit: ' + self.module.getFileName())
        self.setStatus("Saved " + self.module.getFileName() + '.')

    def simulateTreeSelChange(self):
        lastSelected = self.selectedTreeItem
        self.selectedTreeItem = None
        self.tree.SelectItem(lastSelected,False)
        self.tree.SelectItem(lastSelected,True)

    def propertyChanged(self,control,prop):
        if control.__class__ == wx.Button and control.GetName() == "Faction_addButton":
            # add a faction
            factionItem = self.tree.AppendItem(self.factionRoot,\
                prop.getName())
            self.tree.SetPyData(factionItem,prop)
            self.tree.Refresh()
            self.simulateTreeSelChange()
            self.setFileChanged(True)
        elif control.__class__ == wx.Button and control.GetName() == "Faction_delButton":
            # remove a faction
            pass
        elif prop.getName() == 'FactionName':
            # change a faction name
            # the modified item should be the one selected...
            item = self.tree.GetSelection()
            self.tree.SetItemText(item,control.control.GetValue())
            data = self.tree.GetPyData(item)
            data.setProperty('FactionName',control.control.GetValue())
            self.simulateTreeSelChange()
            self.setFileChanged(True)
        elif control.__class__ == FactionGrid:
            self.applyPropControlValues()
            self.setFileChanged(True)


def run(args=None):
    app = wx.PySimpleApp()
    app.SetVendorName('org.openknights')
    app.SetAppName('neveredit')
    frame = NeverEditMainWindow(None,-1,_("neveredit"))
    if args and len(args) > 0:
        frame.fname = args[0]
        frame.doRead = True
    frame.init()
    app.MainLoop()

def main():
    if len(os.path.dirname(sys.argv[0])) > 0:
        # mainly to find neveredit.jpg in mac os app bundle
        os.chdir(os.path.dirname(sys.argv[0]))
    run()

if __name__ == "__main__":
    main()
