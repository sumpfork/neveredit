
import wx
from neveredit.util import neverglobals



class HAKListControl(wx.BoxSizer) :
# This is a control with two ListBox-es. In one of them, avaible HAKs,
# and in the other, the HAKs that are "included" in the Module.
# One can put one hak from one of those ListBox-es to the other one using
# the |->| and |<-| buttons (arrow pixmaps and wxBitmapButton would be nicer)
# Then, one can set the HAK order in the Module using "up" and "down" buttons
# (the higher the HAK is in the ListBox, the higher is its priority).
# Finally, a TextCtrl allows to manually add a HAK (even if not in the
# filesystem) by typing it in and hitting enter.

# BUG : The selection/deselection does not work as wanted. Multiple selection
# just by clicking (no problem), but you can only deselect by holding Ctrl
# and clicking, at least on linux/gtk2.

# BUG : resizing the neveredit window will move everything alright, but the
# StaticText ant the TextCtrl will divide in two, with one part that follow
# the rest, and one that is stricly still, at least under linux/gtk2.

    def __init__(self, prop, propWindow) :
        wx.BoxSizer.__init__(self,wx.VERTICAL)
        self.prop = prop
        self.propWindow = propWindow

        exterior_sizer = wx.BoxSizer(wx.HORIZONTAL)
        arrows_sizer = wx.BoxSizer(wx.VERTICAL)
        updown_sizer = wx.BoxSizer(wx.VERTICAL)
        usedhaks_sizer = wx.BoxSizer(wx.VERTICAL)
        nonused_sizer = wx.BoxSizer(wx.VERTICAL)

        self.nonused_haks = wx.ListBox(propWindow, -1, size=(-1,100),\
                choices = [x for x in self.getAvaibleHAKs()\
                if x not in self.getUsedHAKs()],\
                style = wx.LB_MULTIPLE|wx.LB_NEEDED_SB|wx.LB_SORT)
        self.used_haks = wx.ListBox(propWindow, -1, size=(-1,100),\
                choices = self.getUsedHAKs(),
                style = wx.LB_MULTIPLE|wx.LB_NEEDED_SB)
        self.to_used = wx.Button(propWindow, -1, "->", style=wx.BU_EXACTFIT)
        self.to_nonused = wx.Button(propWindow, -1, "<-", style=wx.BU_EXACTFIT)
        self.up_button = wx.Button(propWindow, -1, _("  up  "), style=wx.BU_EXACTFIT)
        self.down_button = wx.Button(propWindow, -1, _("down"), style=wx.BU_EXACTFIT)
        self.text_edit = wx.TextCtrl(propWindow, -1, style = wx.TE_PROCESS_ENTER)

        self.label = wx.StaticText(propWindow,-1,'')
        self.Add(self.label, 0, wx.ALL, 5)

        arrows_sizer.Add(self.to_used)
        arrows_sizer.Add(self.to_nonused)

        updown_sizer.Add(self.up_button)
        updown_sizer.Add(self.down_button)

        usedhaks_sizer.Add(self.text_edit,flag=wx.EXPAND)
        usedhaks_sizer.Add(self.used_haks)
        nonused_sizer.Add(wx.StaticText(propWindow,-1,_('Avaible HAKs')),flag=wx.TOP)
        nonused_sizer.Add(self.nonused_haks,flag=wx.ALIGN_BOTTOM)

        exterior_sizer.Add(nonused_sizer,flag=wx.ALIGN_BOTTOM)
        exterior_sizer.Add(arrows_sizer,flag=wx.ALIGN_CENTER_VERTICAL)
        exterior_sizer.Add(usedhaks_sizer)
        exterior_sizer.Add(updown_sizer,flag=wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE)

        wx.EVT_BUTTON(propWindow, self.to_used.GetId(), self.HAKAdd)
        wx.EVT_BUTTON(propWindow, self.to_nonused.GetId(), self.HAKRemove)
        wx.EVT_BUTTON(propWindow, self.up_button.GetId(), self.HAKMoveUp)
        wx.EVT_BUTTON(propWindow, self.down_button.GetId(), self.HAKMoveDown)
        wx.EVT_TEXT_ENTER(propWindow, self.text_edit.GetId(), self.HAKManualAdd)

        self.Add(exterior_sizer)

    def Destroy(self) :
        self.label.Destroy()
        self.nonused_haks.Destroy()
        self.used_haks.Destroy()
        self.up_button.Destroy()
        self.down_button.Destroy()
        self.to_used.Destroy()
        self.to_nonused.Destroy()
        # should I also destroy th wx.Sizer-s?
        wx.BoxSizer.Destroy(self)

    def getAvaibleHAKs(self) :
        return [x.split('.')[0].lower() for x in\
            neverglobals.getResourceManager().getHAKFileNames()]

    def getUsedHAKs(self) :
        return [x['Mod_Hak'].lower()for x in self.prop.getValue()]

    def GetStringSelections(self):
        count = self.used_haks.GetCount()
        haknames = map(self.used_haks.GetString,range(0,count))
        return haknames

    def GetRejectedStrings(self):
        count = self.nonused_haks.GetCount()
        rejects = map(self.nonused_haks.GetString,range(0,count))
        return rejects

    def GetId(self) :
        return self.used_haks.GetId()

    def HAKAdd(self, event):
        indexes = self.nonused_haks.GetSelections()
        selections = map(self.nonused_haks.GetString, indexes)
        if len(selections)!=0:

            event.SetId(self.GetId())
            self.propWindow.controlUsed(event)

            map(self.used_haks.Append,selections)
            for s in selections:
                i = self.nonused_haks.FindString(s)
                self.nonused_haks.Delete(i)

    def HAKRemove(self, event):
        indexes = self.used_haks.GetSelections()
        selections = map(self.used_haks.GetString, indexes)
        if len(selections)!=0:

            event.SetId(self.GetId())
            self.propWindow.controlUsed(event)

            map(self.nonused_haks.Append,selections)
            for s in selections:
                i = self.used_haks.FindString(s)
                self.used_haks.Delete(i)

    def HAKMoveUp(self, event) :
        n_haks = self.used_haks.GetSelections()
        if len(n_haks)==1 :		# for multiple choices, that can make strange behavior!

            event.SetId(self.GetId())
            self.propWindow.controlUsed(event)

            for i in n_haks:
                if i>0 :
                    moved_name = self.used_haks.GetString(i)
                    self.used_haks.Delete(i)
                    self.used_haks.Insert(moved_name,i-1)
                    self.used_haks.SetSelection(i-1)

        elif len(n_haks)>1 :
            self.warnMoveHAKsOneByOne(frame)


    def HAKMoveDown(self, event) :
        n_haks = self.used_haks.GetSelections()
        if len(n_haks)==1 :		    # for multiple choices, that can make strange behavior!

            event.SetId(self.GetId())
            self.propWindow.controlUsed(event)

            for i in n_haks:
                if i+1<self.used_haks.GetCount():
                    moved_name = self.used_haks.GetString(i)
                    self.used_haks.Delete(i)
                    self.used_haks.Insert(moved_name,i+1)
                    self.used_haks.SetSelection(i+1)

        elif len(n_haks)>1 :
            self.warnMoveHAKsOneByOne(self.parent)

    def warnMoveHAKsOneByOne(parent) :
        # use whatever to warn the user to move the haks one by one
        pass

    def HAKManualAdd(self, event) :
        hakname = self.text_edit.GetValue()
        if len(hakname)!=0 :
            selected = self.GetStringSelections()
            if hakname not in selected:

                event.SetId(self.GetId())
                self.propWindow.controlUsed(event)

                self.used_haks.Append(hakname)
                avaible = self.GetRejectedStrings()
                if hakname in avaible:
                    index = self.nonused_haks.FindString(hakname)
                    self.nonused_haks.Delete(index)

