import wx,wx.grid
from wx.grid import Grid
from neveredit.file.GFFFile import GFFStruct
from neveredit.game.Factions import ReputStruct
from neveredit.game.ChangeNotification import PropertyChangeNotifier


class FactionGridWindow(wx.Panel,PropertyChangeNotifier):
    def __init__(self,parent,data,mainWindow):
        wx.Panel.__init__(self,parent,-1)
        PropertyChangeNotifier.__init__(self)
        self.mainWindow = mainWindow

        self.addPropertyChangeListener(self.mainWindow)

        self.addBtn = wx.Button(self,-1,_('Add Faction'),name='Faction_addButton')
        self.delBtn = wx.Button(self,-1,_('Delete Faction'),name='Faction_delButton')
        self.choice = wx.TextCtrl(self,-1)
        up_sizer = wx.BoxSizer(wx.HORIZONTAL)
        up_sizer.Add(self.addBtn,flag=wx.ALL,border=3)
        up_sizer.Add(self.delBtn,flag=wx.ALL,border=3)
        up_sizer.Add(self.choice,flag=wx.ALL,border=3)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(up_sizer,flag=wx.ALL,border=3)
        main_sizer.Add(wx.StaticText(self,-1,_('''
            To add a faction, type the faction name in the text control and press "Add Faction".
            No new faction will be created if there is already a faction with this name.
            To remove a faction, enter the faction name in the text control and press "Delete Faction".

            Change the Faction reactions in the grid below. The number in column x row y gives
            the reaction of x faction towards y faction.
            Reactions of PC faction towards other factions are not required.
            ''')),flag=wx.ALL,border=3)

        self.grid = FactionGrid(self,data)
        main_sizer.Add(self.grid,flag=wx.ALL|wx.EXPAND,border=3)
        self.SetSizer(main_sizer)

        wx.EVT_BUTTON(self,self.addBtn.GetId(),self.addFaction)
        wx.EVT_BUTTON(self,self.delBtn.GetId(),self.delFaction)

        # while this is not done
        self.delBtn.Disable()

    def addFaction(self,event):
        name = self.choice.GetValue()
        factions = map(lambda x:x.getName(),self.grid.FactionObject.factionList)
        if name not in factions:
            self.grid.FactionObject.addFaction(name)
            # simulate a tree selection change to redraw the faction window
            self.propertyChanged(self.addBtn,self.grid.FactionObject.factionList[-1])

    def delFaction(self,event):
        name = self.Choice.GetValue()
        factions = map(lambda x:x.getName(),self.FactionObject.factionList)
        if name in factions:
            pass

    def applyPropControlValues(self,data):
        self.grid.applyPropControlValues(data)

class FactionGrid(Grid):

    def __init__(self,parent,data):
        Grid.__init__(self,parent,-1)
        self.parent = parent
        self.FactionObject = data
        self.factionNumber = len(self.FactionObject.factionList)
        self.hasChanged = False
        self.CreateGrid()

    def cellChanged(self,event):
        self.hasChanged = True

    def cellSelected(self,event):
        if self.hasChanged:
            self.parent.propertyChanged(self,self.FactionObject)
        event.Skip()

    def CreateGrid(self):
        Grid.CreateGrid(self,self.factionNumber,self.factionNumber)
        self.SetDefaultEditor(wx.grid.GridCellNumberEditor(0,100))
        self.SetDefaultRenderer(wx.grid.GridCellNumberRenderer())
        self.SetDefaultColSize(50)
        self.setLabels()
        self.setDataCells()
        wx.grid.EVT_GRID_CELL_CHANGE(self,self.cellChanged)
        wx.grid.EVT_GRID_SELECT_CELL(self,self.cellSelected)

    def setLabels(self):
        for x in range(self.factionNumber):
            name = self.FactionObject.factionList[x].getName()
            self.SetColLabelValue(x,name)
            self.SetRowLabelValue(x,name)

    def setDataCells(self):
        for x in range(0,self.factionNumber):
            for y in range(0,self.factionNumber):
                self.SetCellValue(x,y,str(self.FactionObject.getReputationValue(x,y)))
                # yes, the rows and cols are right here

    def GetData(self):
        # will return a 'RepList' compatible GFFStruct
        replist = []
        for x in range(self.factionNumber):
            for y in range(self.factionNumber):
                value = self.GetCellValue(x,y)
                if value != 'None':
                    s = GFFStruct()
                    s.add('FactionID1',x,'INT')
                    s.add('FactionID2',y,'INT')
                    try:
                        s.add('FactionRep',int(value),'INT')
                    except ValueError:
                        pass
                        # this could lead to not complete enough struct in some (not rare!) cases
                        # but i can't see how that could happen here
                    replist.append(ReputStruct(s))
        return replist

    def applyPropControlValues(self,data):
        if not self.hasChanged:
            return False
        data.setProperty('FactionList',[x.getGFFStruct('factStruct') for x in\
                                                     self.FactionObject.factionList])
        data.setProperty('RepList',[x.getGFFStruct('repStruct') for x in self.GetData()])
        self.FactionObject.hasChanged()

