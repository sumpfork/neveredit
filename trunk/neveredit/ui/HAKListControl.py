
import wx
from neveredit.util import neverglobals



class HAKListControl(wx.BoxSizer) :
# This is a control with two ListBox-es. In one of them, avaible HAKs,
# and in the other, the HAKs that are "included" in the Module.
# One can put one hak from one of those ListBox-es to the other one using
# the |->| and |<-| buttons (arrow pixmaps and wxBitmapButton would be nicer)
# Then, one can set the HAK order in the Module using "up" and "down" buttons
# (the higher the HAK is in the ListBox, the higher is its priority).


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
                style = wx.LB_SINGLE|wx.LB_NEEDED_SB|wx.LB_SORT)
                # The selection mode is "wx.LB_SINGLE" for the moment
                # because I couldn't have the good behaviour with wx.LB_EXTENDED
                # I'm not sure it won't we kept that way
        self.used_haks = wx.ListBox(propWindow, -1, size=(-1,100),\
                choices = self.getUsedHAKs(),
                style = wx.LB_SINGLE|wx.LB_NEEDED_SB)
        self.to_used = wx.Button(propWindow, -1, "->")
        self.to_nonused = wx.Button(propWindow, -1, "<-")
        self.up_button = wx.Button(propWindow, -1, _("move up"))
        self.down_button = wx.Button(propWindow, -1, _("move down"))

        self.unused_label = wx.StaticText(propWindow,-1,_('Avaible HAKs'))
        self.used_label = wx.StaticText(propWindow,-1,_('Selected HAKs'))

        arrows_sizer.Add(self.to_used, 0, wx.EXPAND)
        arrows_sizer.Add(self.to_nonused, 0, wx.EXPAND)
        arrows_sizer.Add(self.up_button, 0, wx.EXPAND)
        arrows_sizer.Add(self.down_button, 0, wx.EXPAND)

        usedhaks_sizer.Add(self.used_label,flag=wx.TOP)
        usedhaks_sizer.Add(self.used_haks)

        nonused_sizer.Add(self.unused_label,flag=wx.TOP)
        nonused_sizer.Add(self.nonused_haks,flag=wx.ALIGN_BOTTOM)

        exterior_sizer.Add(nonused_sizer,flag=wx.ALIGN_BOTTOM)
        exterior_sizer.Add(arrows_sizer,flag=wx.ALIGN_CENTER_VERTICAL)
        exterior_sizer.Add(usedhaks_sizer)
        exterior_sizer.Add(updown_sizer,flag=wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE)

        wx.EVT_BUTTON(propWindow, self.to_used.GetId(), self.HAKAdd)
        wx.EVT_BUTTON(propWindow, self.to_nonused.GetId(), self.HAKRemove)
        wx.EVT_BUTTON(propWindow, self.up_button.GetId(), self.HAKMoveUp)
        wx.EVT_BUTTON(propWindow, self.down_button.GetId(), self.HAKMoveDown)

        self.Add(exterior_sizer)

    def Destroy(self) :
        self.nonused_haks.Destroy()
        self.used_haks.Destroy()
        self.up_button.Destroy()
        self.down_button.Destroy()
        self.to_used.Destroy()
        self.to_nonused.Destroy()
        self.used_label.Destroy()
        self.unused_label.Destroy()
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
        if len(n_haks)==1 :             # for multiple choices, that can make strange behavior!

            event.SetId(self.GetId())
            self.propWindow.controlUsed(event)

            for i in n_haks:
                if i>0 :
                    moved_name = self.used_haks.GetString(i)
                    self.used_haks.Delete(i)
                    self.used_haks.Insert(moved_name,i-1)
                    self.used_haks.SetSelection(i-1)

        elif len(n_haks)>1 :
            self.warnMoveHAKsOneByOne(self.parent)


    def HAKMoveDown(self, event) :
        n_haks = self.used_haks.GetSelections()
        if len(n_haks)==1 :                 # for multiple choices, that can make strange behavior!

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

