import logging
logger = logging.getLogger("neveredit")
import ConfigParser,cStringIO
from sets import Set

from neveredit.util import neverglobals
from neveredit.game.Tile import Tile

class TileSetFile(ConfigParser.ConfigParser):
    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)
        self.groupTiles = None
        self.tiles = None
        
    def fromFile(self,f):        
        self.readfp(f)

    def getTileCount(self):
        return self.getint('TILES','Count')

    def getGroupCount(self):
        return self.getint('GROUPS','Count')

    def getAllGroupTileIDs(self):
        if self.groupTiles:
            return self.groupTiles
        self.groupTiles = Set()
        for i in range(self.getGroupCount()):
            self.groupTiles.update(self.getGroupTileIDs(i))
        return self.groupTiles

    def isTileInGroup(self,tile):
        tiles = self.getAllGroupTileIDs()
        return tile.getId() in tiles
    
    def getGroupTileIDs(self,group):
        tiles = []
        gname = 'GROUP' + `group`
        rows = self.getint(gname,'Rows')
        cols = self.getint(gname,'Columns')
        for i in range(rows*cols):
            tiles.append(self.getint(gname,'Tile'+`i`))
        return tiles

    def getStandardTiles(self):
        if not self.tiles:
            self.tiles = [self.makeNewTile(i)
                          for i in range(self.getTileCount())
                          if i not in self.getAllGroupTileIDs()]
        return self.tiles
    
    def makeNewTile(self,tid):
        t = Tile(tid=tid,tileset=self)
        return t
    
    def getTileInfo(self,tid):
        return self.items('TILE'+`tid`)
    
    def __getitem__(self,key):
        section,entry = key.split('.')
        return self.get(section,entry)
    
    def __str__(self):
        io = cStringIO.StringIO
        self.write(io)
        return io.value()

    def __repr__(self):
        return self.__str__()
    
if __name__ == '__main__':
    import neveredit.util.Loggers
    import sys
    t = TileSetFile()
    t.fromFile(open(sys.argv[1]))
    for i in t.items('GENERAL'):
        print i
        
