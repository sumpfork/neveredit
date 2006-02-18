import logging
logger = logging.getLogger('neveredit.ui')

import sys,string,re,os

import wx
import wx.stc as stc

import neveredit
import neveredit.ui.HelpViewer
from neveredit.ui import PreferencesDialog
from neveredit.game.Script import Script
from neveredit.game import Module
from neveredit.util import Utils
from neveredit.util import Preferences
from neveredit.util import neverglobals

import gettext

gettext.install('neveredit','translations')

VERSION = neveredit.__version__

SCRIPTADDEVENT = wx.NewEventType()

def EVT_SCRIPTADD(window,function):
    '''notifies about the selection of a tool in the palette'''
    window.Connect(-1,-1,SCRIPTADDEVENT,function)

class ScriptAddEvent(wx.PyCommandEvent):
    eventType = SCRIPTADDEVENT
    def __init__(self,windowID,script):
        wx.PyCommandEvent.__init__(self,self.eventType,windowID)
        self.script = script

    def getScript(self):
        return self.script
    
    def Clone(self):
        self.__class__(self.GetId(),self.script)

class UnitializedError(Exception):
    pass
        
class NewScriptDialog(wx.Dialog):
    def __init__(self,parent,title):
        wx.Dialog.__init__(self,parent,title=title)
        
        dlg = self

        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(dlg, -1, "New Script Name:")
        label.SetHelpText("Enter a new script name, max 16 characters")
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.text = wx.TextCtrl(dlg,-1)
        self.text.SetHelpText("New Script Name")
        self.text.SetMaxLength(16)
        box.Add(self.text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        btn = wx.Button(dlg, wx.ID_OK, " OK ")
        btn.SetDefault()
        btn.SetHelpText("Create a script with this name")
        box.Add(btn, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        btn = wx.Button(dlg, wx.ID_CANCEL, " Cancel ")
        btn.SetHelpText("Don't create new script.")
        box.Add(btn, 0, wx.ALIGN_RIGHT|wx.ALL, 5)

        sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        
        dlg.SetSizer(sizer)
        dlg.SetAutoLayout(True)
        dlg.CenterOnParent()
        sizer.Fit(dlg)

        self.Bind(wx.EVT_TEXT,self.OnText,id=self.text.GetId())
        self.value = ''

    def OnText(self,event):
        self.value = self.text.GetValue()
        
    def getValue(self):
        return self.value

    def ShowModal(self):
        r = wx.Dialog.ShowModal(self)
        if r == wx.ID_OK:
            return self.getValue()
        else:
            return None
        
class ScriptEditor(wx.SplitterWindow):
    def __init__(self,parent,id,standalone=False):
        wx.SplitterWindow.__init__(self,parent,id)
        if standalone:
            self.ID_PREFS = wx.NewId()
            self.ID_ABOUT = wx.NewId()
            self.ID_OPEN  = wx.NewId()
            self.ID_SAVE  = wx.NewId()
            self.ID_SAVEAS = wx.NewId()
            self.ID_EXIT  = wx.NewId()
            self.ID_HELP = wx.NewId()
            self.ID_NEW = wx.NewId()            
            self.ID_CUT = wx.NewId()
            self.ID_COPY = wx.NewId()
            self.ID_PASTE = wx.NewId()
            self.ID_DEL = wx.NewId()

        self.standalone = standalone

        self.scripts = []
        self.scriptTable = {}
        self.editors = []
        self.helpviewer = None
        self.module = None

        splitter = self
        self.notebook = wx.Notebook(splitter,-1)
        buttonPanel = self.getFrame().CreateToolBar()
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnPageChanged)
        self.newButton = wx.Button(buttonPanel,-1,"New Script")
        buttonPanel.AddControl(self.newButton)
        self.newButton.Bind(wx.EVT_BUTTON,self.OnNew)
        self.newButton.Enable(False)
        self.compileButton = wx.Button(buttonPanel,-1,"Compile")
        buttonPanel.AddControl(self.compileButton)
        self.closeButton = wx.Button(buttonPanel,-1,"Close Script Tab")
        buttonPanel.AddControl(self.closeButton)
        self.helpButton = wx.Button(buttonPanel,-1,"Help on Selection")
        buttonPanel.AddControl(self.helpButton)
        self.scriptChoice = wx.Choice(buttonPanel,-1)
        buttonPanel.AddControl(self.scriptChoice)
        self.updateScriptChoice()
        self.scriptChoice.Bind(wx.EVT_CHOICE,self.OnScriptChoice)
        
        self.compileButton.Bind(wx.EVT_BUTTON,self.OnCompile)
        self.compileButton.Enable(False)
        self.closeButton.Bind(wx.EVT_BUTTON,self.OnCloseEditor)
        self.closeButton.Enable(False)
        self.helpButton.Bind(wx.EVT_BUTTON,self.OnHelp)
        self.helpButton.Enable(False)
        self.output = wx.ListCtrl(splitter,-1,style=wx.LC_REPORT|wx.LC_NO_HEADER)
        self.output.Bind(wx.EVT_LIST_ITEM_SELECTED,self.OnOutSelected)

        splitter.SplitHorizontally(self.notebook,self.output,-100)
        splitter.SetMinimumPaneSize(70)
                
        splitter.SetSashGravity(1.0)

        self.Bind(wx.EVT_SIZE,self.OnSize)
        parent.Bind(wx.EVT_CLOSE,self.OnClose)
        
        if self.standalone:
            self.setupMenus()
            helps = [file for file in os.listdir(os.getcwd())
                     if (file[:5] == 'help_' and file[-4:] == '.zip')]
            print os.getcwd()
            self.helpviewer = neveredit.ui.HelpViewer.makeHelpViewer(helps,os.getcwd())

        self.setFileChanged(False)
        self.fileChangeCallback = None

        self.prefs = Preferences.getPreferences()

    def getFrame(self):
        w = self.GetParent()
        while w and not w.IsTopLevel():
            w = w.GetParent()
        return w
    
    def setupMenus(self):

        frame = self.GetParent()
        
        if Utils.iAmOnMac():
            wx.App_SetMacExitMenuItemId(self.ID_EXIT)
            wx.App_SetMacPreferencesMenuItemId(self.ID_PREFS)
            wx.App_SetMacAboutMenuItemId(self.ID_ABOUT)

        #menus
        self.filemenu = wx.Menu()
        self.filemenu.Append(self.ID_NEW, '&' + ('New Script') + '\tCtrl+N',
                             _("Make new script"))
        self.filemenu.Append(self.ID_OPEN, '&' + _('Open Module...')
                             + '\tCtrl+O',
                             _("Open a File"))
        self.filemenu.AppendSeparator()
        self.filemenu.Append(self.ID_SAVE, '&' + _('Save') + '\tCtrl+S',
                             _("Save File"))
        self.filemenu.Append(self.ID_SAVEAS, '&' + _('Save As...') +
                             '\tShift+Ctrl+S',
                             _("Save File under a new name"))
        if not Utils.iAmOnMac():
            self.filemenu.Append(self.ID_EXIT,_('E&xit') + '\tAlt-X',
                                 _("Quit NeverScript"))
        self.filemenu.Enable(self.ID_SAVE,False)
        self.filemenu.Enable(self.ID_SAVEAS,False)

        self.editmenu = wx.Menu()
        self.setupEditMenu()
        
        helpmenu = wx.Menu()
        helpmenu.Append(self.ID_ABOUT, '&' + _('About...'),
                        _("About NeverScript"))
        helpmenu.Append(self.ID_HELP,'&'+ _('NeverScript Help'),
                        _("NeverScript Help"))
        
        menuBar = wx.MenuBar()
        menuBar.Append(self.filemenu,"&" + _("File"))
        menuBar.Append(self.editmenu, "&" + _("Edit"))
        menuBar.Append(helpmenu, "&" + _("Help"))
        frame.SetMenuBar(menuBar)
            
        wx.EVT_MENU(frame,self.ID_NEW,self.OnNew)
        wx.EVT_MENU(frame,self.ID_OPEN,self.openFile)
        wx.EVT_MENU(frame,self.ID_SAVE,self.saveFile)
        wx.EVT_MENU(frame,self.ID_SAVEAS,self.saveFileAs)
        wx.EVT_MENU(frame,self.ID_ABOUT,self.about)
        wx.EVT_MENU(frame,self.ID_EXIT,self.exit)
        wx.EVT_MENU(frame,self.ID_HELP,self.help)
        wx.EVT_MENU(frame,self.ID_PREFS,self.OnPreferences)
        
        self.filemenu.Enable(self.ID_SAVEAS,False)
        self.editmenu.Enable(self.ID_COPY,False)
        self.editmenu.Enable(self.ID_DEL,False)
        self.editmenu.Enable(self.ID_PASTE,False)
        self.editmenu.Enable(self.ID_CUT,False)
        self.filemenu.Enable(self.ID_NEW,False)
        self.filemenu.Enable(self.ID_SAVE,False)
        if self.standalone:
            self.editmenu.Enable(self.ID_PREFS,True)

    def setEditMenu(self, em):
        self.editmenu = em
        
    def setupEditMenu(self, editmenu=None, frame=None):
        '''Set up the Edit Menu'''
        if editmenu:
            self.editmenu = editmenu

        if self.editmenu.FindItemById(self.ID_CUT):
            return
        if not frame:
            frame = self.GetParent()
        
        self.editmenu.Append(self.ID_CUT, '&'+_('Cut'), _('cut'))
        self.editmenu.Append(self.ID_COPY, '&'+_('Copy'), _('copy'))
        self.editmenu.Append(self.ID_PASTE, '&'+_('Paste'), _('paste'))
        self.sep1=self.editmenu.AppendSeparator()
        self.editmenu.Append(self.ID_DEL, '&'+_('Delete'), _('del'))
        if self.standalone:
            self.sep2=self.editmenu.AppendSeparator()
            self.editmenu.Append(self.ID_PREFS,'&' + _('Preferences...'),
                                 _('prefs'))
        
        wx.EVT_MENU(frame,self.ID_DEL,self.OnDelete)
        wx.EVT_MENU(frame,self.ID_CUT,self.OnCut)
        wx.EVT_MENU(frame,self.ID_COPY,self.OnCopy)
        wx.EVT_MENU(frame,self.ID_PASTE,self.OnPaste)
        self.editmenu.Bind(wx.EVT_MENU_OPEN, self.OnEditMenu)
            
    def OnPaste(self,event):
        '''Perform a paste operation'''
        self.getCurrentEditor().Paste()

    def OnCopy(self,event):
        '''Perform a copy operation'''
        self.getCurrentEditor().Copy()
        

    def OnDelete(self,event):
        '''Perform a delete operation'''
        editor = self.getCurrentEditor()
        
        # Cut the item out and the clear it from the Clipboard        
        editor.Clear()

    def OnCut(self,event):
        '''Peform a cut operation'''
        editor = self.getCurrentEditor()
        
        # Cut the item out 
        editor.Cut()
       

    def OnEditMenu(self,event,idobject=None):
        if not idobject:
            idobject = self
        self.editmenu.Enable(idobject.ID_CUT,False)
        self.editmenu.Enable(idobject.ID_COPY,False)
        self.editmenu.Enable(idobject.ID_PASTE,False)
        self.editmenu.Enable(idobject.ID_DEL,False)
        # Guard against the possibility of no editors,
        # then check to see if any text has been selected.
        # If not, don't do anything
        if len(self.editors):
            text = self.getCurrentEditor().GetSelectedText()
        else:
            return

        # If we have highlighted text, enable the appropriate options
        if text:
            self.editmenu.Enable(idobject.ID_CUT,True)
            self.editmenu.Enable(idobject.ID_COPY,True)
            self.editmenu.Enable(idobject.ID_DEL,True)

        # if we can paste, enable the option
        if self.getCurrentEditor().CanPaste():
            self.editmenu.Enable(idobject.ID_PASTE,True)        
    
    def openFile(self,event):
        '''Display a dialog to find a file, and load it if user says yes.'''
        dlg = wx.FileDialog(self,_("Choose an ERF (mod/hak/nwm) File"),\
                            '', '',\
                            'MOD|*.mod|ERF|*.erf|HAK|*.hak|'+_('All Files')
                            +'|*.*',
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            m = Module.Module(dlg.GetPath())
            self.setModule(m)
        dlg.Destroy()

    def saveFile(self,event):
        '''save the module file'''
        self.commit()
        self.module.saveToReadFile()

    def saveFileAs(self,event):
        '''Save the file to a filename the users specifies in a file dialog.'''
        dlg = wx.FileDialog(self,_("Choose a an ERF (mod/hak/nwm) File Name for Saving"),
                           os.getcwd(), '',\
                           'MOD|*.mod|'+_('All Files') + '|*.*',
                           wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            self.commit()
            self.module.saveAs(dlg.GetPath())
        dlg.Destroy()
        self.setFileChanged(False)

    def OnFileChanged(self,event):
        self.setFileChanged(True)
        
    def setFileChanged(self,changed):
        if self.standalone:
            self.filemenu.Enable(self.ID_SAVE,changed)
        self.fileChanged = changed
        if changed and self.fileChangeCallback:
            self.fileChangeCallback()

    def OnPreferences(self,event):
        d = PreferencesDialog.PreferencesDialog(self.GetParent(),
                                                tablist=["ScriptEditorPanel"])
        if d.ShowAndInterpret():
            self.prefsChanged
            
    def prefsChanged(self):
        for e in self.editors:
            e.SetUseAntiAliasing(self.prefs['ScriptAntiAlias'])
        
    def about(self,event):
        '''About menu item callback.'''
        dlg = wx.MessageDialog(self,_('NeverScript ') + VERSION +
                               _(''' by Sumpfork (part of neveredit)
The OpenKnights Consortium
Copyright 2003-2004'''),
                               _('About NeverScript'),
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def help(self,event):
        self.helpviewer.DisplayContents()

    def maybeSave(self):
        '''Ask whether we should save changes and do so if yes.
        @return: boolean indicating whether changes were saved.'''
        if self.fileChanged:
            dlg = wx.MessageDialog(self,_('Save Changes to ') + self.module.getFileName()
                                  + '?',
                                  _("Changed File"),wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
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

    def OnClose(self,doForce=False):
        '''Window closing callback method for the main app.'''
        if self.maybeSave():
            sys.exit()
        else:
            return False
        
    def exit(self,event):
        '''Exit the Main app, asking about possible unsaved changes.'''
        if self.OnClose():
            sys.exit()

    def clearOutput(self):
        self.output.ClearAll()
        self.output.InsertColumn(0,"Output")
        self.output.SetColumnWidth(0,self.GetSize().width)
        
    def OnNew(self,event):
        if not self.module:
            raise UnitializedError,"Script Editor has no Module Assigned in OnNew"

        dlg = NewScriptDialog(self,"New Script")

        val = dlg.ShowModal()
        if val:
            val = val[:16]
            if not self.selectScript(val):
                script = Script(val + '.nss','')
                script.setModule(self.module.getFileName())
                script.setNWNDir(neverglobals.getResourceManager().getAppDir())
                self.module.addScript(script)
                self.addScript(script)
                self.updateScriptChoice()
                addEvent = ScriptAddEvent(self.GetId(),script)
                self.GetEventHandler().AddPendingEvent(addEvent)                
                self.setFileChanged(True)
                
    def OnPageChanged(self,event):
        #bug: I would've thought the GetSelection() on the notebook should return
        # the new selection, but it doesn't
        try:
            s = self.scripts[event.GetSelection()]
            self.scriptChoice.SetStringSelection(s.getName()[:-4])
        except:
            pass
        self.clearOutput()
        event.Skip()
        
    def OnScriptChoice(self,event):
        self.addScript(self.module.getScripts()[event.GetString().encode('latin1')])
        
    def OnCompile(self,event):
        self.compile()
            
    def OnCloseEditor(self,event):
        self.removeCurrentTab()
        
    def OnHelp(self,event):
        if self.helpviewer:
            try:
                sel = self.getCurrentEditor().GetSelectedText()
                if sel:
                    self.helpviewer.Display(sel)
            except IndexError:
                pass
    
    def OnSize(self,event):
        if self.output.GetColumnCount() > 0:
            self.output.SetColumnWidth(0,self.GetSize().width)
        event.Skip()

    def OnOutSelected(self,event):        
        line = event.GetIndex()
        r = re.compile('\([0-9]+\)')
        num = r.findall(self.output.GetItemText(line))
        if num:
            editor = self.getCurrentEditor()
            row = int(num[0][1:-1])-1
            editor.EnsureVisible(row)
            editor.GotoLine(row)            
            editor.SetSelection(editor.GetCurrentPos(),editor.GetLineEndPosition(row))

    def updateScriptChoice(self):
        if not self.module:
            self.scriptChoice.Enable(False)
        else:
            self.scriptChoice.Enable(True)
            self.scriptChoice.Clear()
            scriptNames = self.module.getScripts().keys()
            scriptNames.sort()
            self.scriptChoice.AppendItems(scriptNames)
            self.chooseCurrentScript()

    def chooseCurrentScript(self):
        try:
            self.scriptChoice.SetStringSelection(s.getName()[:-4])
        except:
            pass
                    
    def setModule(self,m):
        self.removeAllTabs()
        self.module = m
        self.newButton.Enable(True)
        if self.standalone:
            self.filemenu.Enable(self.ID_NEW,True)
            self.filemenu.Enable(self.ID_SAVEAS,True)        
            self.filemenu.Enable(self.ID_SAVEAS,True)
        self.updateScriptChoice()
        self.clearOutput()
        self.output.InsertStringItem(0,
                                     m.getFileName() +
                                     " loaded, select script from pulldown or add new script")
        
    def getCurrentEditor(self):
        try:
            return self.editors[self.notebook.GetSelection()]
        except IndexError:
            return None

    def commit(self):
        '''
        Takes the current content of the script shown in the GUI and copies it back
        to the module. This only sets the uncompiled version of the script.
        '''
        script = self.getCurrentScript()
        if script:
            script.setUnixData(self.editors[self.notebook.GetSelection()].GetText())
        
    def compile(self):
        '''
        Try to compile the currently selected script.
        @return: the compiled script binary data, or None if compile unsuccessful
        '''
        script = self.getCurrentScript()
        self.commit()
        try:
            compiled,err = script.compile()
        except:
            logger.exception("script compile failed")
            self.output.InsertStringItem(0,
                                         "compiler call failed "
                                         "- compiler not available?")
            return None
        prefix = "Errors occured during compile:\n"
        if compiled:
            prefix = "Compile Successful!\n"
            self.setFileChanged(True)
        if err:
            prefix += err
        self.clearOutput()
        lines = prefix.split('\n')
        for i,line in enumerate(lines):
            if line:
                self.output.InsertStringItem(i,line)
        return compiled

    def setHelpViewer(self,hv):
        self.helpviewer = hv
        self.helpButton.Enable(True)
        
    def getCurrentScript(self):
        '''
        Get the currently selected script.
        @return: the currently selected Script object
        @raise: IndexError if no scripts present
        '''
        return self.scripts[self.notebook.GetSelection()]
    
    def getScript(self,name):
        '''
        Get a script object from the editor.
        @param name: name of the script to get
        @return: a Script object or None if not present
        '''
        s = self.scriptTable.get(name,None)
        if s:
            return s[0]
        else:
            return None

    def selectScript(self,name):
        '''
        Attempt to select the script with the given name
        in the editor.
        @param name: the name of the script (e.g. "script.NSS")
        @return: True if script was present, False otherwise
        '''
        s = self.scriptTable.get(name,None)
        if s:
            if self.notebook.GetSelection() != s[1]:
                self.notebook.SetSelection(s[1])
                self.chooseCurrentScript()
                self.clearOutput()
            return True
        return False

    def addChangeListener(self,callback):
        '''
        Add a listener that will get called on any changes to the file.
        @param callback: the function to be called (will be called without args)
        '''
        self.fileChangeCallback = callback

    def addScript(self,s):
        '''
        Add a Script object to the editor
        @param s: the script object to add
        '''
        if not self.selectScript(s.getName()):
            s.setNWNDir(neverglobals.getResourceManager().getAppDir())
            if self.module:
                s.setModule(self.module.getFileName())
            self.scripts.append(s)
            editor = self.makeEditor()
            editor.SetText(s.getData())
            editor.ConvertEOLs(stc.STC_EOL_LF)
            self.editors.append(editor)
            self.notebook.AddPage(editor,s.getName()[:-4])
            self.notebook.SetSelection(len(self.scripts)-1)
            self.scriptTable[s.getName()] = (s,len(self.scripts)-1)
            self.chooseCurrentScript()
            self.clearOutput()
            editor.SetModEventMask(wx.stc.STC_MOD_INSERTTEXT|
                                   wx.stc.STC_MOD_DELETETEXT|
                                   wx.stc.STC_PERFORMED_USER)
            wx.stc.EVT_STC_CHANGE(editor,
                                  editor.GetId(),
                                  self.OnFileChanged)
        self.compileButton.Enable(True)
        self.closeButton.Enable(True)
        if self.helpviewer:
            self.helpButton.Enable(True)

    def removeCurrentTab(self):
        if self.prefs['ScriptAutoCompile']:
            self.compile()
        index = self.notebook.GetSelection()
        s = self.getCurrentScript()
        self.scripts = self.scripts[:index] + self.scripts[index+1:]
        self.editors = self.editors[:index] + self.editors[index+1:]
        del self.scriptTable[s.getName()]
        self.notebook.DeletePage(index)
        if not self.notebook.GetPageCount():
            self.closeButton.Enable(False)
            self.compileButton.Enable(False)
            self.helpButton.Enable(False)

    def removeAllTabs(self):
        while self.notebook.GetPageCount() > 0:
            self.removeCurrentTab()
            
    def makeEditor(self):
        textCtl = stc.StyledTextCtrl(self.notebook,-1)
        textCtl.SetLexerLanguage('cpp')
        textCtl.SetKeyWords(0,Script.lang_keywords)
        textCtl.SetKeyWords(1,string.join(Script.nwscript_keywords.keys()))

        textCtl.SetProperty("fold","1")
        
        textCtl.SetViewWhiteSpace(False)
        textCtl.SetUseAntiAliasing(self.prefs['ScriptAntiAlias'])

        textCtl.SetEOLMode(stc.STC_EOL_LF)
        textCtl.SetUseTabs(False)
        textCtl.SetTabWidth(4)
        textCtl.SetTabIndents(True)
        textCtl.SetBackSpaceUnIndents(True)
        textCtl.SetIndent(4)
        
        #textCtl.SetEdgeMode(stc.STC_EDGE_LINE)
        #textCtl.SetEdgeColumn(78)

        # Setup a margin to hold fold markers
        textCtl.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        textCtl.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        textCtl.SetMarginSensitive(2, True)
        textCtl.SetMarginWidth(2, 12)
        
        textCtl.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,
                          stc.STC_MARK_CIRCLEMINUS,          "white", "#404040");
        textCtl.MarkerDefine(stc.STC_MARKNUM_FOLDER,
                          stc.STC_MARK_CIRCLEPLUS,           "white", "#404040");
        textCtl.MarkerDefine(stc.STC_MARKNUM_FOLDERSUB,
                          stc.STC_MARK_VLINE,                "white", "#404040");
        textCtl.MarkerDefine(stc.STC_MARKNUM_FOLDERTAIL,
                          stc.STC_MARK_LCORNERCURVE,         "white", "#404040");
        textCtl.MarkerDefine(stc.STC_MARKNUM_FOLDEREND,
                          stc.STC_MARK_CIRCLEPLUSCONNECTED,  "white", "#404040");
        textCtl.MarkerDefine(stc.STC_MARKNUM_FOLDEROPENMID,
                          stc.STC_MARK_CIRCLEMINUSCONNECTED, "white", "#404040");
        textCtl.MarkerDefine(stc.STC_MARKNUM_FOLDERMIDTAIL,
                          stc.STC_MARK_TCORNERCURVE,         "white", "#404040");
        
        faces = None
        if wx.Platform == '__WXMSW__':
            faces = { 'times': 'Times New Roman',
                      'mono' : 'Courier New',
                      'helv' : 'Arial',
                      'other': 'Comic Sans MS',
                      'size' : 10,
                      'size2': 8,
                      }
        elif Utils.iAmOnLinux():
            faces = { 'times': 'Times',
                      'mono' : 'Courier',
                      'helv' : 'Helvetica',
                      'other': 'new century schoolbook',
                      'size' : 10,
                      'size2': 8,
                      }
        else:
            faces = { 'times': 'Times',
                      'mono' : 'Courier',
                      'helv' : 'Helvetica',
                      'other': 'new century schoolbook',
                      'size' : 12,
                      'size2': 10,
                      }

        textCtl.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        textCtl.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        textCtl.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        textCtl.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(mono)s,size:%(size2)d" % faces)
        textCtl.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(mono)s" % faces)
        textCtl.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        textCtl.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

        # C styles
        # Default 
        textCtl.StyleSetSpec(stc.STC_C_DEFAULT, "fore:#000000,face:%(mono)s,size:%(size)d" % faces)
        # Comments
        textCtl.StyleSetSpec(stc.STC_C_COMMENTLINE, "fore:#007F00,face:%(mono)s,size:%(size)d" % faces)
        # Number
        textCtl.StyleSetSpec(stc.STC_C_NUMBER, "fore:#007F7F,size:%(size)d" % faces)
        # String
        textCtl.StyleSetSpec(stc.STC_C_STRING, "fore:#7F007F,face:%(mono)s,size:%(size)d" % faces)
        # Single quoted string
        textCtl.StyleSetSpec(stc.STC_C_CHARACTER, "fore:#7F007F,face:%(mono)s,size:%(size)d" % faces)
        # Keyword
        textCtl.StyleSetSpec(stc.STC_C_WORD, "fore:#00007F,bold,size:%(size)d" % faces)
        # Keyword2
        textCtl.StyleSetSpec(stc.STC_C_WORD2, "fore:#007F00,size:%(size)d" % faces)
        # Operators
        textCtl.StyleSetSpec(stc.STC_C_OPERATOR, "bold,size:%(size)d" % faces)
        # Identifiers
        textCtl.StyleSetSpec(stc.STC_C_IDENTIFIER, "fore:#000000,face:%(mono)s,size:%(size)d" % faces)
        # Comment-blocks
        textCtl.StyleSetSpec(stc.STC_C_COMMENT, "fore:#7F7F7F,size:%(size)d" % faces)
        # End of line where string is not closed
        textCtl.StyleSetSpec(stc.STC_C_STRINGEOL,
                             "fore:#000000,face:%(mono)s,back:#E0C0E0,eol,size:%(size)d" % faces)

        # Line numbers in margin
        textCtl.StyleSetSpec(wx.stc.STC_STYLE_LINENUMBER,'fore:#000000,back:#99A9C2')
    
        # Highlighted brace
        textCtl.StyleSetSpec(wx.stc.STC_STYLE_BRACELIGHT,'fore:#00009D,back:#FFFF00')
        # Unmatched brace
        textCtl.StyleSetSpec(wx.stc.STC_STYLE_BRACEBAD,'fore:#00009D,back:#FF0000')
        # Indentation guide
        textCtl.StyleSetSpec(wx.stc.STC_STYLE_INDENTGUIDE, "fore:#CDCDCD")
            
        textCtl.SetCaretForeground("BLUE")
        textCtl.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        textCtl.SetMarginWidth(1, 25)

        textCtl.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        textCtl.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
        textCtl.UsePopUp(True)
        #self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)

        textCtl.SetSelBackground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))
        textCtl.SetSelForeground(True, wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

        return textCtl
    
    def OnUpdateUI(self, evt):
        editor = evt.GetEventObject()
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = editor.GetCurrentPos()

        if caretPos > 0:
            charBefore = editor.GetCharAt(caretPos - 1)
            styleBefore = editor.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == stc.STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = editor.GetCharAt(caretPos)
            styleAfter = editor.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == stc.STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = editor.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            editor.BraceBadLight(braceAtCaret)
        else:
            editor.BraceHighlight(braceAtCaret, braceOpposite)

    def OnMarginClick(self, evt):
        editor = evt.GetEventObject()
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll(editor)
            else:
                lineClicked = editor.LineFromPosition(evt.GetPosition())

                if editor.GetFoldLevel(lineClicked) & stc.STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        editor.SetFoldExpanded(lineClicked, True)
                        self.Expand(editor,lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if editor.GetFoldExpanded(lineClicked):
                            editor.SetFoldExpanded(lineClicked, False)
                            self.Expand(editor,lineClicked, False, True, 0)
                        else:
                            editor.SetFoldExpanded(lineClicked, True)
                            self.Expand(editor,lineClicked, True, True, 100)
                    else:
                        editor.ToggleFold(lineClicked)
                        
    def FoldAll(self,editor):
        lineCount = editor.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if editor.GetFoldLevel(lineNum) & stc.STC_FOLDLEVELHEADERFLAG:
                expanding = not editor.GetFoldExpanded(lineNum)
                break;

        lineNum = 0

        while lineNum < lineCount:
            level = editor.GetFoldLevel(lineNum)
            if level & stc.STC_FOLDLEVELHEADERFLAG and \
               (level & stc.STC_FOLDLEVELNUMBERMASK) == stc.STC_FOLDLEVELBASE:

                if expanding:
                    editor.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(editor,lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = editor.GetLastChild(lineNum, -1)
                    editor.SetFoldExpanded(lineNum, False)

                    if lastChild > lineNum:
                        editor.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1

    def Expand(self, editor, line, doExpand, force=False, visLevels=0, level=-1):
        lastChild = editor.GetLastChild(line, level)
        line = line + 1

        while line <= lastChild:
            if force:
                if visLevels > 0:
                    editor.ShowLines(line, line)
                else:
                    editor.HideLines(line, line)
            else:
                if doExpand:
                    editor.ShowLines(line, line)

            if level == -1:
                level = editor.GetFoldLevel(line)

            if level & stc.STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        editor.SetFoldExpanded(line, True)
                    else:
                        editor.SetFoldExpanded(line, False)

                    line = editor.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and editor.GetFoldExpanded(line):
                        line = editor.Expand(line, True, force, visLevels-1)
                    else:
                        line = editor.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1;

        return line

def run(args=None):
    global win
    win = None
    class MyApp(wx.App):
        def OnInit(self):
            global win
            Script.init_nwscript_keywords()
            frame = wx.Frame(None,-1,"Script Editor",
                             wx.DefaultPosition,wx.Size(600,400))
            win = ScriptEditor(frame,-1,True)
            win.SetFocus()
            self.SetTopWindow(frame)
            frame.Show(True)
            frame.SetSize((701,500))
            return True
    app = MyApp(0)
    if args:
        mod = Module.Module(args[0])
        win.setModule(mod)
    app.MainLoop()

def main():
    if len(os.path.dirname(sys.argv[0])) > 0:
        # mainly to find neveredit.jpg in mac os app bundle
        os.chdir(os.path.dirname(sys.argv[0]))
    run()
    
    
if __name__ == '__main__':
    main()
