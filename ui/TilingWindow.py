"""A GUI control to lay an area's tiles"""
import logging
logger = logging.getLogger('neveredit.ui')
import sets

import wx
import wx.lib.ogl as ogl
import wx.lib.mixins.listctrl  as  listmix
import Image

from neveredit.ui import WxUtils
from neveredit.game.Tile import Tile
from neveredit.util import Utils
from neveredit.util import neverglobals
from neveredit.ui.ModelWindow import ModelWindow

class TileShape(ogl.BitmapShape):
    def __init__(self,t,tilesize=32):
        ogl.BitmapShape.__init__(self)
        self.tilesize=tilesize
        self.tile = t
        tile = t.get2DTile()
        if not tile:
            logger.warning('no 2D tile for' + `tile`)
        else:
            tile = Utils.resizeSquareImage(tile,self.tilesize)
            tile = tile.rotate(t.getBearing())
            self.SetBitmap(WxUtils.bitmapFromImage(tile))
            self.SetFixedSize(self.tilesize,self.tilesize)

    def getTile(self):
        return self.tile
    
class ShapeEventHandler(ogl.ShapeEvtHandler):
    def __init__(self,parent):
        ogl.ShapeEvtHandler.__init__(self)
        self.parent = parent

    def OnLeftClick(self,x,y,keys=0,attachment=0):
        shape = self.GetShape()
        canvas = shape.GetCanvas()
        dc = wx.ClientDC(canvas)
        canvas.PrepareDC(dc)

        shapes = canvas.GetDiagram().GetShapeList()
        toUnselect = []
        for s in shapes:
            if s.Selected():
                # If we unselect it now then some of the objects in
                # shapeList will become invalid (the control points are
                # shapes too!) and bad things will happen...
                toUnselect.append(s)


            if toUnselect:
                for s in toUnselect:
                    s.Select(False, dc)
        shape.Select(True, dc)
        canvas.Redraw(dc)
        print 'orientation:',self.GetShape().getTile().getBearing()
        for c in Tile.CORNERS:
            print c,self.GetShape().getTile().getCornerType(c)
        for c in Tile.SIDES:
            print c,self.GetShape().getTile().getSideType(c)
        self.parent.selected(shape)
        
class TileListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        
class TilingWindow(wx.Panel):
    __doc__=globals()['__doc__']
    oglInitialized = False
    def __init__(self,parent,tilesize=32):
        wx.Panel.__init__(self,parent,-1)        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        if not TilingWindow.oglInitialized:
            ogl.OGLInitialize()
            TilingWindow.oglInitialized=True
        self.tileset = None
        self.mapWindow = ogl.ShapeCanvas(self,-1,(400,400))
        self.sizer.Add(self.mapWindow,True,wx.EXPAND)
        self.map = ogl.Diagram()
        self.map.SetCanvas(self.mapWindow)
        self.mapWindow.SetDiagram(self.map)
        self.area = None
        self.tilelist = None
        self.mapWindow.SetBackgroundColour("LIGHT BLUE")

        self.map.SetGridSpacing(tilesize)
        self.map.SetSnapToGrid(True)
        
        self.map.ShowAll(True)
        self.vertSizer = wx.BoxSizer(wx.VERTICAL)
        self.tileListCtrl = wx.ListCtrl(self,
                                        style=wx.LC_REPORT|wx.LC_NO_HEADER|wx.LC_SINGLE_SEL)
        self.vertSizer.Add(self.tileListCtrl,True,wx.EXPAND)
        self.modelWindow = ModelWindow(self)
        self.modelWindow.SetSize((150,150))
        self.vertSizer.Add(self.modelWindow,False,wx.ALIGN_RIGHT|wx.ALIGN_BOTTOM)
        self.sizer.Add(self.vertSizer,False,wx.EXPAND)
        
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)

        self.Layout()
        self.Update()
        
        self.tilesize = tilesize
        self.tileshapes = []
        self.tileImageList = wx.ImageList(self.tilesize,self.tilesize)
        self.tileImageMap = {}
        self.tilelist = []

    def setArea(self,area):
        self.area = area
        self.tileshapes = []
        self.area.readTiles()
        self.tilelist = self.area.getTiles()
        for i,t in enumerate(self.tilelist):
            x = i % self.area.getWidth()
            y = i / self.area.getWidth()
            s = TileShape(t,self.tilesize)
            s.SetCanvas(self.mapWindow)
            s.SetX(x*self.tilesize+self.tilesize/2)
            height = self.area.getHeight()*self.tilesize
            s.SetY(height-y*self.tilesize+self.tilesize/2)
            handler = ShapeEventHandler(self)
            handler.SetShape(s)
            handler.SetPreviousHandler(s.GetEventHandler())
            s.SetEventHandler(handler)
            self.map.AddShape(s)
            s.Show(True)
            self.tileshapes.append(s)
            
        self.mapWindow.SetScrollbars(20, 20,
                                     (self.area.getWidth()*self.tilesize)/20,
                                     (self.area.getHeight()*self.tilesize)/20)

        tiles = self.area.getTileSet().getStandardTiles()
        for t in tiles:
            imageName = t.get2DImageName()
            if not imageName in self.tileImageMap:
                twodtile = t.get2DTile()
                if twodtile:
                    twodtile = Utils.resizeSquareImage(twodtile,self.tilesize)
                    index = self.tileImageList.Add(WxUtils.bitmapFromImage(twodtile))
                    self.tileImageMap[imageName + '.0'] = index
                    for angle in [90,180,270]:
                        twodtileRotated = twodtile.rotate(angle)
                        index = self.tileImageList.Add(WxUtils.bitmapFromImage(twodtileRotated))
                        self.tileImageMap[imageName + '.' + `angle`] = index
        self.tileListCtrl.ClearAll()
        self.tileListCtrl.SetImageList(self.tileImageList,wx.IMAGE_LIST_NORMAL)
        self.tileListCtrl.SetImageList(self.tileImageList,wx.IMAGE_LIST_SMALL)

        self.Layout()
        self.Update()
        
    def updateTileListCtrl(self,tiles):
        self.tileListCtrl.ClearAll()
        self.tileListCtrl.InsertColumn(0,"Tiles")
        for t in tiles:
            #print 'adding tile',t.getId(),t.getBearing()
            self.tileListCtrl.InsertImageStringItem(self.tileListCtrl.GetItemCount(),
                                                    t.getName(),
                                                    self.tileImageMap[t.get2DImageName()
                                                                      + '.'
                                                                      + `int(t.getBearing())`])
        
    def selected(self,shape):
        self.modelWindow.setModel(shape.getTile().getModel())
        self.modelWindow.Refresh(True)
        x = shape.GetX() / self.tilesize
        y = self.area.getHeight() - (shape.GetY() / self.tilesize)
        #print 'shape',shape.getTile().getId(),'at',x,y
        alltiles = self.area.getTileSet().getStandardTiles()
        goodtiles = {}
        for xdiff in (-1,0,1):
            for ydiff in (-1,0,1):
                if not xdiff and not ydiff:
                    continue
                placedX = x+xdiff
                placedY = y+ydiff
                if placedX < 0 or placedX >= self.area.getWidth() or\
                   placedY < 0 or placedY >= self.area.getHeight():
                    continue
                placed = self.area.getTile(placedX,placedY)
                #print 'relative:',placedX,placedY,
                direction = ''
                if ydiff == -1:
                    direction = 'Top'
                elif ydiff == 1:
                    direction = 'Bottom'
                if xdiff == -1:
                    direction += 'Right'
                elif xdiff == 1:
                    direction += 'Left'
                #print direction,placed.getType(direction)
                for t in alltiles:
                    for angle in [0,90,180,270]:
                        rotTile = self.area.getTileSet().makeNewTile(t.getId())
                        rotTile.rotate(angle)
                        tilekey = `rotTile.getId()` + '.' + `angle`
                        if xdiff == ydiff == -1:
                            if rotTile.canPlaceRelativeTo(placed,direction):
                                goodtiles[tilekey] = rotTile
                        else:
                            if not rotTile.canPlaceRelativeTo(placed,direction) and\
                                   tilekey in goodtiles:
                                del goodtiles[tilekey]
        self.updateTileListCtrl(goodtiles.values())
                
                
def run(args):
    import neveredit.util.Loggers
    class MyApp(wx.App):
        def __init__(self,i,a):
            self.area = a
            wx.App.__init__(self,i)
            
        def OnInit(self):
            f = wx.Frame(None,-1,'Tiling Map')
            win = TilingWindow(f)
            win.setArea(self.area)
            f.Show(True)
            return True
    from neveredit.game.Module import Module
    m = Module(args[0])
    a = m.getEntryArea()
    app = MyApp(0,a)
    
    app.MainLoop()
    
if __name__ == '__main__':
    import sys
    run(sys.argv)
