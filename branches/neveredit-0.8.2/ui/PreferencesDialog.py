"""The neveredit preferences dialog."""

import wx,wx.xrc
from wx.lib.filebrowsebutton import DirBrowseButton

from neveredit.resources.xrc import PreferencesDialog_xrc

import neveredit.util.Preferences
import neveredit.file.Language
import sys

class PreferencesDialog(wx.Dialog):
    __doc__ = globals()['__doc__']
    def __init__(self,parent,prefs=None,tablist=None):

                
        if not prefs:
            prefs = neveredit.util.Preferences.getPreferences()
        self.preferences = prefs
        if not tablist:
            tablist = ["GeneralPanel","ScriptEditorPanel","TextPanel", "UserControlsPanel"]
            # tablist list all tabs that will be activated, the other ones do
            # not show
        self.tablist = tablist
        resourceText = PreferencesDialog_xrc.data
        resource = wx.xrc.EmptyXmlResource()
        resource.LoadFromString(resourceText)

        dialog = resource.LoadDialog(parent,"PrefDialog")
        notebook = wx.xrc.XRCCTRL(dialog,"PrefNotebook")
        
        generalPanel = wx.xrc.XRCCTRL(dialog,"GeneralPanel")
        if "GeneralPanel" in self.tablist:
            self.appDirButton = DirBrowseButton(generalPanel,-1,(500,30),
                                                labelText=_('NWN Directory'),
                                                buttonText=_('Select...'),
                                                startDirectory=
                                                prefs['NWNAppDir'])
            self.appDirButton.SetValue(prefs['NWNAppDir'])            
            resource.AttachUnknownControl('AppDir',
                                          self.appDirButton,
                                          generalPanel)
        else:
            index = self.__getPanelIndex(notebook,generalPanel)
            notebook.DeletePage(index)
        if "ScriptEditorPanel" in self.tablist:
            self.scriptAntiAlias = wx.xrc.XRCCTRL(dialog,"ScriptAntiAlias")
            self.scriptAntiAlias.SetValue(prefs['ScriptAntiAlias'])
            self.scriptAutoCompile = wx.xrc.XRCCTRL(dialog,"ScriptAutoCompile")
            self.scriptAutoCompile.SetValue(prefs['ScriptAutoCompile'])
        else:
            index = self.__getPanelIndex(notebook,
                                         wx.xrc.XRCCTRL(dialog,
                                                        "ScriptEditorPanel"))
            notebook.DeletePage(index)
        if "TextPanel" in self.tablist :
                self.DefaultLocStringLang = wx.xrc.XRCCTRL(
                                        dialog,"DefaultLocStringLang")
                self.DefaultLocStringLang.SetSelection(neveredit.file.Language.\
                        convertFromBIOCode(prefs["DefaultLocStringLang"]))
        else:
                index = self.__getPanelIndex(notebook,
                                         wx.xrc.XRCCTRL(dialog, "TextPanel"))
                notebook.DeletePage(index)

        # Set up the User Controls Panel
        # Create Controls
        # Fix length 
        # Set value
        if "UserControlsPanel" in self.tablist :
                self.mwUpKey = wx.xrc.XRCCTRL(dialog,"mwUpKey")
                self.mwUpKey.SetMaxLength(1)
                self.mwUpKey.SetValue(prefs['GLW_UP'])
                self.mwDownKey = wx.xrc.XRCCTRL(dialog,"mwDownKey")
                self.mwDownKey.SetMaxLength(1)
                self.mwDownKey.SetValue(prefs['GLW_DOWN'])
                self.mwLeftKey = wx.xrc.XRCCTRL(dialog,"mwLeftKey")
                self.mwLeftKey.SetMaxLength(1)
                self.mwLeftKey.SetValue(prefs['GLW_LEFT'])
                self.mwRightKey = wx.xrc.XRCCTRL(dialog,"mwRightKey")
                self.mwRightKey.SetMaxLength(1)
                self.mwRightKey.SetValue(prefs['GLW_RIGHT'])
                
        else:
                index = self.__getPanelIndex(notebook,
                                         wx.xrc.XRCCTRL(dialog, "UserControlsPanel"))
                notebook.DeletePage(index)

        dialog.Bind(wx.EVT_BUTTON, self.OnOk, id=wx.xrc.XRCID("ID_OK"))
        dialog.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.xrc.XRCID("ID_CANCEL"))
        self.PostCreate(dialog)

    def __getPanelIndex(self,notebook,panel):
        index = [notebook.GetPage(i).GetId() for i in
                 range(notebook.GetPageCount())]\
                 .index(panel.GetId())
        return index
                
    def getValues(self):
        values = {}
        if "GeneralPanel" in self.tablist:
            values.update({'NWNAppDir':self.appDirButton.GetValue()})
        if "ScriptEditorPanel" in self.tablist:
            values.update({'ScriptAntiAlias':
                           self.scriptAntiAlias.GetValue(),
                           'ScriptAutoCompile':
                           self.scriptAutoCompile.GetValue()})
        if "TextPanel" in self.tablist:
            values.update({"DefaultLocStringLang":neveredit.file.Language.\
                           convertToBIOCode(self.DefaultLocStringLang.GetSelection())})
            
        # Update value of direction keys for Model/GLWindow
        if "UserControlsPanel" in self.tablist:
            values.update({'GLW_UP': self.mwUpKey.GetValue(),
                           'GLW_DOWN': self.mwDownKey.GetValue(),
                           'GLW_LEFT': self.mwLeftKey.GetValue(),
                           'GLW_RIGHT': self.mwRightKey.GetValue()})
        return values

    def ShowAndInterpret(self):
        self.CentreOnParent()
        if self.ShowModal() == wx.ID_OK:
            result = self.getValues()
            self.preferences.values.update(result)
            self.preferences.save()
            return True
        else:
            return False

    def OnCancel(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnOk(self, event):
        self.EndModal(wx.ID_OK)

    

if __name__ == '__main__':
    import gettext,sys
    from neveredit.util.Preferences import Preferences
    gettext.install('neveredit','translations')
    sys.path.insert(0,'..')
    class MyApp(wx.App):
        def OnInit(self):
            d = PreferencesDialog(None)
            d.ShowAndInterpret()
            return True
    app = MyApp(0)
    
    app.MainLoop()
