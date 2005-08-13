"""A set of GUI classes showing blueprint palettes and a toolbar"""
import string

import wx

from neveredit.game.Palette import Palette
from neveredit.ui import WxUtils

class PaletteWindow(wx.TreeCtrl):
    """A tree control representing a blueprint palette."""
    def __init__(self,parent,id):
        wx.TreeCtrl.__init__(self,parent,id,
                             style=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)
        self.AddRoot("Blueprint Palette")        
        self.palette = None
        self.imagelist = wx.ImageList(16,26)
        self.SetImageList(self.imagelist)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING,self.itemExpanding)
        self.Bind(wx.EVT_TREE_SEL_CHANGING,self.selectionChanging)
        self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP,self.supplyToolTip)
        
    def fromPalette(self,palette):
        self.fromPaletteHelper(self.GetRootItem(),palette.getRoots())
        self.palette = palette
        
    def fromPaletteHelper(self,parentNode,childSpecs):
        for r in childSpecs:
            r.childrenReady = False
            node = self.AppendItem(parentNode,r.getName())
            self.SetPyData(node,r)
            image = r.getImage()
            if image:
                image = image.crop((0,0,16,26))
                index = self.imagelist.Add(WxUtils.bitmapFromImage(image))
                self.SetItemImage(node,index)
            if r.getChildren():
                self.SetItemHasChildren(node,True)

    def itemExpanding(self,event):
        item = event.GetItem()
        data = self.GetPyData(item)
        if data and not data.childrenReady:
            self.fromPaletteHelper(item,data.getChildren())
            data.childrenReady = True

    def selectionChanging(self,event):
        if event.GetItem().IsOk() and\
           self.GetPyData(event.GetItem()) and\
           not self.GetPyData(event.GetItem()).getBlueprint():
            event.Veto()
            
    def supplyToolTip(self,event):
        if event.GetItem().IsOk() and\
           self.GetPyData(event.GetItem()):
            bp = self.GetPyData(event.GetItem()).getBlueprint()
            if bp:                
                event.SetToolTip(bp.getDescription())
    
    def get_standalone(cls, pname=None):
        class MyApp(wx.App):
            def OnInit(self):
                #if not pname:
                pname = 'creaturepalstd.itp'
                frame = wx.MiniFrame(None, -1, "Palette",
                                     wx.DefaultPosition, wx.Size(200,400))
                self.win = PaletteWindow(frame,-1)
                self.win.fromPalette(Palette.getStandardPalette('Creature'))
                frame.Show(True)
                self.SetTopWindow(frame)
                return True
        cls.app = MyApp(0)
        return cls.app.win
    get_standalone = classmethod(get_standalone)

    def start_standalone(cls):
        cls.app.MainLoop()
    start_standalone = classmethod(start_standalone)

TOOLSELECTIONEVENT = wx.NewEventType()

def EVT_TOOLSELECTION(window,function):
    '''notifies about the selection of a tool in the palette'''
    window.Connect(-1,-1,TOOLSELECTIONEVENT,function)

class ToolSelectionEvent(wx.PyCommandEvent):
    eventType = TOOLSELECTIONEVENT
    def __init__(self,windowID,tooltype):
        wx.PyCommandEvent.__init__(self,self.eventType,windowID)
        self.tooltype = tooltype
        self.data = None

    def setData(self,data):
        self.data = data

    def getData(self):
        return self.data
    
    def getToolType(self):
        return self.tooltype
    
    def Clone(self):
        self.__class__(self.GetId(),self.tooltype)

SELECTION_TOOL = wx.NewId()
ROTATE_TOOL = wx.NewId()
PAINT_TOOL = wx.NewId()

class ToolFrame(wx.MiniFrame):
    def __init__(self):
        import Image,WxUtils
        wx.MiniFrame.__init__(self,None,-1,"Tools",(800,50),(300,600))
        self.SetBackgroundColour('WHITE')
        self.CreateStatusBar()
        self.toolbar = self.CreateToolBar()
        self.toolbar.SetBackgroundColour(wx.WHITE)
        self.selectId = SELECTION_TOOL
        self.toolbar.AddCheckTool(self.selectId,
                                  wx.Bitmap('select_icon.png'),
                                  wx.Bitmap('select_icon_sel.png'),
                                  shortHelp=('Select Object'),
                             longHelp='Select and Move objects on Map')
        self.paintId = PAINT_TOOL        
        self.toolbar.AddCheckTool(self.paintId,
                                  wx.Bitmap('paint_icon.png'),
                                  wx.Bitmap('paint_icon_sel.png'),
                                  shortHelp='Paint Objects',
                                  longHelp='Paint selected objects onto Map Display')
        self.rotateId = ROTATE_TOOL        
        self.toolbar.AddCheckTool(self.rotateId,
                                  wx.Bitmap('rotate_icon.png'),
                                  wx.Bitmap('rotate_icon_sel.png'),
                                  shortHelp=('Rotate Object'),
                                  longHelp=('Rotate object shown on Map'))
        self.Bind(wx.EVT_TOOL,self.toolSelected)
        self.toolbar.AddSeparator()
        self.toolbar.Realize()
        self.toolIds = [self.selectId,self.paintId,self.rotateId]

        sublist = [ptype for ptype in Palette.PALETTE_TYPES
                   if ptype not in ['Sound','Encounter','Waypoint',
                                    'Trigger','Store','Item']]
        self.stdPalettes = dict(zip(sublist,
                                    [Palette.getStandardPalette(ptype)
                                     for ptype in sublist]))
        self.notebook = wx.Notebook(self,-1,style=wx.NB_LEFT)
        for type,palette in self.stdPalettes.iteritems():
            pw = PaletteWindow(self.notebook,-1)
            pw.fromPalette(palette)
            self.notebook.AddPage(pw,type)
            pw.Bind(wx.EVT_TREE_SEL_CHANGED,self.treeItemSelected)

        self.toggleToolOn(self.selectId)
        self.lastPaletteSelection = None
        
    def getActivePaletteWindow(self):
        return self.notebook.GetPage(self.notebook.GetSelection())
    
    def toggleToolOn(self,id):
        for tid in self.toolIds:
            self.toolbar.ToggleTool(tid,tid==id)
        newEvent = ToolSelectionEvent(self.GetId(),id)
        if id != self.paintId:
            self.lastPaletteSelection = self.getActivePaletteWindow().GetSelection()
            self.getActivePaletteWindow().Unselect()
        else:
            if self.lastPaletteSelection:
                self.getActivePaletteWindow().SelectItem(self.lastPaletteSelection)
                self.lastPaletteSelection = None
            bp = self.getSelectedBlueprint()
            if bp:
                newEvent.setData(bp.toInstance())
        self.GetEventHandler().AddPendingEvent(newEvent)        
            
    def treeItemSelected(self,event):
        if self.getActivePaletteWindow().GetPyData(event.GetItem()):
            self.toggleToolOn(self.paintId)
        event.Skip()

    def getSelectedBlueprint(self):
        palette = self.getActivePaletteWindow()
        data = palette.GetPyData(palette.GetSelection())
        if data:
            return data.getBlueprint()
        
    def toolSelected(self,event):
        self.toggleToolOn(event.GetId())
        event.Skip()

if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            wx.InitAllImageHandlers()            
            f = ToolFrame()
            f.Show(True)
            self.SetTopWindow(f)
            return True
    app = MyApp(0)
    app.MainLoop()
    
            
